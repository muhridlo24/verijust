"use client";

import React from "react";
import { 
  GitCommit, AlertOctagon, ArrowRightLeft, 
  Fingerprint, Waves, BrainCircuit, 
  ShieldAlert, Siren, UserCheck, UserX
} from "lucide-react";
import { AudioFile } from "@/lib/types";

// --- Types ---
interface IndicatorCardProps {
  title: string;
  value: string;
  sub: string;
  icon: React.ReactNode;
  color: "rose" | "amber" | "purple";
}

// --- Extended Mock Data for Advanced Features ---
const CASE_RISK_SCORE = 88; // High Risk

// 1. Tone/Sentiment Data
const TONE_ANALYSIS = {
  overall: "Aggressive & Anxious",
  timeline: [
    { file: "Call 1", sentiment: "Neutral", anxiety: 20 },
    { file: "Call 2", sentiment: "Urgent", anxiety: 85 }, // Spike in anxiety
    { file: "Voicemail", sentiment: "Aggressive", anxiety: 90 },
  ]
};

// 2. Linguistic Fraud Indicators
const FRAUD_SIGNALS = [
  { type: "Urgency Tactics", count: 4, desc: "Repeated use of 'immediately', 'now', 'or else'." },
  { type: "Dissociation", count: 2, desc: "Shifted from 'I' to 'We'/'They' when discussing funds." },
  { type: "Hedging", count: 3, desc: "Use of 'maybe', 'I think', 'to my knowledge'." }
];

// 3. Biometric Matching (Speaker Verification)
// const BIOMETRICS = {
//   matchScore: 42, // Low match = Likely Imposter
//   verdict: "Imposter Detected",
//   reference: "Call 1 (Verified)",
//   suspect: "Call 2 (Mismatch)"
// };

export default function ContextView({ files }: { files: AudioFile[] }) {
  
  if (files.length < 2) return (
    <div className="flex flex-col items-center justify-center h-full text-neutral-500 animate-in fade-in">
      <GitCommit className="w-16 h-16 mb-6 opacity-20" />
      <h2 className="text-xl font-bold text-neutral-300">Insufficient Data</h2>
      <p className="max-w-md text-center mt-2">Upload at least 2 files to unlock Cross-File Intelligence, Speaker Verification, and Story Semantics.</p>
    </div>
  );

  return (
    <div className="space-y-8 animate-in slide-in-from-right-4 duration-700 pb-20">
      
      {/* 1. MASTER RISK DASHBOARD */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Risk Score Gauge */}
        <div className="lg:col-span-1 bg-neutral-900/50 border border-neutral-800 rounded-3xl p-6 flex flex-col items-center justify-center relative overflow-hidden">
          <div className="absolute inset-0 bg-rose-500/10 blur-3xl" />
          <h3 className="text-xs font-bold uppercase tracking-widest text-neutral-500 mb-4 z-10">Case Risk Score</h3>
          <div className="relative z-10 flex items-center justify-center">
            <svg className="w-32 h-32 transform -rotate-90">
              <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-neutral-800" />
              <circle cx="64" cy="64" r="56" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-rose-500" strokeDasharray={351} strokeDashoffset={351 - (351 * CASE_RISK_SCORE) / 100} />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-4xl font-bold text-white">{CASE_RISK_SCORE}</span>
              <span className="text-[10px] text-rose-400 font-bold uppercase">Critical</span>
            </div>
          </div>
          <p className="text-xs text-center text-neutral-400 mt-4 z-10">
            Combined probability of Spoofing, Fraud, and Contradiction.
          </p>
        </div>

        {/* Key Indicators */}
        <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-4">
          <IndicatorCard 
            title="Forgery Impact" 
            value="High" 
            sub="Detected in 2/3 files"
            icon={<ShieldAlert className="text-rose-500" />} 
            color="rose"
          />
          <IndicatorCard 
            title="Biometric Match" 
            value="Failed" 
            sub="Speaker voice mismatch"
            icon={<UserX className="text-amber-500" />} 
            color="amber"
          />
          <IndicatorCard 
            title="Semantic Logic" 
            value="3 Conflicts" 
            sub="Money & Location errors"
            icon={<GitCommit className="text-purple-500" />} 
            color="purple"
          />
        </div>
      </div>

      {/* 2. SPEAKER BIO-METRICS (The "Imposter" Check) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-neutral-900/40 border border-neutral-800 rounded-2xl p-8 relative overflow-hidden">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-amber-500/10 rounded-lg"><Fingerprint className="w-5 h-5 text-amber-500" /></div>
            <h3 className="text-lg font-bold text-white">Speaker Verification</h3>
          </div>
          
          <div className="flex items-center justify-between gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-neutral-800 rounded-full flex items-center justify-center mb-2 mx-auto border-2 border-emerald-500/50">
                <UserCheck className="w-8 h-8 text-emerald-500" />
              </div>
              <p className="text-xs text-neutral-400">File 1 (Base)</p>
            </div>

            <div className="flex-1 flex flex-col items-center">
               <div className="w-full h-1 bg-neutral-800 rounded-full mb-2 overflow-hidden">
                 <div className="h-full bg-amber-500 w-[42%]" />
               </div>
               <span className="text-xs font-mono text-amber-500 bg-amber-500/10 px-2 py-0.5 rounded">
                 42% Match (Threshold: 85%)
               </span>
               <p className="text-[10px] text-rose-400 mt-1 font-bold uppercase tracking-wide">Imposter Likely</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-neutral-800 rounded-full flex items-center justify-center mb-2 mx-auto border-2 border-rose-500/50 animate-pulse">
                <UserX className="w-8 h-8 text-rose-500" />
              </div>
              <p className="text-xs text-neutral-400">File 2 (Suspect)</p>
            </div>
          </div>
        </div>

        {/* 3. TONE & EMOTION ANALYSIS */}
        <div className="bg-neutral-900/40 border border-neutral-800 rounded-2xl p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-cyan-500/10 rounded-lg"><Waves className="w-5 h-5 text-cyan-500" /></div>
            <h3 className="text-lg font-bold text-white">Psychological Tone</h3>
          </div>
          
          <div className="space-y-4">
            {TONE_ANALYSIS.timeline.map((item, i) => (
              <div key={i} className="flex items-center gap-4">
                <span className="text-xs text-neutral-500 w-16">{item.file}</span>
                <div className="flex-1 h-2 bg-neutral-800 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${item.anxiety > 50 ? 'bg-gradient-to-r from-orange-500 to-rose-500' : 'bg-emerald-500'}`} 
                    style={{ width: `${item.anxiety}%` }}
                  />
                </div>
                <span className={`text-xs font-bold w-20 text-right ${item.anxiety > 50 ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {item.sentiment}
                </span>
              </div>
            ))}
          </div>
          <p className="text-xs text-neutral-500 mt-6 pt-4 border-t border-neutral-800">
            <span className="text-cyan-400 font-bold">Insight:</span> Subject shows rapid escalation in anxiety and aggression between File 1 and File 2, correlated with the Spoof detection.
          </p>
        </div>
      </div>

      {/* 4. FRAUD LINGUISTICS & CONTRADICTIONS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Fraud Tags */}
        <div className="lg:col-span-1 bg-neutral-900/40 border border-neutral-800 rounded-2xl p-6">
          <h3 className="text-sm font-bold text-neutral-300 mb-4 flex items-center gap-2">
            <Siren className="w-4 h-4 text-rose-500" /> Linguistic Deception
          </h3>
          <div className="space-y-3">
            {FRAUD_SIGNALS.map((sig, i) => (
              <div key={i} className="bg-neutral-900 border border-neutral-800 p-3 rounded-lg hover:border-rose-500/30 transition">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-rose-200 font-bold text-sm">{sig.type}</span>
                  <span className="bg-rose-500/20 text-rose-400 text-[10px] px-1.5 rounded font-mono">x{sig.count}</span>
                </div>
                <p className="text-[10px] text-neutral-500">{sig.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Semantic Story Graph (The Contradiction Card) */}
        <div className="lg:col-span-2 bg-neutral-900/40 border border-neutral-800 rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10"><GitCommit className="w-32 h-32 text-purple-500" /></div>
          
          <h3 className="text-sm font-bold text-neutral-300 mb-6 flex items-center gap-2 relative z-10">
            <BrainCircuit className="w-4 h-4 text-purple-500" /> Story Semantics (Logic Audit)
          </h3>

          <div className="bg-neutral-950/50 border border-neutral-800 rounded-xl p-6 relative z-10">
             <div className="flex items-center gap-3 mb-6">
                <AlertOctagon className="w-4 h-4 text-rose-500" />
                <span className="text-rose-200 font-bold text-sm">Critical Discrepancy: Financials</span>
             </div>
             
             <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="flex-1">
                   <p className="text-[10px] text-neutral-500 uppercase mb-1">File 1 (00:12)</p>
                   <div className="p-3 bg-neutral-900 border border-neutral-700 rounded-lg">
                      <p className="text-lg font-mono text-white">&ldquo;$100.00&rdquo;</p>
                   </div>
                </div>
                
                <ArrowRightLeft className="text-neutral-600" />
                
                <div className="flex-1">
                   <p className="text-[10px] text-neutral-500 uppercase mb-1">File 2 (03:45)</p>
                   <div className="p-3 bg-rose-950/20 border border-rose-500/50 rounded-lg relative overflow-hidden">
                      <div className="absolute top-0 right-0 bg-rose-600 text-[8px] font-bold text-white px-1.5 py-0.5">FAKE VOICE</div>
                      <p className="text-lg font-mono text-rose-400">&ldquo;$10,000.00&rdquo;</p>
                   </div>
                </div>
             </div>
             <p className="text-[11px] text-neutral-500 mt-4 border-t border-neutral-800 pt-3">
               <span className="text-purple-400 font-bold">Logic Failure:</span> Subject altered the claim amount by 10,000% while using a synthesized voice profile.
             </p>
          </div>
        </div>

      </div>
    </div>
  );
}

// --- Sub Component ---
function IndicatorCard({ title, value, sub, icon, color }: IndicatorCardProps) {
  const colors: Record<string, string> = {
    rose: "bg-rose-500/10 border-rose-500/20 text-rose-500",
    amber: "bg-amber-500/10 border-amber-500/20 text-amber-500",
    purple: "bg-purple-500/10 border-purple-500/20 text-purple-500"
  };

  return (
    <div className={`p-4 rounded-2xl border flex items-start justify-between ${colors[color] || colors.rose}`}>
      <div>
        <p className="text-xs font-bold uppercase opacity-70 mb-1">{title}</p>
        <p className="text-2xl font-bold text-white mb-1">{value}</p>
        <p className="text-[10px] opacity-60">{sub}</p>
      </div>
      <div className="p-2 bg-neutral-950/20 rounded-lg">{icon}</div>
    </div>
  );
}