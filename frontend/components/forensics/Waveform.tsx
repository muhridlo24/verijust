import { Activity } from "lucide-react";

interface WaveformProps {
  duration: string;
  segments: { isSpoof: boolean; intensity: number }[];
}

export function Waveform({ duration, segments }: WaveformProps) {
  return (
    <div className="bg-neutral-900/30 border border-neutral-800 rounded-2xl p-6">
      <div className="flex justify-between mb-4">
        <h3 className="text-sm font-bold text-neutral-300 flex gap-2">
          <Activity className="w-4 h-4 text-indigo-400" /> Frame-Level Heatmap
        </h3>
        <span className="text-xs text-neutral-600 font-mono">{duration}</span>
      </div>
      
      <div className="h-24 flex items-center gap-0.5 px-2">
        {segments.map((seg, i) => (
          <div 
            key={i}
            className={`w-full rounded-sm transition-all ${
              seg.isSpoof 
                ? 'bg-rose-500 shadow-[0_0_15px_rgba(244,63,94,0.3)] animate-pulse' 
                : 'bg-neutral-800'
            }`}
            style={{ height: `${seg.intensity}%` }}
          />
        ))}
      </div>
    </div>
  );
}