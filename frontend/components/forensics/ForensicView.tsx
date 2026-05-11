import { useState } from "react";
import { ShieldAlert, ShieldCheck, FileAudio, Activity, Search, Play, BrainCircuit } from "lucide-react";
import { AudioFile } from "../../lib/types";
import MetricRow from "../ui/MetricRow";
import Transcript from "./Transcript";

function ForensicView({ file }: { file: AudioFile }) {
  const [heights] = useState(() => Array.from({ length: 60 }, () => Math.max(20, Math.random() * 100)));
  if (file.status !== "complete") {
    // Processing State UI
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-center space-y-6 animate-in fade-in">
        <div className="relative w-24 h-24">
          <div className="absolute inset-0 border-4 border-neutral-800 rounded-full" />
          <div className="absolute inset-0 border-4 border-indigo-500 rounded-full border-t-transparent animate-spin" />
          <Activity className="absolute inset-0 m-auto w-8 h-8 text-indigo-500 animate-pulse" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">
            {file.status === "extracting" ? "Extracting Features..." : "Running Neural Analysis..."}
          </h2>
          <p className="text-neutral-500">Processing frame-level tensors on GPU Cluster</p>
        </div>
        <div className="w-64 h-1 bg-neutral-900 rounded-full overflow-hidden">
          <div className="h-full bg-indigo-500 transition-all duration-500" style={{ width: `${file.progress}%` }} />
        </div>
      </div>
    );
  }

  const isSpoof = file.verdict === "spoof";

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Result Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 bg-neutral-900/50 border border-neutral-800 rounded-2xl p-8 relative overflow-hidden group hover:border-neutral-700 transition">
          <div className={`absolute top-0 left-0 w-1 h-full ${isSpoof ? 'bg-rose-500' : 'bg-emerald-500'}`} />
          <div className={`absolute -right-20 -top-20 w-64 h-64 rounded-full blur-[100px] opacity-10 group-hover:opacity-20 transition duration-1000 ${isSpoof ? 'bg-rose-600' : 'bg-emerald-600'}`} />

          <div className="relative z-10 flex flex-col md:flex-row justify-between items-start gap-4">
            <div>
              <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-4 border ${isSpoof ? 'bg-rose-500/10 border-rose-500/20 text-rose-400' : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'}`}>
                {isSpoof ? <ShieldAlert className="w-3 h-3" /> : <ShieldCheck className="w-3 h-3" />}
                {isSpoof ? "Manipulated Audio" : "Authentic Audio"}
              </div>
              <h1 className="text-4xl font-bold mb-2 text-white">{isSpoof ? "Deepfake Detected" : "Integrity Verified"}</h1>
              <p className="text-neutral-400 max-w-lg text-sm leading-relaxed">
                Analysis of {file.name} complete.
                {isSpoof
                  ? ' High-confidence synthetic artifacts detected in 3 distinct segments. Voice cloning signature matches known generative models.'
                  : ' No synthetic manipulation detected across 42,000 frames. Audio appears to be an original recording.'}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-neutral-500 mb-1 uppercase tracking-widest font-semibold">Confidence Score</p>
              <div className="text-6xl font-mono font-bold tracking-tighter text-white">
                {file.confidence?.toFixed(1)}%
              </div>
            </div>
          </div>
        </div>

        {/* Forensic Metadata */}
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-2xl p-6 flex flex-col justify-center space-y-3">
          <MetricRow label="File Size" value={file.size} icon={<FileAudio className="w-4 h-4" />} />
          <MetricRow label="Duration" value={file.duration} icon={<Activity className="w-4 h-4" />} />
          <MetricRow label="Sample Rate" value="16.0 kHz" icon={<Search className="w-4 h-4" />} />
          <div className="h-px bg-neutral-800 my-2" />
          <div className="flex items-center gap-2 text-xs text-neutral-500">
             <BrainCircuit className="w-3 h-3" /> Model: W2V2-XL
          </div>
        </div>
      </div>

      {/* Waveform */}
      <div className="bg-neutral-900/30 border border-neutral-800 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-sm font-bold text-neutral-300 flex items-center gap-2">
            <Activity className="w-4 h-4 text-indigo-400" /> Frame-Level Heatmap
          </h3>
          <span className="text-xs text-neutral-600 font-mono">00:00 / {file.duration}</span>
        </div>

        <div className="h-24 flex items-center gap-0.5 justify-between px-2 relative group cursor-crosshair">
          {Array.from({ length: 60 }).map((_, i) => {
            const isSuspicious = isSpoof && i > 30 && i < 45;
            const height = heights[i];
            return (
              <div
                key={i}
                className={`w-full rounded-sm transition-all duration-300 ${isSuspicious ? 'bg-rose-500/80 shadow-[0_0_15px_rgba(244,63,94,0.3)] animate-pulse' : 'bg-neutral-800 group-hover:bg-neutral-700'}`}
                style={{ height: `${height}%` }}
              />
            )
          })}
          {/* Mock Playhead */}
          <div className="absolute left-[30%] h-full w-0.5 bg-white shadow-[0_0_10px_white] z-10 pointer-events-none" />
        </div>

        <div className="flex justify-center mt-6">
          <button className="w-12 h-12 bg-white text-black rounded-full flex items-center justify-center hover:scale-105 transition shadow-xl shadow-white/10">
            <Play className="w-5 h-5 ml-1" />
          </button>
        </div>
      </div>

      {/* Transcript */}
      {file.transcript && <Transcript transcript={file.transcript} />}
    </div>
  );
}

export default ForensicView;