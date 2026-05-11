import { Activity, Lock, Upload } from "lucide-react";
import { LandingPageProps } from "../lib/types";

function LandingPage({ onUploadClick, fileInputRef, handleFileSelect }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-neutral-950 text-white flex flex-col relative overflow-hidden font-sans selection:bg-indigo-500/30">

      {/* Dynamic Background */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[128px]" />
        <div className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-[128px]" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20" />
      </div>

      {/* Navbar */}
      <nav className="relative z-10 flex items-center justify-between px-12 py-8">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <span className="text-2xl font-bold tracking-tight">VeriJust<span className="text-neutral-500">.ai</span></span>
        </div>
        <div className="flex gap-8 text-sm font-medium text-neutral-400">
          <a href="/login" className="hover:text-white transition">Login</a>
          {/* <a href="#" className="hover:text-white transition">Forensics</a>
          <a href="#" className="hover:text-white transition">Enterprise</a> */}
        </div>
      </nav>

      {/* Hero Content */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-4">

        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-neutral-900/50 border border-neutral-800 text-xs font-medium text-neutral-400 mb-8 backdrop-blur-sm animate-in fade-in slide-in-from-bottom-4 duration-700">
          <Lock className="w-3 h-3" /> End-to-End Encrypted Analysis
        </div>

        <h1 className="text-6xl md:text-7xl font-bold tracking-tight mb-6 max-w-4xl bg-clip-text text-transparent bg-gradient-to-b from-white to-neutral-500 animate-in fade-in slide-in-from-bottom-8 duration-1000">
          Detect the Truth in <br /> Every Audio Frame.
        </h1>

        <p className="text-xl text-neutral-400 mb-12 max-w-2xl leading-relaxed animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-100">
          Advanced deepfake detection powered by Wav2Vec 2.0 and semantic logic analysis.
          Identify synthetic splicing, cloned voices, and logical contradictions instantly.
        </p>

        {/* Upload Zone */}
        <div
          onClick={onUploadClick}
          className="group relative w-full max-w-xl h-64 border border-dashed border-neutral-700 bg-neutral-900/30 hover:bg-neutral-800/50 hover:border-indigo-500/50 rounded-3xl flex flex-col items-center justify-center cursor-pointer transition-all duration-300 animate-in zoom-in-95 duration-1000 delay-200"
        >
          <input
            type="file"
            multiple
            accept="audio/*"
            className="hidden"
            ref={fileInputRef}
            onChange={handleFileSelect}
          />

          <div className="w-20 h-20 bg-neutral-800 rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-xl group-hover:shadow-indigo-500/20">
            <Upload className="w-8 h-8 text-indigo-400" />
          </div>

          <h3 className="text-xl font-semibold text-white mb-2">Upload Evidence Files</h3>
          <p className="text-neutral-500 text-sm">Drag & drop or click to browse</p>
          <div className="flex gap-3 mt-6 text-[10px] text-neutral-600 uppercase tracking-widest font-mono">
            <span>MP3</span>
            <span>•</span>
            <span>WAV</span>
            <span>•</span>
            <span>FLAC</span>
            <span>•</span>
            <span>M4A</span>
          </div>

          {/* Decorative Corner Accents */}
          <div className="absolute top-4 left-4 w-3 h-3 border-l border-t border-neutral-600 opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="absolute top-4 right-4 w-3 h-3 border-r border-t border-neutral-600 opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="absolute bottom-4 left-4 w-3 h-3 border-l border-b border-neutral-600 opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="absolute bottom-4 right-4 w-3 h-3 border-r border-b border-neutral-600 opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>

      </main>

      {/* Footer Stats */}
      <footer className="relative z-10 py-8 border-t border-neutral-900">
        <div className="flex justify-center gap-16 text-center">
          <div>
            <p className="text-2xl font-bold text-white">99.2%</p>
            <p className="text-xs text-neutral-500 uppercase tracking-wider">Accuracy</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-white">&lt;40ms</p>
            <p className="text-xs text-neutral-500 uppercase tracking-wider">Latency</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-white">256-bit</p>
            <p className="text-xs text-neutral-500 uppercase tracking-wider">Encryption</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;