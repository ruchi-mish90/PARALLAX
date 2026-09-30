import React, { useEffect, useState } from 'react';
import { useParallax } from '../../state/ParallaxContext';

export const CustomCursor: React.FC = () => {
  const { cursorLabel, isTouchDevice } = useParallax();
  const [pos, setPos] = useState({ x: -100, y: -100 });
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (isTouchDevice) return;

    const handleMouseMove = (e: MouseEvent) => {
      setPos({ x: e.clientX, y: e.clientY });
      if (!visible) setVisible(true);
    };

    const handleMouseLeave = () => setVisible(false);

    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    document.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [visible, isTouchDevice]);

  if (isTouchDevice || !visible) return null;

  return (
    <div
      className="pointer-events-none fixed z-50 transition-transform duration-75 ease-out"
      style={{
        transform: `translate3d(${pos.x}px, ${pos.y}px, 0)`,
        left: 0,
        top: 0,
      }}
    >
      {/* Precision optical reticle crosshair (1px hairline) */}
      <div className="relative -left-2 -top-2 h-4 w-4">
        {/* Subtle circular boundary */}
        <div className="absolute inset-0 rounded-full border border-white/40" />
        {/* Center reticle point */}
        <div className="absolute top-1/2 left-1/2 h-1 w-1 -translate-x-1/2 -translate-y-1/2 bg-[#F7F7F5]" />
      </div>

      {/* Dynamic Context Tag (Restrained technical readout) */}
      {cursorLabel && (
        <div className="absolute left-4 top-2 whitespace-nowrap rounded-none border border-[#333333] bg-[#161616] px-2 py-0.5 font-mono-tech text-[10px] tracking-wider text-[#F7F7F5] uppercase shadow-md">
          {cursorLabel}
        </div>
      )}
    </div>
  );
};
