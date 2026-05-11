import { AudioFile } from "@/lib/types";
import FileCard from "@/components/ui/FileCard";
import { Plus, Activity, BrainCircuit } from "lucide-react";

interface SidebarProps {
  files: AudioFile[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onDelete?: (id: string) => void;
  viewMode?: "forensic" | "contextual";
  setViewMode?: (mode: "forensic" | "contextual") => void;
}

export function Sidebar({ files, activeId, onSelect, onUpload, onDelete, viewMode = "forensic", setViewMode }: SidebarProps) {
  return (
    <div className="w-80 border-r border-neutral-800 bg-neutral-900/40 flex flex-col backdrop-blur-sm">
      <div className="p-6">
        {/* Brand */}
        <div className="flex items-center gap-2 mb-8">
          <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight">VeriJust<span className="text-neutral-500">.ai</span></span>
        </div>

        {/* Contextual Mode Toggle */}
        <button 
          onClick={() => setViewMode?.("contextual")}
          className={`w-full py-3 px-4 rounded-xl border flex items-center justify-between transition-all group mb-6
            ${viewMode === 'contextual' 
              ? 'bg-purple-500/10 border-purple-500/50 text-purple-200 shadow-[0_0_20px_rgba(168,85,247,0.15)]' 
              : 'bg-neutral-800/50 border-neutral-700 hover:border-neutral-500 text-neutral-400'
            }`}
        >
          <div className="flex items-center gap-3">
            <BrainCircuit className="w-5 h-5" />
            <div className="text-left">
              <p className="text-sm font-bold">Contextual Logic</p>
              <p className="text-[10px] opacity-70">Cross-file Analysis</p>
            </div>
          </div>
        </button>

        <div className="flex items-center justify-between mb-3">
          <p className="text-xs font-semibold text-neutral-500 uppercase">Case Files</p>
          <label className="p-1 hover:bg-neutral-800 rounded text-neutral-400 cursor-pointer">
            <Plus className="w-4 h-4" />
            <input type="file" multiple hidden accept="audio/*" onChange={onUpload} />
          </label>
        </div>

        <div className="space-y-2">
          {files.map(file => (
            <FileCard 
              key={file.id} 
              file={file} 
              isActive={activeId === file.id}
              onClick={() => onSelect(file.id)}
              onDelete={onDelete}
            />
          ))}
        </div>
        
      </div>
    </div>
  );
}

export default Sidebar;