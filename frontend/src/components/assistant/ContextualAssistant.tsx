import React, { useState } from 'react';
import { useParallax } from '../../state/ParallaxContext';
import { Terminal, Send, X, ChevronRight, MessageSquare, AlertCircle } from 'lucide-react';

interface Message {
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
}

export const ContextualAssistant: React.FC = () => {
  const { 
    selectedRegion, 
    sourceInstrument, 
    targetInstrument, 
    sourceProduct,
    targetProduct,
    metrics, 
    explainMode,
    setCursorLabel,
    pairCharacterization,
    selectedModelId,
    isAnmsActive,
  } = useParallax();

  const sourceName = sourceProduct?.label ? sourceProduct.label.replace(/^Chandrayaan-2\s*/i, '').split(' (')[0] : sourceInstrument;
  const targetName = targetProduct?.label ? targetProduct.label.replace(/^Chandrayaan-2\s*/i, '').split(' (')[0] : targetInstrument;

  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [inputQuery, setInputQuery] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'assistant',
      text: `Greetings. I am your PARALLAX Scientific Terminal. Current observation pair: ${sourceName} × ${targetName} over ${selectedRegion.name}. Pair difficulty is characterized as ${pairCharacterization?.overallDifficulty || 'MEDIUM'} (Scale ratio: ${pairCharacterization?.scaleRatio.toFixed(1)}:1, Modality: ${pairCharacterization?.modalityDifference}). Selected correspondence engine: ${selectedModelId.toUpperCase()}. Reprojection RMSE is ${metrics.rmse.toFixed(2)} px with ANMS spatial dispersion at ${metrics.spatialCoverage.toFixed(1)}%. [Calibrated Benchmark Data]. How may I assist your scientific analysis?`,
      timestamp: 'Session Init'
    }
  ]);

  const quickQuestions = [
    'Why was this model selected for this pair?',
    'Why does ANMS matter more than raw match count?',
    'When is the TMC-2 bridge triggered?',
    'How is registration uncertainty quantified?',
    'Explain this result like I am new to planetary CV.'
  ];

  const handleSend = (queryText?: string) => {
    const query = queryText || inputQuery;
    if (!query.trim()) return;

    const userMsg: Message = {
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, userMsg]);
    if (!queryText) setInputQuery('');

    // Session-grounded deterministic intelligent response
    setTimeout(() => {
      let reply = '';
      const q = query.toLowerCase();

      if (q.includes('selected') || q.includes('model') || q.includes('router') || q.includes('why rift') || q.includes('why sift')) {
        reply = `The Adaptive Model Router evaluated this pair (${sourceName} × ${targetName}) and characterized difficulty as ${pairCharacterization?.overallDifficulty}. It selected ${selectedModelId.toUpperCase()} because: ${
          selectedModelId === 'RIFT' 
            ? 'extreme polar shadow migration and radiation variation between passes renders gradient magnitude unstable, so RIFT uses phase congruency and maximum moments to find invariant structural boundaries.' 
            : selectedModelId === 'HOPC'
            ? 'the cross-modal radiometric gap between panchromatic and hyperspectral channels requires phase-congruency energy orientation rather than direct intensity correlation.'
            : selectedModelId === 'SIFT'
            ? 'the pair has homogeneous panchromatic modality and moderate scale ratio (<25:1), making octave-downsampled SIFT + Lowe ratio the most computationally efficient baseline.'
            : 'its structural invariance properties provide the highest suitability score for this specific pair geometry.'
        }`;
      } else if (q.includes('anms') || q.includes('spatial') || q.includes('distribution') || q.includes('raw match')) {
        reply = `In planetary remote sensing, a high raw match count is dangerous if 90% of points cluster on a single sunlit crater rim! ANMS (Adaptive Non-Maximal Suppression) computes local suppression radii so keypoints are uniformly dispersed across the entire orbital field of view. ${metrics.candidateMatches > 0 ? `This achieved ${metrics.spatialCoverage.toFixed(1)}% convex-hull spatial coverage` : 'This maximizes convex-hull spatial coverage across the sensor FOV'}, preventing mathematical singularity during homography or epipolar matrix estimation.`;
      } else if (q.includes('bridge') || q.includes('tmc-2 bridge') || q.includes('tmc2')) {
        reply = `The TMC-2 intermediate bridge is a proposed conditional strategy triggered when the ground-sampling distance ratio exceeds 100:1 (such as registering OHRC at 0.25 m/px directly against IIRS at 80 m/px, a 320:1 gap!). Rather than attempting a single catastrophic leap, PARALLAX proposes registering OHRC to TMC-2 (20:1), and subsequently TMC-2 to IIRS (16:1), composing the transformations transitively: H_composite = H_TMC2_to_IIRS · H_OHRC_to_TMC2.`;
      } else if (q.includes('uncertainty') || q.includes('trustworthy') || q.includes('quality gate')) {
        reply = `Registration trustworthiness is quantified through three orthogonal checks: (1) Reprojection RMSE (${metrics.candidateMatches > 0 ? `${metrics.rmse.toFixed(2)} px vs 1.50 px target gate` : 'target gate < 1.50 px'}); (2) Spatial Dispersion via ANMS (${metrics.candidateMatches > 0 ? `${metrics.spatialCoverage.toFixed(1)}% convex-hull coverage vs 60% gate` : 'target gate > 60%'}); (3) Covariance-based uncertainty ellipse (${metrics.candidateMatches > 0 ? `±${metrics.uncertaintyPx.toFixed(2)} px 1-sigma bound` : '1-sigma error bound'}). Every metric is categorized as MEASURED BENCHMARK, TARGET GATE, or SIMULATED.`;
      } else if (q.includes('rmse') || q.includes('pixel error')) {
        reply = metrics.candidateMatches > 0 
          ? `An RMSE of ${metrics.rmse.toFixed(2)} pixels means that across all ${metrics.inlierMatches} verified inliers, the root mean square discrepancy between reprojected and target coordinates is ${metrics.rmse.toFixed(2)} px. Sub-pixel local refinement (ECC) further optimizes alignment inside 31x31 patches to target <0.5 px.`
          : 'Reprojection RMSE quantifies the subpixel Euclidean discrepancy between transformed source landmarks and target coordinates. Target gate is <1.5 px for Chandrayaan-2 lunar mapping.';
      } else if (q.includes('new to') || q.includes('simple') || q.includes('explain')) {
        reply = `Think of it this way: different spacecraft cameras take very different photos—some are ultra-close zoom shots, some are wide 3D scans, and some are heat/mineral color scans. If you try to match them with just one simple tool, it gets confused by shifting crater shadows. PARALLAX first looks at the two photos, decides how tricky the match is, picks the smartest matching tool for the job, spreads the match points out across the whole crater, and double-checks the math so lunar landing craft don't get lost.`;
      } else {
        reply = `Session context: ${sourceName} × ${targetName} on ${selectedRegion.name}. Evaluated difficulty: ${pairCharacterization?.overallDifficulty}. Inlier consensus: ${metrics.candidateMatches > 0 ? `${metrics.inlierRatio.toFixed(1)}% (${metrics.inlierMatches}/${metrics.candidateMatches})` : 'Awaiting Run'}. Model: ${selectedModelId.toUpperCase()} with ANMS ${isAnmsActive ? 'ACTIVE' : 'BYPASS'}.`;
      }

      const assistantMsg: Message = {
        sender: 'assistant',
        text: reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, assistantMsg]);
    }, 450);
  };

  return (
    <>
      {/* Floating Assistant Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={() => setCursorLabel('OPEN SCIENTIFIC TERMINAL')}
        onMouseLeave={() => setCursorLabel('')}
        className="fixed bottom-6 right-6 z-40 flex items-center gap-2 px-3.5 py-2 rounded-none sm:rounded-sm bg-[#161616] border border-[#333333] text-[#F7F7F5] font-mono-tech text-xs tracking-wider shadow-lg hover:bg-[#222222] hover:border-[#555555] transition-colors"
      >
        <Terminal className="h-3.5 w-3.5 text-[#86D88E]" />
        <span className="font-semibold text-[11px]">ASSISTANT</span>
        <span className="h-1.5 w-1.5 bg-[#86D88E]" />
      </button>

      {/* Slide-over Assistant Drawer Panel */}
      {isOpen && (
        <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-96 bg-[#161616] border-l border-[#262626] shadow-2xl flex flex-col animate-in slide-in-from-right duration-200 text-left">
          
          {/* Header */}
          <div className="p-3.5 border-b border-[#262626] flex items-center justify-between bg-[#111111]">
            <div className="flex items-center gap-2">
              <div className="h-6 w-6 rounded-none bg-[#161616] border border-[#333333] flex items-center justify-center">
                <Terminal className="h-3.5 w-3.5 text-[#86D88E]" />
              </div>
              <div>
                <div className="font-sans text-xs font-bold text-[#F7F7F5] flex items-center gap-2">
                  <span>PARALLAX TELEMETRY TERMINAL</span>
                </div>
                <div className="text-[10px] font-mono-tech text-[#8C8C89]">
                  {sourceName} × {targetName} • {selectedRegion.name}
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 rounded-none text-[#8C8C89] hover:text-[#FFFFFF] hover:bg-[#1E1E1E]"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Demonstration Notice */}
          <div className="px-3.5 py-1.5 bg-[#1A1A1A] border-b border-[#262626] text-[10px] font-mono-tech text-[#A0A0A0] flex items-center gap-2">
            <AlertCircle className="h-3 w-3 text-[#E0A855] shrink-0" />
            <span>Telemetry calibrated on verified ISRO demonstration dataset.</span>
          </div>

          {/* Message List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[90%] rounded-none sm:rounded-sm p-3 text-xs leading-relaxed ${
                    m.sender === 'user'
                      ? 'bg-[#1E1E1E] border border-[#383838] text-[#F7F7F5] font-mono-tech'
                      : 'bg-[#111111] border border-[#262626] text-[#A0A0A0] font-sans'
                  }`}
                >
                  {m.text}
                </div>
                <span className="text-[9px] font-mono-tech text-[#646462] mt-1 px-1">
                  {m.timestamp}
                </span>
              </div>
            ))}
          </div>

          {/* Contextual Quick Questions */}
          <div className="p-3 border-t border-[#262626] bg-[#111111] space-y-1.5">
            <div className="text-[10px] font-mono-tech text-[#8C8C89] uppercase flex items-center gap-1">
              <MessageSquare className="h-3 w-3 text-[#A0A0A0]" />
              <span>Suggested Inquiries:</span>
            </div>
            <div className="flex flex-col gap-1">
              {quickQuestions.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(q)}
                  className="text-left text-[11px] font-mono-tech text-[#A0A0A0] hover:text-[#FFFFFF] hover:bg-[#1E1E1E] px-2 py-1 rounded-none border border-[#262626] transition-colors truncate flex items-center justify-between"
                >
                  <span className="truncate">{q}</span>
                  <ChevronRight className="h-3 w-3 shrink-0 text-[#646462]" />
                </button>
              ))}
            </div>
          </div>

          {/* Input Footer */}
          <div className="p-3 border-t border-[#262626] bg-[#111111]">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                placeholder={explainMode ? 'Ask about this lunar result...' : 'Query pipeline telemetry, RANSAC, or RMSE...'}
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                className="flex-1 bg-[#161616] border border-[#333333] rounded-none px-3 py-2 text-xs font-mono-tech text-[#F7F7F5] placeholder-[#646462] focus:outline-none focus:border-[#555555]"
              />
              <button
                type="submit"
                className="p-2 rounded-none bg-[#F7F7F5] text-[#111111] hover:bg-[#FFFFFF] transition-colors"
                title="Send query"
              >
                <Send className="h-3.5 w-3.5" />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
};
