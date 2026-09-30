import React, { useState } from 'react';
import { useParallax } from '../../state/ParallaxContext';
import { LunarImageProduct } from '../../types/correspondence';
import { 
  ArrowLeftRight, 
  RotateCcw, 
  Play, 
  Sparkles, 
  Camera, 
  Layers, 
  AlertTriangle, 
  CheckCircle2, 
  Info,
  Calendar,
  Sun,
  Maximize,
  Compass,
  FolderOpen
} from 'lucide-react';

export const PairSelectionControlArea: React.FC = () => {
  const {
    sourceProduct,
    setSourceProduct,
    targetProduct,
    setTargetProduct,
    availableProducts,
    swapInstruments,
    resetImagePair,
    pairCharacterization,
    selectedModel,
    modelCandidates,
    runCorrespondence,
    isProcessing,
    pipelineProgress,
    useTmcBridge,
    toggleTmcBridge,
    isObservable,
    observabilityReason,
    preprocessingAuto,
    togglePreprocessingAuto,
    claheEnabled,
    toggleClaheEnabled,
    setCursorLabel,
  } = useParallax();

  const [previewZoomModal, setPreviewZoomModal] = useState<LunarImageProduct | null>(null);

  // Group products by instrument for the select menu
  const ohrcProducts = availableProducts.filter(p => p.instrument === 'OHRC');
  const tmcProducts = availableProducts.filter(p => p.instrument === 'TMC-2');
  const iirsProducts = availableProducts.filter(p => p.instrument === 'IIRS');
  const refProducts = availableProducts.filter(p => p.instrument !== 'OHRC' && p.instrument !== 'TMC-2' && p.instrument !== 'IIRS');

  const getDifficultyColor = (diff: string) => {
    if (diff === 'Easy') return 'text-[#86D88E] border-[#2E5E32] bg-[#1A2E1C]';
    if (diff === 'Medium') return 'text-[#E0A855] border-[#5E4218] bg-[#2E2211]';
    return 'text-[#E57373] border-[#5E2626] bg-[#2E1616]';
  };

  return (
    <div className="space-y-4 font-sans text-left">
      {/* ─── 3-COLUMN TOP CONTROL AREA ─── */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        
        {/* ═══ COLUMN 1: SOURCE A (4 Cols) ═══ */}
        <div className="lg:col-span-4 rounded-none sm:rounded-sm p-4 border border-[#262626] bg-[#161616] flex flex-col justify-between space-y-3">
          {/* Header */}
          <div className="flex items-center justify-between pb-2 border-b border-[#262626]">
            <div className="flex items-center gap-2">
              <Camera className="h-4 w-4 text-[#A0A0A0]" />
              <span className="font-mono-tech text-xs font-bold text-[#F7F7F5] tracking-wider uppercase">
                SOURCE A
              </span>
            </div>
            <span className="px-2 py-0.5 rounded-none text-[10px] font-mono-tech bg-[#111111] border border-[#262626] text-[#A0A0A0] font-semibold">
              {sourceProduct.id.startsWith('custom-') ? 'CUSTOM' : sourceProduct.instrument} • {sourceProduct.gsdDisplay}
            </span>
          </div>

          {/* Product Dropdown Selector + Local File Browser */}
          <div className="space-y-1">
            <label className="text-[10px] font-mono-tech text-[#8C8C89] uppercase tracking-wider flex items-center justify-between">
              <span>SELECT OBSERVATION / PRODUCT:</span>
              <span className="text-[#F7F7F5] font-semibold truncate max-w-[160px]" title={sourceProduct.label}>
                {sourceProduct.label ? sourceProduct.label.replace(/^Chandrayaan-2\s*/i, '').replace(/^(OHRC|TMC-2|IIRS)\s*/i, '').split(' (')[0] : sourceProduct.regionId.toUpperCase()}
              </span>
            </label>
            <div className="flex items-center gap-1.5">
              <select
                value={sourceProduct.id}
                onChange={(e) => {
                  const found = availableProducts.find(p => p.id === e.target.value);
                  if (found) setSourceProduct(found);
                }}
                className="flex-1 min-w-0 bg-[#111111] border border-[#333333] rounded-none px-2.5 py-1.5 text-xs font-mono-tech text-[#F7F7F5] focus:outline-none focus:border-[#555555] transition-colors"
              >
                {sourceProduct.id.startsWith('custom-') && (
                  <optgroup label="Inserted Local Image">
                    <option value={sourceProduct.id}>
                      {sourceProduct.label} (Custom Image)
                    </option>
                  </optgroup>
                )}
                <optgroup label="Chandrayaan-2 OHRC (0.25 - 0.32 m/px)">
                  {ohrcProducts.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.label.replace(/^OHRC\s*/i, '')} ({p.gsdDisplay})
                    </option>
                  ))}
                </optgroup>
                <optgroup label="Chandrayaan-2 TMC-2 (5.0 m/px)">
                  {tmcProducts.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.label.replace(/^TMC-2\s*/i, '')} ({p.gsdDisplay})
                    </option>
                  ))}
                </optgroup>
                <optgroup label="Chandrayaan-2 IIRS (80 m/px)">
                  {iirsProducts.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.label.replace(/^IIRS\s*/i, '')} ({p.gsdDisplay})
                    </option>
                  ))}
                </optgroup>
                <optgroup label="Reference Lunar Baselines">
                  {refProducts.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.label} ({p.gsdDisplay})
                    </option>
                  ))}
                </optgroup>
              </select>

              <label 
                className="px-2 py-1.5 border border-[#333333] bg-[#1a1a1a] hover:bg-[#252525] text-[10px] font-mono-tech text-[#F7F7F5] cursor-pointer flex items-center gap-1 transition-colors flex-shrink-0"
                title="Browse and select image from any folder on your computer"
              >
                <FolderOpen className="h-3 w-3 text-[#A0A0A0]" />
                <span className="hidden sm:inline">BROWSE</span>
                <input 
                  type="file" 
                  accept="image/*,.tif,.tiff,.png,.jpg,.jpeg" 
                  className="hidden" 
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      const url = URL.createObjectURL(file);
                      setSourceProduct({
                        ...sourceProduct,
                        id: `custom-src-${Date.now()}`,
                        productId: file.name,
                        label: file.name,
                        instrument: 'Custom',
                        instrumentLabel: 'Custom Inserted Image',
                        thumbnailUrl: url,
                        sensorDescription: `Local custom image: ${file.name}`
                      });
                    }
                  }} 
                />
              </label>
            </div>
          </div>

          {/* Thumbnail Preview with HUD Overlay */}
          <div className="relative rounded-none overflow-hidden border border-[#262626] aspect-[16/9] group bg-[#111111]">
            <img
              src={sourceProduct.thumbnailUrl}
              alt={sourceProduct.label}
              className="w-full h-full object-cover transition-transform duration-200"
            />
            {/* Corner Badges */}
            <div className="absolute top-2 left-2 px-1.5 py-0.5 rounded-none text-[9px] font-mono-tech bg-[#111111]/90 border border-[#262626] text-[#F7F7F5]">
              GSD: {sourceProduct.gsdDisplay}
            </div>
            {sourceProduct.orbitNumber && (
              <div className="absolute top-2 right-2 px-1.5 py-0.5 rounded-none text-[9px] font-mono-tech bg-[#111111]/90 border border-[#262626] text-[#A0A0A0]">
                ORBIT #{sourceProduct.orbitNumber}
              </div>
            )}
            <div 
              className="absolute bottom-2 left-2 px-2 py-0.5 rounded-none text-[9px] font-mono-tech bg-[#111111]/95 text-[#F7F7F5] font-semibold truncate max-w-[85%] border border-[#262626]"
              title={sourceProduct.label || sourceProduct.productId}
            >
              {sourceProduct.label ? sourceProduct.label.replace(/^Chandrayaan-2\s*/i, '').replace(/^OHRC\s*/i, '') : sourceProduct.productId}
            </div>
            <button
              onClick={() => setPreviewZoomModal(sourceProduct)}
              className="absolute bottom-2 right-2 p-1 rounded-none bg-[#111111]/90 text-[#F7F7F5] hover:text-[#FFFFFF] border border-[#262626] opacity-0 group-hover:opacity-100 transition-opacity"
              title="Inspect Frame"
            >
              <Maximize className="h-3 w-3" />
            </button>
          </div>

          {/* Metadata Summary */}
          <div className="grid grid-cols-2 gap-2 text-[10px] font-mono-tech pt-1">
            <div className="p-2 rounded-none bg-[#111111] border border-[#262626] space-y-0.5">
              <span className="text-[#646462] uppercase flex items-center gap-1">
                <Layers className="h-3 w-3 text-[#A0A0A0]" /> MODALITY
              </span>
              <div className="text-[#A0A0A0] font-semibold truncate" title={sourceProduct.modality}>
                {sourceProduct.modality.split('(')[0]}
              </div>
            </div>

            <div className="p-2 rounded-none bg-[#111111] border border-[#262626] space-y-0.5">
              <span className="text-[#646462] uppercase flex items-center gap-1">
                <Sun className="h-3 w-3 text-[#E0A855]" /> SOLAR EL / AZ
              </span>
              <div className="text-[#A0A0A0] font-semibold">
                {sourceProduct.solarElevation}° / {sourceProduct.solarAzimuth}°
              </div>
            </div>

            <div className="p-2 rounded-none bg-[#111111] border border-[#262626] space-y-0.5">
              <span className="text-[#646462] uppercase flex items-center gap-1">
                <Calendar className="h-3 w-3 text-[#646462]" /> ACQUIRED
              </span>
              <div className="text-[#8C8C89] truncate" title={sourceProduct.acquisitionDate}>
                {sourceProduct.acquisitionDate.split(' ')[0]}
              </div>
            </div>

            <div className="p-2 rounded-none bg-[#111111] border border-[#262626] space-y-0.5">
              <span className="text-[#646462] uppercase flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3 text-[#86D88E]" /> VALID PIXELS
              </span>
              <div className="text-[#86D88E] font-semibold">
                {sourceProduct.validPixelRatio}%
              </div>
            </div>
          </div>
        </div>

        {/* ═══ COLUMN 2: PAIR / ADAPTIVE ROUTER (4 Cols) ═══ */}
        <div className="lg:col-span-4 rounded-none sm:rounded-sm p-4 border border-[#262626] bg-[#161616] flex flex-col justify-between space-y-3">
          {/* Header Controls (Swap & Reset) */}
          <div className="flex items-center justify-between pb-2 border-b border-[#262626]">
            <div className="font-mono-tech text-xs font-bold text-[#F7F7F5] uppercase tracking-wider flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-[#A0A0A0]" />
              <span>PAIR ANALYSIS & ROUTER</span>
            </div>
            
            <div className="flex items-center gap-1.5">
              <button
                onClick={swapInstruments}
                onMouseEnter={() => setCursorLabel('SWAP SOURCE AND TARGET')}
                onMouseLeave={() => setCursorLabel('')}
                className="flex items-center gap-1 px-2.5 py-1 rounded-none bg-[#111111] border border-[#262626] hover:border-[#383838] text-[#A0A0A0] hover:text-[#FFFFFF] text-[10px] font-mono-tech transition-colors"
                title="Swap Image A and Image B"
              >
                <ArrowLeftRight className="h-3 w-3 text-[#A0A0A0]" />
                <span>SWAP</span>
              </button>

              <button
                onClick={resetImagePair}
                onMouseEnter={() => setCursorLabel('RESET DEFAULT PAIR')}
                onMouseLeave={() => setCursorLabel('')}
                className="p-1.5 rounded-none bg-[#111111] border border-[#262626] hover:border-[#383838] text-[#8C8C89] hover:text-[#FFFFFF] transition-colors"
                title="Reset Image Pair & Models"
              >
                <RotateCcw className="h-3 w-3" />
              </button>
            </div>
          </div>

          {/* Pair Physical Diagnostic Summary */}
          <div className="space-y-2 font-mono-tech">
            <div className="flex items-center justify-between p-2.5 rounded-none bg-[#111111] border border-[#262626]">
              <div className="space-y-0.5 text-left min-w-0 flex-1 mr-2">
                <span className="text-[10px] text-[#8C8C89] uppercase">ACTIVE PAIR:</span>
                <div className="text-xs font-bold text-[#F7F7F5] truncate max-w-[260px]" title={`${sourceProduct.label} ↔ ${targetProduct.label}`}>
                  {sourceProduct.label ? sourceProduct.label.replace(/^Chandrayaan-2\s*/i, '').replace(/^(OHRC|TMC-2|IIRS)\s*/i, '').split(' (')[0] : sourceProduct.productId} ↔ {targetProduct.label ? targetProduct.label.replace(/^Chandrayaan-2\s*/i, '').replace(/^(OHRC|TMC-2|IIRS)\s*/i, '').split(' (')[0] : targetProduct.productId}
                </div>
              </div>
              <span className={`px-2.5 py-0.5 rounded-none text-xs font-semibold uppercase border shrink-0 ${getDifficultyColor(pairCharacterization.overallDifficulty)}`}>
                {pairCharacterization.overallDifficulty}
              </span>
            </div>

            {/* Micro Gauge Metrics */}
            <div className="grid grid-cols-3 gap-1.5 text-center text-[10px]">
              <div className="p-2 rounded-none bg-[#111111] border border-[#262626] space-y-0.5">
                <span className="text-[#646462] uppercase block">SCALE RATIO</span>
                <span className="text-[#F7F7F5] font-bold text-xs">{pairCharacterization.scaleRatioDisplay}</span>
              </div>
              <div className="p-2 rounded-none bg-[#111111] border border-[#262626] space-y-0.5">
                <span className="text-[#646462] uppercase block">MODALITY Δ</span>
                <span className="text-[#E0A855] font-bold text-xs">{pairCharacterization.modalityDifference}</span>
              </div>
              <div className="p-2 rounded-none bg-[#111111] border border-[#262626] space-y-0.5">
                <span className="text-[#646462] uppercase block">OVERLAP EST</span>
                <span className="text-[#86D88E] font-bold text-xs">{pairCharacterization.estimatedOverlap}%</span>
              </div>
            </div>
          </div>

          {/* Recommended Strategy Box */}
          <div className="p-3 rounded-none bg-[#111111] border border-[#262626] space-y-2 text-left font-mono-tech">
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-[#86D88E] font-semibold uppercase flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 bg-[#86D88E]" />
                RECOMMENDED STRATEGY
              </span>
              <span className="text-[#F7F7F5] font-semibold bg-[#161616] px-2 py-0.5 rounded-none text-[10px] border border-[#262626]">
                SCORE: {selectedModel.suitabilityScore}/100
              </span>
            </div>

            <div className="text-[#F7F7F5] font-sans font-bold text-sm">
              {selectedModel.name}
            </div>

            <p className="text-[11px] text-[#8C8C89] font-sans leading-relaxed">
              {selectedModel.selectionRationale}
            </p>

            {/* Quick Rank Snapshot */}
            <div className="pt-1 border-t border-[#262626] flex items-center justify-between text-[10px] text-[#646462]">
              <span>RANKED: 1. {modelCandidates[0]?.name.split('(')[0]} ({modelCandidates[0]?.suitabilityScore || 0})</span>
              <span>2. {modelCandidates[1]?.name.split('(')[0]} ({modelCandidates[1]?.suitabilityScore || 0})</span>
            </div>
          </div>

          {/* Conditional Bridge Alert if Scale > 100x */}
          {pairCharacterization.suggestTmcBridge && (
            <div className="p-2.5 rounded-none bg-[#2E2211]/50 border border-[#5E4218] flex items-start gap-2 text-left">
              <AlertTriangle className="h-4 w-4 text-[#E0A855] shrink-0 mt-0.5" />
              <div className="space-y-1 text-[11px] font-mono-tech">
                <div className="text-[#E0A855] font-bold">PROPOSED TMC-2 INTERMEDIATE BRIDGE</div>
                <p className="text-[#A0A0A0] font-sans text-[10px] leading-tight">
                  Extreme {pairCharacterization.scaleRatioDisplay} scale gap. Routing via TMC-2 (20:1 + 16:1) is proposed.
                </p>
                <button
                  onClick={toggleTmcBridge}
                  className={`px-2 py-0.5 rounded-none text-[9px] font-bold border transition-colors ${
                    useTmcBridge 
                      ? 'bg-[#E0A855] text-[#111111] border-[#E0A855]' 
                      : 'bg-[#111111] text-[#E0A855] border-[#5E4218] hover:bg-[#1E1E1E]'
                  }`}
                >
                  {useTmcBridge ? 'BRIDGE ACTIVE: OHRC → TMC-2 → IIRS' : 'ENABLE CONDITIONAL BRIDGE'}
                </button>
              </div>
            </div>
          )}

          {/* 7.2 Observability / Geographic Overlap Gate */}
          <div className={`p-2.5 rounded-none border text-left font-mono-tech text-xs space-y-1 ${
            isObservable 
              ? 'bg-[#1A2E1C]/40 border-[#2E5E32] text-[#86D88E]' 
              : 'bg-[#2E1616]/60 border-[#5E2626] text-[#E57373]'
          }`}>
            <div className="flex items-center justify-between text-[10px] font-bold tracking-wider uppercase">
              <span className="flex items-center gap-1.5">
                {isObservable ? <CheckCircle2 className="h-3.5 w-3.5 text-[#86D88E]" /> : <AlertTriangle className="h-3.5 w-3.5 text-[#E57373]" />}
                {isObservable ? 'GEOMETRIC OBSERVABILITY' : 'REGISTRATION BLOCKED'}
              </span>
              <span>{isObservable ? 'PASSED' : 'DISJOINT'}</span>
            </div>

            {isObservable ? (
              <div className="grid grid-cols-2 gap-1 text-[9.5px] text-[#A0A0A0] pt-0.5">
                <span className="text-[#86D88E]">✓ Geographic overlap</span>
                <span className="text-[#86D88E]">✓ Valid pixels &gt; 90%</span>
                <span className="text-[#86D88E]">✓ Observable area</span>
                <span className="text-[#86D88E]">✓ Registration candidate</span>
              </div>
            ) : (
              <p className="text-[10px] font-sans text-[#E57373] leading-tight pt-0.5">
                {observabilityReason} No valid 2-D geographic ground footprint overlap.
              </p>
            )}
          </div>

          {/* 7.3 Compact Preprocessing Controls */}
          <div className="p-2.5 rounded-none bg-[#111111] border border-[#262626] space-y-1.5 text-left font-mono-tech text-xs">
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-[#8C8C89] uppercase tracking-wider font-semibold">PREPROCESSING PIPELINE:</span>
              <span className="text-[#86D88E]">{preprocessingAuto ? 'AUTO' : 'MANUAL'}</span>
            </div>

            <div className="flex items-center justify-between text-[8.5px] text-[#777774] border-b border-[#262626] pb-1">
              <span>RAW</span>
              <span>→</span>
              <span>NORM</span>
              <span>→</span>
              <span>NLM</span>
              <span>→</span>
              <span>CLAHE</span>
              <span>→</span>
              <span className="text-[#86D88E] font-bold">READY</span>
            </div>

            <div className="flex items-center justify-between gap-2 pt-0.5">
              <button
                onClick={togglePreprocessingAuto}
                className={`px-2 py-0.5 text-[9.5px] border transition-colors ${
                  preprocessingAuto ? 'bg-[#1C1C1C] border-[#86D88E] text-[#86D88E]' : 'bg-[#111111] border-[#333333] text-[#8C8C89]'
                }`}
              >
                PREPROCESS: {preprocessingAuto ? 'AUTO' : 'CUSTOM'}
              </button>

              <button
                onClick={toggleClaheEnabled}
                className={`px-2 py-0.5 text-[9.5px] border transition-colors ${
                  claheEnabled ? 'bg-[#1C1C1C] border-[#E0A855] text-[#E0A855]' : 'bg-[#111111] border-[#333333] text-[#8C8C89]'
                }`}
              >
                CLAHE: {claheEnabled ? 'ON' : 'OFF'}
              </button>
            </div>
          </div>

          {/* Primary Action Button: RUN REGISTRATION PIPELINE */}
          <div className="pt-1">
            <button
              onClick={runCorrespondence}
              disabled={isProcessing || !isObservable}
              onMouseEnter={() => setCursorLabel(isObservable ? 'EXECUTE ADAPTIVE REGISTRATION' : 'REGISTRATION BLOCKED')}
              onMouseLeave={() => setCursorLabel('')}
              className={`w-full py-2.5 px-4 rounded-none font-mono-tech text-xs tracking-wider font-bold flex items-center justify-center gap-2 transition-colors ${
                !isObservable
                  ? 'bg-[#222222] text-[#666666] border border-[#333333] cursor-not-allowed'
                  : isProcessing
                  ? 'bg-[#222222] text-[#86D88E] border border-[#2E5E32] cursor-wait'
                  : 'bg-[#F7F7F5] text-[#111111] hover:bg-[#FFFFFF]'
              }`}
            >
              {!isObservable ? (
                <span>REGISTRATION BLOCKED (NO OVERLAP)</span>
              ) : isProcessing ? (
                <>
                  <div className="h-3 w-3 border border-[#86D88E] border-t-transparent rounded-full animate-spin" />
                  <span>EXECUTING STAGE: {pipelineProgress}%</span>
                </>
              ) : (
                <>
                  <Play className="h-3 w-3 fill-current" />
                  <span>RUN REGISTRATION PIPELINE</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* ═══ COLUMN 3: SOURCE B (4 Cols) ═══ */}
        <div className="lg:col-span-4 rounded-none sm:rounded-sm p-4 border border-[#262626] bg-[#161616] flex flex-col justify-between space-y-3">
          {/* Header */}
          <div className="flex items-center justify-between pb-2 border-b border-[#262626]">
            <div className="flex items-center gap-2">
              <Compass className="h-4 w-4 text-[#A0A0A0]" />
              <span className="font-mono-tech text-xs font-bold text-[#F7F7F5] tracking-wider uppercase">
                SOURCE B
              </span>
            </div>
            <span className="px-2 py-0.5 rounded-none text-[10px] font-mono-tech bg-[#111111] border border-[#262626] text-[#A0A0A0] font-semibold">
              {targetProduct.id.startsWith('custom-') ? 'CUSTOM' : targetProduct.instrument} • {targetProduct.gsdDisplay}
            </span>
          </div>

          {/* Product Dropdown Selector + Local File Browser */}
          <div className="space-y-1">
            <label className="text-[10px] font-mono-tech text-[#8C8C89] uppercase tracking-wider flex items-center justify-between">
              <span>SELECT OBSERVATION / PRODUCT:</span>
              <span className="text-[#F7F7F5] font-semibold truncate max-w-[160px]" title={targetProduct.label}>
                {targetProduct.label ? targetProduct.label.replace(/^Chandrayaan-2\s*/i, '').replace(/^(OHRC|TMC-2|IIRS)\s*/i, '').split(' (')[0] : targetProduct.regionId.toUpperCase()}
              </span>
            </label>
            <div className="flex items-center gap-1.5">
              <select
                value={targetProduct.id}
                onChange={(e) => {
                  const found = availableProducts.find(p => p.id === e.target.value);
                  if (found) setTargetProduct(found);
                }}
                className="flex-1 min-w-0 bg-[#111111] border border-[#333333] rounded-none px-2.5 py-1.5 text-xs font-mono-tech text-[#F7F7F5] focus:outline-none focus:border-[#555555] transition-colors"
              >
                {targetProduct.id.startsWith('custom-') && (
                  <optgroup label="Inserted Local Image">
                    <option value={targetProduct.id}>
                      {targetProduct.label} (Custom Image)
                    </option>
                  </optgroup>
                )}
                <optgroup label="Chandrayaan-2 TMC-2 (5.0 m/px)">
                  {tmcProducts.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.label.replace(/^TMC-2\s*/i, '')} ({p.gsdDisplay})
                    </option>
                  ))}
                </optgroup>
                <optgroup label="Chandrayaan-2 OHRC (0.25 - 0.32 m/px)">
                  {ohrcProducts.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.label.replace(/^OHRC\s*/i, '')} ({p.gsdDisplay})
                    </option>
                  ))}
                </optgroup>
                <optgroup label="Chandrayaan-2 IIRS (80 m/px)">
                  {iirsProducts.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.label.replace(/^IIRS\s*/i, '')} ({p.gsdDisplay})
                    </option>
                  ))}
                </optgroup>
                <optgroup label="Reference Lunar Baselines">
                  {refProducts.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.label} ({p.gsdDisplay})
                    </option>
                  ))}
                </optgroup>
              </select>

              <label 
                className="px-2 py-1.5 border border-[#333333] bg-[#1a1a1a] hover:bg-[#252525] text-[10px] font-mono-tech text-[#F7F7F5] cursor-pointer flex items-center gap-1 transition-colors flex-shrink-0"
                title="Browse and select image from any folder on your computer"
              >
                <FolderOpen className="h-3 w-3 text-[#A0A0A0]" />
                <span className="hidden sm:inline">BROWSE</span>
                <input 
                  type="file" 
                  accept="image/*,.tif,.tiff,.png,.jpg,.jpeg" 
                  className="hidden" 
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      const url = URL.createObjectURL(file);
                      setTargetProduct({
                        ...targetProduct,
                        id: `custom-tgt-${Date.now()}`,
                        productId: file.name,
                        label: file.name,
                        instrument: 'Custom',
                        instrumentLabel: 'Custom Inserted Image',
                        thumbnailUrl: url,
                        sensorDescription: `Local custom image: ${file.name}`
                      });
                    }
                  }} 
                />
              </label>
            </div>
          </div>

          {/* Thumbnail Preview with HUD Overlay */}
          <div className="relative rounded-none overflow-hidden border border-[#262626] aspect-[16/9] group bg-[#111111]">
            <img
              src={targetProduct.thumbnailUrl}
              alt={targetProduct.label}
              className="w-full h-full object-cover transition-transform duration-200"
            />
            {/* Corner Badges */}
            <div className="absolute top-2 left-2 px-1.5 py-0.5 rounded-none text-[9px] font-mono-tech bg-[#111111]/90 border border-[#262626] text-[#F7F7F5]">
              GSD: {targetProduct.gsdDisplay}
            </div>
            {targetProduct.orbitNumber && (
              <div className="absolute top-2 right-2 px-1.5 py-0.5 rounded-none text-[9px] font-mono-tech bg-[#111111]/90 border border-[#262626] text-[#A0A0A0]">
                ORBIT #{targetProduct.orbitNumber}
              </div>
            )}
            <div 
              className="absolute bottom-2 left-2 px-2 py-0.5 rounded-none text-[9px] font-mono-tech bg-[#111111]/95 text-[#F7F7F5] font-semibold truncate max-w-[85%] border border-[#262626]"
              title={targetProduct.label || targetProduct.productId}
            >
              {targetProduct.label ? targetProduct.label.replace(/^Chandrayaan-2\s*/i, '').replace(/^TMC-2\s*/i, '') : targetProduct.productId}
            </div>
            <button
              onClick={() => setPreviewZoomModal(targetProduct)}
              className="absolute bottom-2 right-2 p-1 rounded-none bg-[#111111]/90 text-[#F7F7F5] hover:text-[#FFFFFF] border border-[#262626] opacity-0 group-hover:opacity-100 transition-opacity"
              title="Inspect Frame"
            >
              <Maximize className="h-3 w-3" />
            </button>
          </div>

          {/* Metadata Summary */}
          <div className="grid grid-cols-2 gap-2 text-[10px] font-mono-tech pt-1">
            <div className="p-2 rounded-none bg-[#111111] border border-[#262626] space-y-0.5">
              <span className="text-[#646462] uppercase flex items-center gap-1">
                <Layers className="h-3 w-3 text-[#A0A0A0]" /> MODALITY
              </span>
              <div className="text-[#A0A0A0] font-semibold truncate" title={targetProduct.modality}>
                {targetProduct.modality.split('(')[0]}
              </div>
            </div>

            <div className="p-2 rounded-none bg-[#111111] border border-[#262626] space-y-0.5">
              <span className="text-[#646462] uppercase flex items-center gap-1">
                <Sun className="h-3 w-3 text-[#E0A855]" /> SOLAR EL / AZ
              </span>
              <div className="text-[#A0A0A0] font-semibold">
                {targetProduct.solarElevation}° / {targetProduct.solarAzimuth}°
              </div>
            </div>

            <div className="p-2 rounded-none bg-[#111111] border border-[#262626] space-y-0.5">
              <span className="text-[#646462] uppercase flex items-center gap-1">
                <Calendar className="h-3 w-3 text-[#646462]" /> ACQUIRED
              </span>
              <div className="text-[#8C8C89] truncate" title={targetProduct.acquisitionDate}>
                {targetProduct.acquisitionDate.split(' ')[0]}
              </div>
            </div>

            <div className="p-2 rounded-none bg-[#111111] border border-[#262626] space-y-0.5">
              <span className="text-[#646462] uppercase flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3 text-[#86D88E]" /> VALID PIXELS
              </span>
              <div className="text-[#86D88E] font-semibold">
                {targetProduct.validPixelRatio}%
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Frame Inspection Modal */}
      {previewZoomModal && (
        <div 
          onClick={() => setPreviewZoomModal(null)}
          className="fixed inset-0 z-50 bg-[#111111]/90 flex items-center justify-center p-4 animate-in fade-in duration-150"
        >
          <div 
            onClick={(e) => e.stopPropagation()}
            className="rounded-none sm:rounded-sm p-6 border border-[#333333] bg-[#161616] max-w-2xl w-full space-y-4 shadow-2xl"
          >
            <div className="flex items-center justify-between pb-3 border-b border-[#262626] font-mono-tech text-xs">
              <div className="flex items-center gap-2">
                <Info className="h-4 w-4 text-[#A0A0A0]" />
                <span className="text-[#F7F7F5] font-bold">{previewZoomModal.productId}</span>
              </div>
              <button 
                onClick={() => setPreviewZoomModal(null)}
                className="px-2.5 py-1 rounded-none bg-[#111111] border border-[#262626] text-[#A0A0A0] hover:text-[#FFFFFF]"
              >
                CLOSE [ESC]
              </button>
            </div>

            <div className="rounded-none overflow-hidden border border-[#262626] aspect-[16/9] relative">
              <img 
                src={previewZoomModal.thumbnailUrl} 
                alt={previewZoomModal.label} 
                className="w-full h-full object-cover"
              />
              <div className="absolute bottom-3 left-3 px-3 py-1 rounded-none bg-[#111111]/90 text-xs font-mono-tech border border-[#262626] text-[#F7F7F5]">
                {previewZoomModal.instrumentLabel} • {previewZoomModal.gsdDisplay}
              </div>
            </div>

            <div className="text-xs text-[#8C8C89] font-sans leading-relaxed">
              {previewZoomModal.sensorDescription}
            </div>

            <div className="grid grid-cols-3 gap-2 font-mono-tech text-[11px] pt-2 border-t border-[#262626]">
              <div>
                <span className="text-[#646462]">CHANNEL:</span>
                <div className="text-[#F7F7F5] font-semibold">{previewZoomModal.channelInfo || 'Broadband'}</div>
              </div>
              <div>
                <span className="text-[#646462]">SUN ELEVATION:</span>
                <div className="text-[#F7F7F5] font-semibold">{previewZoomModal.solarElevation}°</div>
              </div>
              <div>
                <span className="text-[#646462]">VALID DATA:</span>
                <div className="text-[#86D88E] font-semibold">{previewZoomModal.validPixelRatio}%</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
