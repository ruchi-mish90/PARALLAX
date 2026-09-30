import React from "react";

export interface BackgroundSnippetsProps {
  className?: string;
  children?: React.ReactNode;
}

export const Component: React.FC<BackgroundSnippetsProps> = ({ className = "", children }) => {
  return (
    <div className={`absolute inset-0 -z-10 h-full w-full bg-white bg-[linear-gradient(to_right,#f0f0f0_1px,transparent_1px),linear-gradient(to_bottom,#f0f0f0_1px,transparent_1px)] bg-[size:6rem_4rem] ${className}`}>
      <div className="absolute bottom-0 left-0 right-0 top-0 bg-[radial-gradient(circle_800px_at_100%_200px,#d5c5ff,transparent)]"></div>
      {children}
    </div>
  );
};

export const BackgroundSnippets = Component;
export default Component;
