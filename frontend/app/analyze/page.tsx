"use client";
import { useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import ForensicView from "@/components/forensics/ForensicView";
import ContextView from "@/components/contextual/ContextView";
import { uploadAndAnalyze } from "@/lib/api";
import { AudioFile } from "@/lib/types";
// ... imports ...

// export default function AnalyzePage() {
  // ... existing state ...
  

  // ... rest of your code ...
export default function Dashboard() {
  const [files, setFiles] = useState<AudioFile[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const viewMode = "forensic";

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    
    // Create temporary "Queued" files for UI
    const newFiles: AudioFile[] = Array.from(e.target.files).map(f => ({
      id: Math.random().toString(),
      name: f.name,
      size: (f.size / 1024 / 1024).toFixed(2) + " MB",
      duration: "00:00",
      url: URL.createObjectURL(f),
      status: "queued" as const,
      progress: 0
    }));
    
    setFiles(prev => [...prev, ...newFiles]);

    // Actually upload and process (Backend Connection)
    for (let i = 0; i < e.target.files.length; i++) {
      const fileObj = e.target.files[i];
      try {
        // This calls our /lib/api.ts function
        const result = await uploadAndAnalyze(fileObj);
        
        // Update state with real results from Python
        setFiles(prev => prev.map(f => f.name === result.name ? result : f));
      } catch (err) {
        console.error("Analysis failed", err);
      }
    }
  };

  const activeFile = files.find(f => f.id === activeId);

  return (
    <div className="flex h-screen bg-neutral-950 text-white font-sans">
      <Sidebar 
        files={files} 
        activeId={activeId} 
        onSelect={setActiveId} 
        onUpload={handleUpload} 
      />

      <main className="flex-1 overflow-y-auto p-8">
        {viewMode === "forensic" && activeFile ? (
          <ForensicView file={activeFile} />
        ) : (
          <ContextView files={files} />
        )}
      </main>
    </div>
  );
}