"use client"
import React from "react"
import { motion } from "framer-motion"

export interface AuroraBackgroundProps {
  /** Extra wrapper classes */
  className?: string
  /** Content to render on top of the background */
  children?: React.ReactNode
  /** Number of “star” points */
  starCount?: number
  /** Two CSS-variable backed colors for the radial overlays */
  gradientColors?: [string, string]
  /** Pulse animation duration in seconds */
  pulseDuration?: number
  /** ARIA label for the animated background */
  ariaLabel?: string
}

const AuroraBackground: React.FC<AuroraBackgroundProps> = ({
  className = "",
  children,
  starCount = 65,
  gradientColors = [
    "var(--aurora-color1, rgba(168,85,247,0.35))",
    "var(--aurora-color2, rgba(79,70,229,0.35))",
  ],
  pulseDuration = 8,
  ariaLabel = "Animated aurora background",
}) => {
  const [colorA, colorB] = gradientColors

  return (
    <div
      role="img"
      aria-label={ariaLabel}
      className={`relative flex flex-col w-full h-full items-center justify-center text-slate-50 overflow-hidden ${className}`}
    >
      {/* Background layers (hidden from screen readers) */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
        {/* Pulsing radial gradients */}
        <div
          className="absolute inset-0 opacity-70"
          style={{
            backgroundImage: `
              radial-gradient(circle at 25% 25%, ${colorA} 0%, transparent 65%),
              radial-gradient(circle at 75% 75%, ${colorB} 0%, transparent 65%),
              radial-gradient(ellipse at 50% 15%, var(--aurora-color3, rgba(6,182,212,0.25)) 0%, transparent 55%),
              radial-gradient(ellipse at 80% 25%, var(--aurora-color4, rgba(236,72,153,0.2)) 0%, transparent 50%)
            `,
            backgroundSize: "100% 100%",
            animation: `pulse ${pulseDuration}s infinite`,
          }}
        />

        {/* Blurred color blobs - Vibrant Cosmic Aurora */}
        <motion.div
          className="absolute inset-0 mix-blend-screen pointer-events-none"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.2, ease: "easeInOut" }}
        >
          {/* Vibrant Purple Blob */}
          <motion.div
            className="absolute -top-1/4 -left-1/4 w-3/5 h-3/5 bg-purple-600 rounded-full filter blur-[100px] opacity-45"
            animate={{
              x: [-40, 60, -40],
              y: [-25, 25, -25],
              scale: [1, 1.25, 1],
            }}
            transition={{
              duration: 26,
              repeat: Infinity,
              repeatType: "mirror",
              ease: "easeInOut",
            }}
          />

          {/* Glowing Fuchsia Blob */}
          <motion.div
            className="absolute -bottom-1/4 -right-1/4 w-3/5 h-3/5 bg-fuchsia-600 rounded-full filter blur-[110px] opacity-45"
            animate={{
              x: [50, -50, 50],
              y: [30, -30, 30],
              scale: [1, 1.3, 1],
            }}
            transition={{
              duration: 32,
              repeat: Infinity,
              repeatType: "mirror",
              ease: "easeInOut",
            }}
          />

          {/* Deep Indigo/Blue Blob */}
          <motion.div
            className="absolute top-1/4 left-1/3 w-1/2 h-1/2 bg-indigo-700 rounded-full filter blur-[105px] opacity-40"
            animate={{
              x: [25, -35, 25],
              y: [-25, 30, -25],
              rotate: [0, 180, 360],
            }}
            transition={{
              duration: 40,
              repeat: Infinity,
              repeatType: "mirror",
              ease: "easeInOut",
            }}
          />

          {/* Electric Cyan/Teal Accent Blob */}
          <motion.div
            className="absolute bottom-1/4 left-1/4 w-2/5 h-2/5 bg-cyan-400 rounded-full filter blur-[95px] opacity-35"
            animate={{
              x: [-30, 40, -30],
              y: [20, -20, 20],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 30,
              repeat: Infinity,
              repeatType: "mirror",
              ease: "easeInOut",
            }}
          />
        </motion.div>

        {/* Twinkling stars */}
        {Array.from({ length: starCount }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-[1.5px] h-[1.5px] bg-white rounded-full pointer-events-none shadow-[0_0_4px_rgba(255,255,255,0.8)]"
            initial={{
              x: `${(i * 1.57 + 7) % 100}vw`,
              y: `${(i * 2.39 + 13) % 100}vh`,
              opacity: 0.1,
            }}
            animate={{
              opacity: [0.1, 0.9, 0.1],
              scale: [0.8, 1.4, 0.8],
            }}
            transition={{
              duration: 2.5 + (i % 5) * 0.8,
              repeat: Infinity,
              delay: (i % 7) * 0.6,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>

      {/* Foreground content */}
      {children && <div className="relative z-10 w-full">{children}</div>}
    </div>
  )
}

export default AuroraBackground
