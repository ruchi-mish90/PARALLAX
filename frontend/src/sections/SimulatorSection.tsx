import React from 'react';
import { LunarSimulator } from '../components/simulator/LunarSimulator';

export const SimulatorSection: React.FC = () => {
  return (
    <section id="simulator" className="relative py-12 bg-[#111111] border-b border-[#262626]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-left space-y-8">
        


        {/* Interactive Simulator Component */}
        <LunarSimulator />

      </div>
    </section>
  );
};
