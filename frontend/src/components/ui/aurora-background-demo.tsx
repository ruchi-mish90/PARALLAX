"use client"
import AuroraBackground, { AuroraBackgroundProps } from "@/components/ui/aurora-background"

export const AuroraBackgroundDemo = () => {
  const demoProps: AuroraBackgroundProps = {
    gradientColors: [
      "var(--aurora-color1, rgba(99,102,241,0.2))",
      "var(--aurora-color2, rgba(139,92,246,0.2))",
    ],
    pulseDuration: 8,
    starCount: 80,
  }

  return (
    <AuroraBackground {...demoProps} className="px-4 py-8">
      <h1 className="text-5xl md:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-br from-gray-50 to-gray-400 tracking-tight text-center">
        Aurora UI
      </h1>
      <p className="mt-4 text-lg text-gray-300 max-w-xl text-center">
        A shimmering canvas of light to power your next interface.
      </p>
    </AuroraBackground>
  )
}

export default AuroraBackgroundDemo
