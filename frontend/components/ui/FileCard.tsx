import { FileAudio, Trash } from "lucide-react";
import { FileCardProps } from "../../lib/types";

function FileCard({ file, isActive, onClick, onDelete }: FileCardProps) {
  const isSpoof = file.verdict === "spoof";
  return (
    <div
      onClick={onClick}
      className={`p-3 rounded-xl border cursor-pointer transition-all duration-200 group relative overflow-hidden
        ${isActive
          ? 'bg-neutral-800 border-neutral-600 shadow-lg'
          : 'bg-neutral-900/50 border-transparent hover:bg-neutral-800 hover:border-neutral-700'
        }`}
    >
      <div className="flex justify-between items-start relative z-10">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${file.status === 'queued' ? 'bg-neutral-800 text-neutral-500' : isSpoof ? 'bg-rose-500/10 text-rose-500' : 'bg-emerald-500/10 text-emerald-500'}`}>
            <FileAudio className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <p className={`text-sm font-medium truncate ${isActive ? 'text-white' : 'text-neutral-400 group-hover:text-white'}`}>{file.name}</p>
            <p className="text-[10px] text-neutral-600 truncate">
               {file.status === 'complete' ? file.duration : file.status}
               {file.status === 'timeout' && file.error ? ` (${file.error})` : ''}...
            </p>
          </div>
        </div>
        {file.status === 'complete' && (
           <div className={`w-2 h-2 rounded-full ${isSpoof ? 'bg-rose-500' : 'bg-emerald-500'}`} />
        )}
        {onDelete && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (window.confirm(`Delete "${file.name}"?`)) {
                onDelete(file.id);
              }
            }}
            className="absolute top-2 right-2 text-neutral-400 hover:text-rose-500"
          >
            <Trash className="w-4 h-4" />
          </button>
        )}
      </div>
      {/* Mini Progress Bar for Processing Files */}
      {file.status !== 'complete' && file.status !== 'queued' && (
        <div className="absolute bottom-0 left-0 h-0.5 bg-indigo-500 transition-all duration-500" style={{ width: `${file.progress}%` }} />
      )}
    </div>
  );
}

export default FileCard;