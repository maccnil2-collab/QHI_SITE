"use client";

import { useEffect, useState } from "react";
import { ChameleonMark } from "@/components/chameleon-mark";

const splashSessionKey = "qhi-auto:splash:v1";

export function BrandSplash() {
  const [visible, setVisible] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    try {
      if (window.sessionStorage.getItem(splashSessionKey)) return;
      window.sessionStorage.setItem(splashSessionKey, "shown");
    } catch {
      // A restricted storage context should not stop the site from rendering.
    }

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    setReducedMotion(reduceMotion);
    setVisible(true);

    const timeout = window.setTimeout(() => setVisible(false), reduceMotion ? 650 : 2_100);
    return () => window.clearTimeout(timeout);
  }, []);

  if (!visible) return null;

  return (
    <div className={`brand-splash${reducedMotion ? " brand-splash--reduced" : ""}`} aria-hidden="true">
      <div className="brand-splash__content">
        <ChameleonMark className="brand-splash__mark" priority sizes="(max-width: 720px) 80vw, 560px" />
        <span className="brand-splash__wordmark">QHI AUTO</span>
      </div>
    </div>
  );
}
