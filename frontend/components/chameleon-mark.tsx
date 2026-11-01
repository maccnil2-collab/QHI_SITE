import Image from "next/image";

type ChameleonMarkProps = {
  className?: string;
  priority?: boolean;
  sizes?: string;
};

export function ChameleonMark({ className = "", priority = false, sizes = "(max-width: 720px) 72vw, 560px" }: ChameleonMarkProps) {
  return (
    <span className={`chameleon-mark ${className}`} aria-hidden="true">
      <Image
        className="chameleon-mark__art"
        src="/images/qhi-chameleon.webp"
        alt=""
        width={623}
        height={485}
        sizes={sizes}
        priority={priority}
      />
      <span className="chameleon-mark__sheen" />
      <span className="chameleon-mark__eye" />
    </span>
  );
}
