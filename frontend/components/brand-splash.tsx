"use client";

import Image from "next/image";
import { useEffect, useRef, useState } from "react";

const splashSessionKey = "qhi-auto:cinematic-splash:v2";
const splashDuration = 4_950;

type Renderer = "pending" | "webgl" | "canvas" | "static";

const vertexShader = `
attribute vec2 a_position;
varying vec2 v_uv;
void main() {
  v_uv = (a_position + 1.0) * 0.5;
  gl_Position = vec4(a_position, 0.0, 1.0);
}`;

const fragmentShader = `
precision mediump float;
varying vec2 v_uv;
uniform sampler2D u_image;
uniform float u_time;
uniform float u_progress;
uniform float u_energy;
uniform float u_aspect;

float hash(vec2 p) {
  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}
float noise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
             mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}
float fbm(vec2 p) {
  float value = 0.0;
  float weight = 0.5;
  for (int i = 0; i < 4; i++) {
    value += noise(p) * weight;
    p = p * 2.03 + vec2(13.7, 9.2);
    weight *= 0.5;
  }
  return value;
}
void main() {
  vec2 p = v_uv - 0.5;
  p.x *= u_aspect;
  float radius = length(p);
  float angle = atan(p.y, p.x);
  float turbulence = fbm(v_uv * 4.0 + vec2(u_time * 0.13, -u_time * 0.19));
  float curl = sin(angle * 7.0 - u_time * 1.45 + turbulence * 7.0);
  float front = radius * 0.77 + (turbulence - 0.5) * 0.26 + curl * 0.035;
  float reveal = smoothstep(front - 0.022, front + 0.022, u_progress);
  float edge = 1.0 - smoothstep(0.004, 0.065, abs(front - u_progress));

  vec2 flow = vec2(cos(angle + turbulence * 5.2 - u_time * 1.65),
                   sin(angle - turbulence * 4.6 + u_time * 1.35));
  flow += vec2(noise(v_uv * 5.0 + u_time * 0.2) - 0.5,
               noise(v_uv * 5.0 - u_time * 0.17) - 0.5) * 1.35;
  vec2 uv = clamp(v_uv + flow * (0.004 + edge * 0.027) * (1.0 - u_progress * 0.93), 0.002, 0.998);
  vec4 sharp = texture2D(u_image, uv);
  vec4 blurA = texture2D(u_image, clamp(uv + flow * 0.014 * u_energy, 0.002, 0.998));
  vec4 blurB = texture2D(u_image, clamp(uv + flow * 0.027 * u_energy, 0.002, 0.998));
  vec4 image = mix(sharp, (sharp + blurA + blurB) / 3.0, u_energy * 0.58);

  float light = exp(-radius * 3.3) * u_energy;
  vec3 metal = vec3(0.77, 0.86, 0.72);
  vec3 color = image.rgb + metal * edge * (0.48 + u_energy * 0.22) + vec3(0.10, 0.19, 0.12) * light;
  gl_FragColor = vec4(color, image.a * reveal);
}`;

function compileShader(gl: WebGLRenderingContext, type: number, source: string) {
  const shader = gl.createShader(type);
  if (!shader) throw new Error("Unable to allocate shader");
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    const reason = gl.getShaderInfoLog(shader) ?? "Shader compilation failed";
    gl.deleteShader(shader);
    throw new Error(reason);
  }
  return shader;
}

function makeProgram(gl: WebGLRenderingContext) {
  const vertex = compileShader(gl, gl.VERTEX_SHADER, vertexShader);
  const fragment = compileShader(gl, gl.FRAGMENT_SHADER, fragmentShader);
  const program = gl.createProgram();
  if (!program) throw new Error("Unable to allocate WebGL program");
  gl.attachShader(program, vertex);
  gl.attachShader(program, fragment);
  gl.linkProgram(program);
  gl.deleteShader(vertex);
  gl.deleteShader(fragment);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    const reason = gl.getProgramInfoLog(program) ?? "WebGL program link failed";
    gl.deleteProgram(program);
    throw new Error(reason);
  }
  return program;
}

function clamp(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, value));
}

type Particle = {
  angle: number;
  speed: number;
  start: number;
  size: number;
  drift: number;
  seed: number;
  originX: number;
  originY: number;
  ambient: boolean;
};

function makeParticles(): Particle[] {
  let seed = 0x514849;
  const random = () => {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    return seed / 4294967296;
  };
  return Array.from({ length: 116 }, (_, index) => {
    const ambient = index < 30;
    return {
      angle: random() * Math.PI * 2,
      speed: 0.16 + random() * 0.58,
      start: ambient ? random() * 0.8 : 2.34 + random() * 0.47,
      size: ambient ? 0.7 + random() * 1.6 : 1.3 + random() * 4.7,
      drift: random() * Math.PI * 2,
      seed: random() * 8,
      originX: random(),
      originY: random(),
      ambient,
    };
  });
}

function drawParticles(ctx: CanvasRenderingContext2D, width: number, height: number, time: number, particles: Particle[]) {
  ctx.clearRect(0, 0, width, height);
  const centerX = width / 2;
  const centerY = height / 2;

  for (const particle of particles) {
    const age = time - particle.start;
    if (age < 0) continue;

    if (particle.ambient) {
      const fadeIn = clamp(age / 0.5, 0, 1);
      const fadeOut = 1 - clamp((time - 3.75) / 0.85, 0, 1);
      const alpha = fadeIn * fadeOut * (0.25 + 0.3 * (0.5 + 0.5 * Math.sin(time * 1.7 + particle.seed)));
      const x = particle.originX * width + Math.sin(time * 0.35 + particle.drift) * 16;
      const y = (particle.originY * height + time * 13) % height;
      ctx.globalAlpha = alpha;
      ctx.fillStyle = "#cad9bb";
      ctx.beginPath();
      ctx.arc(x % width, y, particle.size, 0, Math.PI * 2);
      ctx.fill();
      continue;
    }

    if (age > 2.15) continue;
    const dissolve = 1 - clamp((age - 0.76) / 1.39, 0, 1);
    const launchX = centerX + Math.cos(particle.angle) * 12;
    const launchY = centerY + Math.sin(particle.angle) * 12;
    const vx = Math.cos(particle.angle) * width * particle.speed;
    const vy = Math.sin(particle.angle) * width * particle.speed;
    const turbulenceX = Math.sin(age * 8 + particle.drift) * width * 0.013 * age;
    const turbulenceY = Math.cos(age * 7 + particle.seed) * width * 0.012 * age;
    const x = launchX + vx * age + turbulenceX;
    const y = launchY + vy * age + age * age * height * 0.11 + turbulenceY;
    const alpha = clamp(age / 0.08, 0, 1) * dissolve * (0.66 + 0.24 * Math.sin(particle.seed + age * 10));
    const tailX = x - vx * 0.026;
    const tailY = y - vy * 0.026;
    ctx.globalAlpha = alpha;
    ctx.lineCap = "round";
    ctx.strokeStyle = particle.size > 3.6 ? "#e3e6d8" : "#a9c19b";
    ctx.lineWidth = Math.max(0.7, particle.size * (particle.size > 4 ? 0.48 : 0.24));
    ctx.beginPath();
    ctx.moveTo(tailX, tailY);
    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.fillStyle = particle.size > 3.6 ? "#f0eddd" : "#c8d7b9";
    ctx.shadowColor = "#c7ddb9";
    ctx.shadowBlur = particle.size > 3.6 ? 9 : 4;
    ctx.beginPath();
    ctx.ellipse(x, y, particle.size, Math.max(0.65, particle.size * 0.62), particle.angle, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;
  }
  ctx.globalAlpha = 1;
}

function drawCanvasFluid(ctx: CanvasRenderingContext2D, image: HTMLImageElement, width: number, height: number, progress: number, time: number) {
  ctx.clearRect(0, 0, width, height);
  if (progress <= 0) return;
  const diagonal = Math.hypot(width, height);
  const radius = diagonal * 0.72 * progress;
  ctx.save();
  ctx.beginPath();
  for (let i = 0; i <= 120; i++) {
    const angle = (i / 120) * Math.PI * 2;
    const ripple = (1 - progress) * (16 * Math.sin(angle * 6 + time * 2.1) + 8 * Math.sin(angle * 13 - time * 1.3));
    const r = Math.max(0, radius + ripple);
    const x = width / 2 + Math.cos(angle) * r;
    const y = height / 2 + Math.sin(angle) * r * 0.62;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.clip();
  const blur = Math.max(0, (1 - progress) * 7);
  ctx.filter = `blur(${blur.toFixed(1)}px) saturate(${(1.08 + (1 - progress) * 0.15).toFixed(2)})`;
  ctx.drawImage(image, 0, 0, width, height);
  ctx.filter = "none";
  ctx.restore();
}

export function BrandSplash() {
  const [visible, setVisible] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [renderer, setRenderer] = useState<Renderer>("pending");
  const startedInThisMount = useRef<boolean | null>(null);
  const artboardRef = useRef<HTMLDivElement>(null);
  const sourceRef = useRef<HTMLImageElement>(null);
  const webglCanvasRef = useRef<HTMLCanvasElement>(null);
  const fallbackCanvasRef = useRef<HTMLCanvasElement>(null);
  const particleCanvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (startedInThisMount.current === null) {
      const replay = new URLSearchParams(window.location.search).get("intro") === "1";
      try {
        const seen = window.sessionStorage.getItem(splashSessionKey);
        startedInThisMount.current = replay || !seen;
        if (startedInThisMount.current) window.sessionStorage.setItem(splashSessionKey, "shown");
      } catch {
        startedInThisMount.current = true;
      }
    }
    if (!startedInThisMount.current) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    setReducedMotion(reduceMotion);
    setRenderer(reduceMotion ? "static" : "pending");
    setVisible(true);
    const timeout = window.setTimeout(() => setVisible(false), reduceMotion ? 700 : splashDuration);
    return () => window.clearTimeout(timeout);
  }, []);

  useEffect(() => {
    if (!visible || reducedMotion) return;

    const image = sourceRef.current;
    const scene = artboardRef.current;
    const webglCanvas = webglCanvasRef.current;
    const fallbackCanvas = fallbackCanvasRef.current;
    const particleCanvas = particleCanvasRef.current;
    if (!image || !scene || !webglCanvas || !fallbackCanvas || !particleCanvas) return;

    let stopped = false;
    let animationFrame = 0;
    let startedAt = 0;
    let sceneWidth = 1;
    let sceneHeight = 1;
    let particleWidth = 1;
    let particleHeight = 1;
    let pixelRatio = 1;
    let gl: WebGLRenderingContext | null = null;
    let program: WebGLProgram | null = null;
    let texture: WebGLTexture | null = null;
    let buffer: WebGLBuffer | null = null;
    let glLocations: { progress: WebGLUniformLocation | null; time: WebGLUniformLocation | null; energy: WebGLUniformLocation | null; aspect: WebGLUniformLocation | null; image: WebGLUniformLocation | null } | null = null;
    let fallbackContext: CanvasRenderingContext2D | null = null;
    let particleContext: CanvasRenderingContext2D | null = null;
    let particles = makeParticles();
    let activeRenderer: "webgl" | "canvas" = "canvas";

    const resize = () => {
      const rect = scene.getBoundingClientRect();
      sceneWidth = Math.max(1, rect.width);
      sceneHeight = Math.max(1, rect.height);
      pixelRatio = Math.min(window.devicePixelRatio || 1, 1.35, 1600 / sceneWidth);
      const width = Math.max(1, Math.round(sceneWidth * pixelRatio));
      const height = Math.max(1, Math.round(sceneHeight * pixelRatio));
      webglCanvas.width = width;
      webglCanvas.height = height;
      fallbackCanvas.width = width;
      fallbackCanvas.height = height;
      if (gl) gl.viewport(0, 0, width, height);

      const particleRect = particleCanvas.getBoundingClientRect();
      particleWidth = Math.max(1, particleRect.width);
      particleHeight = Math.max(1, particleRect.height);
      const particleRatio = Math.min(window.devicePixelRatio || 1, 1.25, 1800 / particleWidth);
      particleCanvas.width = Math.max(1, Math.round(particleWidth * particleRatio));
      particleCanvas.height = Math.max(1, Math.round(particleHeight * particleRatio));
      particleContext?.setTransform(particleRatio, 0, 0, particleRatio, 0, 0);
      fallbackContext?.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
    };

    particleContext = particleCanvas.getContext("2d", { alpha: true });

    const prepareCanvasFallback = () => {
      if (stopped) return;
      activeRenderer = "canvas";
      fallbackContext = fallbackCanvas.getContext("2d", { alpha: true });
      if (!fallbackContext) {
        setRenderer("static");
        return;
      }
      resize();
      setRenderer("canvas");
    };

    const prepareWebGL = () => {
      if (stopped) return;
      try {
        gl = webglCanvas.getContext("webgl", { alpha: true, antialias: false, depth: false, stencil: false, premultipliedAlpha: true });
        if (!gl) throw new Error("WebGL is not available");
        program = makeProgram(gl);
        buffer = gl.createBuffer();
        texture = gl.createTexture();
        if (!buffer || !texture) throw new Error("Unable to allocate WebGL resources");

        gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
        gl.useProgram(program);
        const position = gl.getAttribLocation(program, "a_position");
        gl.enableVertexAttribArray(position);
        gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);

        gl.activeTexture(gl.TEXTURE0);
        gl.bindTexture(gl.TEXTURE_2D, texture);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, 1);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        glLocations = {
          progress: gl.getUniformLocation(program, "u_progress"),
          time: gl.getUniformLocation(program, "u_time"),
          energy: gl.getUniformLocation(program, "u_energy"),
          aspect: gl.getUniformLocation(program, "u_aspect"),
          image: gl.getUniformLocation(program, "u_image"),
        };
        gl.uniform1i(glLocations.image, 0);
        activeRenderer = "webgl";
        resize();
        setRenderer("webgl");
      } catch {
        prepareCanvasFallback();
      }
    };

    const observer = typeof ResizeObserver === "undefined" ? null : new ResizeObserver(resize);
    observer?.observe(scene);
    window.addEventListener("resize", resize, { passive: true });
    resize();

    const frame = (now: number) => {
      if (stopped) return;
      if (!startedAt) startedAt = now;
      const elapsed = (now - startedAt) / 1000;
      const raw = clamp((elapsed - 0.43) / 2.72, 0, 1);
      const progress = raw * raw * (3 - 2 * raw);
      const impact = Math.exp(-Math.pow((elapsed - 2.72) / 0.48, 2));
      const energy = Math.max((1 - progress) * 0.86, impact * 0.92);

      if (activeRenderer === "webgl" && gl && program && glLocations) {
        gl.clearColor(0, 0, 0, 0);
        gl.clear(gl.COLOR_BUFFER_BIT);
        gl.useProgram(program);
        gl.uniform1f(glLocations.progress, progress);
        gl.uniform1f(glLocations.time, elapsed);
        gl.uniform1f(glLocations.energy, energy);
        gl.uniform1f(glLocations.aspect, sceneWidth / sceneHeight);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      } else if (fallbackContext) {
        drawCanvasFluid(fallbackContext, image, sceneWidth, sceneHeight, progress, elapsed);
      }

      if (particleContext) drawParticles(particleContext, particleWidth, particleHeight, elapsed, particles);
      animationFrame = window.requestAnimationFrame(frame);
    };

    const start = () => {
      if (stopped) return;
      prepareWebGL();
      animationFrame = window.requestAnimationFrame(frame);
    };
    const handleImageError = () => {
      if (stopped) return;
      setRenderer("static");
    };
    const handleContextLost = (event: Event) => {
      event.preventDefault();
      prepareCanvasFallback();
    };
    webglCanvas.addEventListener("webglcontextlost", handleContextLost);

    if (image.complete && image.naturalWidth > 0) start();
    else image.addEventListener("load", start, { once: true });
    image.addEventListener("error", handleImageError, { once: true });

    return () => {
      stopped = true;
      window.cancelAnimationFrame(animationFrame);
      image.removeEventListener("load", start);
      image.removeEventListener("error", handleImageError);
      window.removeEventListener("resize", resize);
      observer?.disconnect();
      webglCanvas.removeEventListener("webglcontextlost", handleContextLost);
      if (gl) {
        if (texture) gl.deleteTexture(texture);
        if (buffer) gl.deleteBuffer(buffer);
        if (program) gl.deleteProgram(program);
      }
      particles = [];
    };
  }, [visible, reducedMotion]);

  if (!visible) return null;

  const modeClass = renderer === "webgl" ? "cinematic-splash--webgl" : renderer === "canvas" ? "cinematic-splash--canvas" : renderer === "static" ? "cinematic-splash--static" : "cinematic-splash--pending";
  return (
    <div className={`cinematic-splash ${modeClass}${reducedMotion ? " cinematic-splash--reduced" : ""}`} aria-hidden="true" data-renderer={renderer}>
      <div className="cinematic-splash__core">
        <div className="cinematic-splash__visual">
          <div className="cinematic-splash__artboard" ref={artboardRef}>
            <Image
              ref={sourceRef}
              className="cinematic-splash__source"
              src="/images/003.jpeg"
              alt=""
              fill
              unoptimized
              priority
              sizes="(max-width: 720px) 94vw, min(92vw, 1160px)"
            />
            <canvas ref={webglCanvasRef} className="cinematic-splash__webgl" />
            <canvas ref={fallbackCanvasRef} className="cinematic-splash__canvas-fallback" />
          </div>
          <canvas ref={particleCanvasRef} className="cinematic-splash__particles" />
        </div>
        <div className="cinematic-splash__wordmark"><span>AUTO</span></div>
      </div>
    </div>
  );
}
