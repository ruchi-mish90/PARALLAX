"use client"

import { useEffect, useState, useRef } from "react"
import "./motion-scramble-text-utils/index.css"

export const PARALLAX_DEFAULT_WORDS = [
  "PARALLAX",
  "CROSS-INSTRUMENT",
  "LUNAR TERRAIN",
  "OHRC 0.25M",
  "TMC-2 STEREO",
  "IIRS HYPERSPECTRAL",
  "FEATURE DETECTION",
  "KEYPOINTS",
  "DESCRIPTORS",
  "IMAGE MATCHING",
  "CORRESPONDENCE",
  "RANSAC INLIERS",
  "GEOMETRIC VERIFICATION",
  "SUBPIXEL ALIGNMENT",
  "LUNAR MAPPING",
] as const

const DEFAULT_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`░▒▓█▀▄■□▪▫●○◆◇◈◊※†‡0123456789"

function randomChar(charset: string) {
  return charset[Math.floor(Math.random() * charset.length)]
}

function scrambleWord(target: string, progress: number, charset: string) {
  const reveal = Math.floor(progress * target.length)
  return target
    .split("")
    .map((ch, i) => {
      // Preserve spaces and punctuation structure
      if (ch === " ") return " "
      return i < reveal ? ch : randomChar(charset)
    })
    .join("")
}

export interface ScrambleTextProps {
  /** List of words/phrases to cycle through. Defaults to authentic PARALLAX mission vocabulary. */
  words?: readonly string[]
  /** Interval in milliseconds between word transitions. Defaults to 2400ms. */
  interval?: number
  /** Duration in milliseconds of the scramble resolve animation. Defaults to 650ms. */
  duration?: number
  /** Optional custom CSS class name for styling the text element. */
  className?: string
  /** Custom character set for the scramble glyph generator. */
  chars?: string
  /** HTML tag for the rendered text container. Defaults to 'span'. */
  as?: "h1" | "h2" | "h3" | "h4" | "p" | "span" | "div"
  /** Optional callback fired when the active word cycles. */
  onWordChange?: (word: string, index: number) => void
}

export function ScrambleText({
  words = PARALLAX_DEFAULT_WORDS,
  interval = 2400,
  duration = 650,
  className = "",
  chars = DEFAULT_CHARS,
  as: Component = "span",
  onWordChange,
}: ScrambleTextProps) {
  const activeWords = words && words.length > 0 ? words : PARALLAX_DEFAULT_WORDS
  const [index, setIndex] = useState(0)
  const [display, setDisplay] = useState<string>(activeWords[0])
  const prefersReducedMotionRef = useRef<boolean>(false)

  // Detect prefers-reduced-motion for accessibility (Step 10)
  useEffect(() => {
    if (typeof window !== "undefined") {
      const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)")
      prefersReducedMotionRef.current = mediaQuery.matches

      const handleChange = (e: MediaQueryListEvent) => {
        prefersReducedMotionRef.current = e.matches
      }

      mediaQuery.addEventListener("change", handleChange)
      return () => mediaQuery.removeEventListener("change", handleChange)
    }
  }, [])

  // Word cycling interval (cleanup properly)
  useEffect(() => {
    if (activeWords.length <= 1) return

    const id = setInterval(() => {
      setIndex((current) => {
        const nextIndex = (current + 1) % activeWords.length
        if (onWordChange) {
          onWordChange(activeWords[nextIndex], nextIndex)
        }
        return nextIndex
      })
    }, interval)

    return () => clearInterval(id)
  }, [activeWords, interval, onWordChange])

  // Animation frame scramble resolution
  useEffect(() => {
    const target = activeWords[index] || activeWords[0] || ""

    // Accessible fallback: if user prefers reduced motion, show target text instantly
    if (prefersReducedMotionRef.current) {
      setDisplay(target)
      return
    }

    const started = performance.now()
    let frameId: number = 0

    const tick = (now: number) => {
      const elapsed = now - started
      const progress = Math.min(1, elapsed / duration)
      
      setDisplay(progress >= 1 ? target : scrambleWord(target, progress, chars))

      if (progress < 1) {
        frameId = requestAnimationFrame(tick)
      }
    }

    frameId = requestAnimationFrame(tick)

    return () => {
      if (frameId) {
        cancelAnimationFrame(frameId)
      }
    }
  }, [index, activeWords, duration, chars])

  return (
    <div className="motion-scramble-container inline-flex items-center justify-center max-w-full overflow-hidden">
      <Component
        className={`motion-scramble-text font-display-tech tabular-nums tracking-wide select-none ${className}`}
        aria-label={display}
        aria-live="polite"
      >
        {display}
      </Component>
    </div>
  )
}

export default ScrambleText
