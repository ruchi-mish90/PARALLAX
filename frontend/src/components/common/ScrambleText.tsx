import React, { useEffect, useState, useRef } from 'react';

interface ScrambleTextProps {
  text: string;
  className?: string;
  scrambleSpeed?: number; // ms per frame
  charset?: string;
  triggerOnHover?: boolean;
}

const DEFAULT_CHARSET = '0123456789ABCDEF_<>[]/\\#%*+~=';

export const ScrambleText: React.FC<ScrambleTextProps> = ({
  text,
  className = '',
  scrambleSpeed = 24,
  charset = DEFAULT_CHARSET,
  triggerOnHover = false,
}) => {
  const [displayText, setDisplayText] = useState(text);
  const frameRef = useRef<number | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const startScramble = (targetText: string) => {
    if (intervalRef.current) clearInterval(intervalRef.current);

    let iteration = 0;
    const maxIterations = targetText.length;

    intervalRef.current = setInterval(() => {
      setDisplayText(() => {
        return targetText
          .split('')
          .map((char, index) => {
            if (char === ' ') return ' ';
            if (index < iteration) {
              return targetText[index];
            }
            return charset[Math.floor(Math.random() * charset.length)];
          })
          .join('');
      });

      iteration += 1 / 2;

      if (iteration >= maxIterations) {
        if (intervalRef.current) clearInterval(intervalRef.current);
        setDisplayText(targetText);
      }
    }, scrambleSpeed);
  };

  useEffect(() => {
    startScramble(text);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (frameRef.current) cancelAnimationFrame(frameRef.current);
    };
  }, [text]);

  return (
    <span
      className={`inline-block font-mono-tech transition-colors ${className}`}
      onMouseEnter={() => {
        if (triggerOnHover) startScramble(text);
      }}
    >
      {displayText}
    </span>
  );
};
