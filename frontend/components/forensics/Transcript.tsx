import { Search } from "lucide-react";
import { TranscriptChunk } from "../../lib/types";

function Transcript({ transcript }: { transcript: TranscriptChunk[] }) {
  return (
    <div className="bg-neutral-900/30 border border-neutral-800 rounded-2xl p-8">
       <h3 className="text-sm font-bold text-neutral-300 mb-6 flex items-center gap-2">
        <Search className="w-4 h-4 text-indigo-400" /> Semantic Audit
      </h3>
      <div className="leading-loose text-lg font-light text-neutral-300 font-serif">
        {transcript.map((chunk, i) => (
          <span
            key={i}
            className={`
              mr-1.5 px-1 py-0.5 rounded transition-all cursor-help relative group
              ${chunk.isSpoof
                ? 'bg-rose-950/40 text-rose-200 border-b-2 border-rose-500'
                : 'hover:bg-neutral-800'
              }
            `}
          >
            {chunk.text}
            {chunk.isSpoof && (
               <span className="absolute -top-10 left-1/2 -translate-x-1/2 bg-neutral-900 text-rose-400 text-[10px] font-bold px-3 py-2 rounded-lg border border-neutral-700 shadow-xl opacity-0 group-hover:opacity-100 transition whitespace-nowrap z-20 pointer-events-none">
                FAKE (99%)
              </span>
            )}
          </span>
        ))}
      </div>
    </div>
  );
}

export default Transcript;