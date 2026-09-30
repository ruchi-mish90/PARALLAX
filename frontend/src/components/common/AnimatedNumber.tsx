import React, { useEffect, useState, useRef } from 'react';

interface AnimatedNumberProps {
  value: number;
  decimals?: number;
  duration?: number; // in ms
  prefix?: string;
  suffix?: string;
  className?: string;
}

export const AnimatedNumber: React.FC<AnimatedNumberProps> = ({
  value,
  decimals = 0,
  duration = 800,
  prefix = '',
  suffix = '',
  className = '',
}) => {
  const safeTarget = typeof value === 'number' && !isNaN(value) ? value : 0;
  const [displayValue, setDisplayValue] = useState<number>(safeTarget);
  const startValueRef = useRef<number>(safeTarget);
  const startTimeRef = useRef<number | null>(null);
  const animFrameRef = useRef<number | null>(null);

  useEffect(() => {
    startValueRef.current = typeof displayValue === 'number' && !isNaN(displayValue) ? displayValue : 0;
    startTimeRef.current = null;

    const animate = (timestamp: number) => {
      if (!startTimeRef.current) startTimeRef.current = timestamp;
      const progress = Math.min((timestamp - startTimeRef.current) / duration, 1);

      // Ease-out cubic curve
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = startValueRef.current + (safeTarget - startValueRef.current) * easeOut;

      setDisplayValue(current);

      if (progress < 1) {
        animFrameRef.current = requestAnimationFrame(animate);
      } else {
        setDisplayValue(safeTarget);
      }
    };

    animFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [safeTarget, duration]);

  const formatted = typeof displayValue === 'number' && !isNaN(displayValue) 
    ? displayValue.toFixed(decimals) 
    : (0).toFixed(decimals);

  return (
    <span className={`inline-block tabular-nums font-mono-tech ${className}`}>
      {prefix}
      {formatted}
      {suffix}
    </span>
  );
};
