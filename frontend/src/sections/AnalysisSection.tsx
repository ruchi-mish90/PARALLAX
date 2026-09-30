import React from 'react';
import { useParallax } from '../state/ParallaxContext';
import { MetricCards } from '../components/analysis/MetricCards';
import { HomographyDisplay } from '../components/analysis/HomographyDisplay';
import { ErrorPlot } from '../components/analysis/ErrorPlot';
import { BarChart2, ShieldAlert } from 'lucide-react';

export const AnalysisSection: React.FC = () => {
  const { explainMode } = useParallax();

  return (
    <section id="analysis" className="relative py-12 bg-[#111111] border-b border-[#262626]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-left space-y-8">
        


        {/* Primary Metric Gauges */}
        <MetricCards />

        {/* Mathematical Matrix & Residual Error Plots */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-2">
          <HomographyDisplay />
          <ErrorPlot />
        </div>

      </div>
    </section>
  );
};
