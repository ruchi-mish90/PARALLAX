import React from "react";

export interface RadialVignetteBackgroundProps {
  className?: string;
  children?: React.ReactNode;
}

export const RadialVignetteBackground: React.FC<RadialVignetteBackgroundProps> = ({
  className = "",
  children,
}) => {
  return (
    <div
      aria-hidden="true"
      className={`fixed inset-0 z-0 h-full w-full pointer-events-none bg-neutral-950 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))] overflow-hidden ${className}`}
    >
      {children}
    </div>
  );
};

export default RadialVignetteBackground;
