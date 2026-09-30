import React, { useState, useEffect } from 'react';
import { useParallax } from '../../state/ParallaxContext';
import { Compass, Sparkles, BookOpen, Menu, X, Activity } from 'lucide-react';

export const Navigation: React.FC = () => {
  const { 
    explainMode, 
    toggleExplainMode, 
    sourceInstrument, 
    targetInstrument,
    setCursorLabel 
  } = useParallax();

  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeSection, setActiveSection] = useState('hero');

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 40);

      // Section tracking
      const sections = ['hero', 'problem', 'explore', 'instruments', 'correspondence', 'analysis', 'simulator', 'mission'];
      for (const section of sections) {
        const el = document.getElementById(section);
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.top <= 200 && rect.bottom >= 200) {
            setActiveSection(section);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { id: 'hero', label: 'MISSION' },
    { id: 'explore', label: 'EXPLORE' },
    { id: 'instruments', label: 'INSTRUMENTS' },
    { id: 'correspondence', label: 'CORRESPONDENCE' },
    { id: 'analysis', label: 'ANALYSIS' },
    { id: 'simulator', label: 'SIMULATOR' },
    { id: 'mission', label: 'ABOUT' },
  ];

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
    setMobileMenuOpen(false);
  };

  return (
    <header 
      className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 ${
        scrolled 
          ? 'bg-space-950/85 backdrop-blur-md border-b border-white/10 py-3 shadow-2xl' 
          : 'bg-transparent py-5'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          
          {/* Brand Logo & Mission Tag */}
          <div 
            className="flex items-center gap-3 cursor-pointer group"
            onClick={() => scrollToSection('hero')}
            onMouseEnter={() => setCursorLabel('PARALLAX HOME')}
            onMouseLeave={() => setCursorLabel('')}
          >
            <div className="h-8 w-8 rounded-full border border-cyan-accent/60 flex items-center justify-center bg-cyan-accent/5 group-hover:border-cyan-accent transition-colors">
              <Compass className="h-4 w-4 text-cyan-accent group-hover:rotate-45 transition-transform duration-500" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-display-tech font-bold tracking-widest text-base sm:text-lg text-white">
                  PARALLAX
                </span>
                <span className="hidden sm:inline-block px-1.5 py-0.5 rounded text-[10px] font-mono-tech bg-white/5 border border-white/10 text-lunar-400">
                  CH-2
                </span>
              </div>
              <p className="hidden md:block text-[10px] font-mono-tech text-lunar-400 tracking-wider uppercase">
                CROSS-INSTRUMENT LUNAR CORRESPONDENCE
              </p>
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1 xl:gap-2">
            {navLinks.map((link) => (
              <button
                key={link.id}
                onClick={() => scrollToSection(link.id)}
                onMouseEnter={() => setCursorLabel(`JUMP TO ${link.label}`)}
                onMouseLeave={() => setCursorLabel('')}
                className={`px-3 py-1 rounded text-xs font-mono-tech tracking-wider transition-all ${
                  activeSection === link.id
                    ? 'text-cyan-accent bg-cyan-accent/10 border border-cyan-accent/30'
                    : 'text-lunar-400 hover:text-white hover:bg-white/5 border border-transparent'
                }`}
              >
                {link.label}
              </button>
            ))}
          </nav>

          {/* Active Context Breadcrumb & Scientific/Explain Toggle */}
          <div className="flex items-center gap-3">
            {/* Active Pair Pill */}
            <div className="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded border border-white/10 bg-space-900/60 text-[11px] font-mono-tech text-lunar-300">
              <Activity className="h-3.5 w-3.5 text-cyan-accent animate-pulse" />
              <span>{sourceInstrument}</span>
              <span className="text-lunar-500">×</span>
              <span>{targetInstrument}</span>
            </div>

            {/* Scientific vs. Explain Mode Toggle */}
            <button
              onClick={toggleExplainMode}
              onMouseEnter={() => setCursorLabel(explainMode ? 'SWITCH TO SCIENTIFIC' : 'SWITCH TO EXPLAIN')}
              onMouseLeave={() => setCursorLabel('')}
              className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-mono-tech tracking-wider border transition-all duration-300 ${
                explainMode 
                  ? 'bg-amber-500/15 border-amber-500/50 text-amber-300 hover:bg-amber-500/25' 
                  : 'bg-cyan-accent/10 border-cyan-accent/40 text-cyan-accent hover:bg-cyan-accent/20'
              }`}
              title="Toggle between dense scientific terminology and accessible conversational explanations"
            >
              {explainMode ? (
                <>
                  <BookOpen className="h-3.5 w-3.5 text-amber-400" />
                  <span className="font-semibold">EXPLAIN MODE</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-3.5 w-3.5 text-cyan-accent" />
                  <span className="font-semibold">SCIENTIFIC MODE</span>
                </>
              )}
            </button>

            {/* Mobile Menu Button */}
            <button
              className="lg:hidden p-2 rounded border border-white/10 text-lunar-300 hover:text-white"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-space-950/95 border-b border-white/10 px-4 pt-4 pb-6 space-y-2 backdrop-blur-xl">
          {navLinks.map((link) => (
            <button
              key={link.id}
              onClick={() => scrollToSection(link.id)}
              className="block w-full text-left px-3 py-2 rounded text-sm font-mono-tech tracking-wider text-lunar-200 hover:text-cyan-accent hover:bg-white/5"
            >
              {link.label}
            </button>
          ))}
          <div className="pt-2 border-t border-white/10 flex justify-between items-center text-xs font-mono-tech text-lunar-400">
            <span>PAIR: {sourceInstrument} × {targetInstrument}</span>
            <span className="text-cyan-accent">STATUS: READY</span>
          </div>
        </div>
      )}
    </header>
  );
};
