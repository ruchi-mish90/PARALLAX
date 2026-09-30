import React from "react"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { ParallaxProvider } from "./state/ParallaxContext"
import { CustomCursor } from "./components/common/CustomCursor"
import { ScrollToTop } from "./components/common/ScrollToTop"
import { ParallaxNavigation } from "./components/navigation/ParallaxNavigation"
import { ContextualAssistant } from "./components/assistant/ContextualAssistant"

// Dedicated Route Pages
import { HomePage } from "./pages/HomePage"
import { ExplorePage } from "./pages/ExplorePage"
import { InstrumentsPage } from "./pages/InstrumentsPage"
import { CorrespondencePage } from "./pages/CorrespondencePage"
import { AnalysisPage } from "./pages/AnalysisPage"
import { SimulatorPage } from "./pages/SimulatorPage"
import { AboutPage } from "./pages/AboutPage"

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <ParallaxProvider>
        <div className="relative min-h-screen bg-[#111111] text-[#F7F7F5] selection:bg-white/20 selection:text-white overflow-x-hidden font-sans">
          {/* Scroll Isolation: Guarantees every route starts at scroll position 0 */}
          <ScrollToTop />

          {/* Desktop Precision Cursor */}
          <CustomCursor />

          {/* Official PARALLAX Navigation: Restrained NASA Kinetic Navigation */}
          <ParallaxNavigation />

          {/* Multi-Page Route Architecture */}
          <main className="relative z-10 min-h-screen flex flex-col bg-[#111111]">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/explore" element={<ExplorePage />} />
              <Route path="/instruments" element={<InstrumentsPage />} />
              <Route path="/correspondence" element={<CorrespondencePage />} />
              <Route path="/analysis" element={<AnalysisPage />} />
              <Route path="/simulator" element={<SimulatorPage />} />
              <Route path="/about" element={<AboutPage />} />
              {/* Fallback redirect */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>

          {/* Global Grounded Scientific AI Assistant */}
          <ContextualAssistant />
        </div>
      </ParallaxProvider>
    </BrowserRouter>
  )
}

export default App
