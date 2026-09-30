import React from 'react';

export type TechnicalBadgeVariant = 
  | 'accept' 
  | 'warning' 
  | 'reject' 
  | 'neutral' 
  | 'editorial' 
  | 'demo' 
  | 'live' 
  | 'cyan' 
  | 'amber';

interface TechnicalBadgeProps {
  label: string;
  variant?: TechnicalBadgeVariant;
  icon?: React.ReactNode;
  className?: string;
}

export const TechnicalBadge: React.FC<TechnicalBadgeProps> = ({
  label,
  variant = 'neutral',
  icon,
  className = '',
}) => {
  // Muted functional states per NASA-inspired scientific guidelines
  const variantStyles: Record<TechnicalBadgeVariant, string> = {
    accept: 'bg-[#1A2E1C] border-[#2E5E32] text-[#86D88E]',
    warning: 'bg-[#2E2211] border-[#5E4218] text-[#E0A855]',
    reject: 'bg-[#2E1616] border-[#5E2626] text-[#E57373]',
    neutral: 'bg-[#181818] border-[#2E2E2E] text-[#B8B8B5]',
    editorial: 'bg-[#F7F7F5] border-[#F7F7F5] text-[#111111] font-bold',
    // Backward compatibility mappings
    live: 'bg-[#1A2E1C] border-[#2E5E32] text-[#86D88E]',
    demo: 'bg-[#2E2211] border-[#5E4218] text-[#E0A855]',
    amber: 'bg-[#2E2211] border-[#5E4218] text-[#E0A855]',
    cyan: 'bg-[#1E1E1E] border-[#383838] text-[#E4E4E2]',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-none font-mono-tech text-[10px] tracking-wider uppercase border ${variantStyles[variant] || variantStyles.neutral} ${className}`}
    >
      {icon}
      <span>{label}</span>
    </span>
  );
};
