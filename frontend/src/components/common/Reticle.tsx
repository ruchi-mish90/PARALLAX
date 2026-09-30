import React from 'react';

interface ReticleProps {
  size?: number;
  className?: string;
  active?: boolean;
}

export const Reticle: React.FC<ReticleProps> = ({ size = 32, className = '', active = false }) => {
  return (
    <div 
      className={`relative flex items-center justify-center ${className}`}
      style={{ width: size, height: size }}
    >
      {/* Outer corner marks */}
      <div className="absolute inset-0 border border-dashed border-cyan-accent/30 rounded-full animate-reticle-spin" />
      
      {/* Reticle crosshair lines */}
      <div className="absolute w-full h-[1px] bg-cyan-accent/40" />
      <div className="absolute h-full w-[1px] bg-cyan-accent/40" />
      
      {/* Central target core */}
      <div 
        className={`rounded-full transition-all duration-300 ${
          active 
            ? 'h-3 w-3 bg-cyan-accent shadow-[0_0_10px_#64D2FF]' 
            : 'h-1.5 w-1.5 bg-cyan-accent/80'
        }`} 
      />
    </div>
  );
};
