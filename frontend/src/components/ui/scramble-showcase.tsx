"use client"

import ScrambleText from "@/components/ui/motion-scramble-text"
import { Sparkles, Terminal, Cpu, Layers } from "lucide-react"

export function ScrambleShowcase() {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-space-900/90 shadow-2xl backdrop-blur-xl">
      {/* Background Unsplash Stock Image with dark gradient overlay */}
      <div className="absolute inset-0 -z-10 opacity-30">
        <img
          src="https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=1600&q=80"
          alt="Space background"
          className="h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-space-950 via-space-950/80 to-transparent" />
      </div>

      {/* Header bar with Lucide Icons */}
      <div className="flex items-center justify-between border-b border-white/10 px-6 py-4">
        <div className="flex items-center gap-2 text-cyan-accent">
          <Terminal className="h-4 w-4" />
          <span className="font-mono-tech text-xs tracking-wider uppercase text-lunar-300">
            Telemetry Stream / Motion Scramble Text
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-cyan-accent/10 px-2.5 py-0.5 text-xs font-medium text-cyan-accent border border-cyan-accent/20">
            <span className="h-1.5 w-1.5 rounded-full bg-cyan-accent animate-ping" />
            Active Scramble
          </span>
          <Cpu className="h-4 w-4 text-lunar-400" />
        </div>
      </div>

      {/* Main Scramble Text Display */}
      <div className="flex flex-col items-center justify-center p-12 text-center min-h-[220px]">
        <ScrambleText />
      </div>

      {/* Footer info banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-t border-white/10 bg-space-950/60 px-6 py-3 text-xs text-lunar-400">
        <div className="flex items-center gap-2">
          <Sparkles className="h-3.5 w-3.5 text-cyan-accent" />
          <span>Real-time progressive glyph decryption effect</span>
        </div>
        <div className="flex items-center gap-4 font-mono-tech">
          <span className="flex items-center gap-1">
            <Layers className="h-3.5 w-3.5 text-azure-accent" />
            <span>RAF: 600ms / 60fps</span>
          </span>
          <span>Cycle: 2000ms</span>
        </div>
      </div>
    </div>
  )
}

export default ScrambleShowcase
