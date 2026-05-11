"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

// --- IMPORTS ---
import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav"; // <--- Import the new component
import ForensicView from "@/components/forensics/ForensicView";
import ContextView from "@/components/contextual/ContextView";
import LandingPage from "@/components/LandingPage";
import { AudioFile } from "@/lib/types";
import { Activity } from "lucide-react";

// API helpers
import { uploadEvidence, apiGet } from "@/lib/api";

export default function Dashboard() {
  const router = useRouter();

  // --- State ---
  const user = (() => {
    if (typeof window !== 'undefined') {
      const storedUser = localStorage.getItem("verijust_user");
      return storedUser ? JSON.parse(storedUser) : null;
    }
    return { name: "Loading...", role: "...", isGuest: true };
  })();
  const [files, setFiles] = useState<AudioFile[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"forensic" | "contextual">("forensic");
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  // --- Auth Check ---
  useEffect(() => {
    if (!user) {
      // Don't redirect, show landing page instead
    }
  }, [user, router]);

  // --- Landing Page Handlers ---
  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    
    // Redirect to login for authentication before upload
    router.push("/login");
  };

  // --- Actions ---
  const handleLogout = () => {
    localStorage.removeItem("verijust_user");
    router.push("/login");
  };

  const handleDeleteFile = (id: string) => {
    // confirm already handled inside FileCard, this just updates state
    setFiles(prev => prev.filter(f => f.id !== id));
    if (activeId === id) {
      setActiveId(null);
    }
  };

  // how long we will wait for the background analysis before giving up
  const POLL_INTERVAL_MS = 2000;
  const MAX_POLL_DURATION_MS = 1000 * 60 * 5; // 5 minutes

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;

    // UI: Create temporary "Queued" files
    const newFiles: AudioFile[] = Array.from(e.target.files).map(f => ({
      id: Math.random().toString(36).substr(2, 9),
      name: f.name,
      size: (f.size / 1024 / 1024).toFixed(2) + " MB",
      duration: "00:00",
      url: URL.createObjectURL(f),
      status: "queued" as const,
      progress: 0
    }));

    setFiles(prev => [...prev, ...newFiles]);
    if (!activeId && newFiles.length > 0) setActiveId(newFiles[0].id);

    // Backend: Upload and Process asynchronously via Celery

    for (let i = 0; i < e.target.files.length; i++) {
      const fileObj = e.target.files[i];
      // mark this file as processing
      setFiles(prev => prev.map(f => f.name === fileObj.name ? { ...f, status: 'extracting', progress: 5 } : f));

      try {
        const uploadResp = await uploadEvidence(fileObj);
        // uploadResp contains evidence_id and task_id
        const { evidence_id: evidenceId, task_id: taskId } = uploadResp;

        // update UI to show task started
        setFiles(prev => prev.map(f => f.name === fileObj.name ? { ...f, status: 'analyzing', progress: 10 } : f));

        // poll task-status endpoint until complete/failure
        const poll = async () => {
          try {
            const statusResp = await apiGet(`/api/v1/forensics/task-status/${taskId}`);
            if (statusResp.status === 'pending' || statusResp.status === 'started') {
              // update progress heuristically
              setFiles(prev => prev.map(f => f.name === fileObj.name ? { ...f, progress: Math.min(95, (f.progress || 10) + 10) } : f));
              return false; // continue polling
            }

            if (statusResp.status === 'completed') {
              const result = statusResp.result || {};
              const updated: AudioFile = {
                id: evidenceId || Math.random().toString(36).substr(2, 9),
                name: fileObj.name,
                size: (fileObj.size / 1024 / 1024).toFixed(2) + " MB",
                duration: result.duration || "03:00",
                url: URL.createObjectURL(fileObj),
                status: 'complete',
                progress: 100,
                verdict: result.verdict || 'bonafide',
                confidence: result.confidence || 0,
                transcript: result.transcript || []
              };

              setFiles(prev => prev.map(f => f.name === fileObj.name ? updated : f));
              return true; // stop polling
            }

            if (statusResp.status === 'failed') {
              setFiles(prev => prev.map(f => f.name === fileObj.name ? { ...f, status: 'queued', progress: 0 } : f));
              console.error('Analysis failed for', fileObj.name, statusResp.error);
              return true; // stop polling
            }

            // unknown state: continue
            return false;
          } catch (err) {
            console.error('Polling error', err);
            return false;
          }
        };

        // poll every POLL_INTERVAL_MS until completion/failure. after the
        // maximum duration we mark the entry as 'timeout' but keep polling in
        // the background so that when the server finally finishes we can
        // display the real results.
        await new Promise<void>((resolve) => {
          const start = Date.now();
          let timedOut = false;
          const iv = setInterval(async () => {
            const elapsed = Date.now() - start;
            if (elapsed > MAX_POLL_DURATION_MS && !timedOut) {
              timedOut = true;
              console.warn("Polling timed out for", fileObj.name);
              setFiles(prev => prev.map(f => f.name === fileObj.name ? { ...f, status: 'timeout', error: 'taking longer than expected' } : f));
            }

            const done = await poll();
            if (done) {
              clearInterval(iv);
              resolve();
            }
          }, POLL_INTERVAL_MS);
        });

      } catch (err) {
        console.error("Upload/analysis failed", err);
        setFiles(prev => prev.map(f => f.name === fileObj.name ? { ...f, status: 'queued', progress: 0 } : f));
      }
    }
  };

  const activeFile = files.find(f => f.id === activeId);

  // Show landing page if no user is logged in
  if (!user) {
    return (
      <LandingPage
        onUploadClick={handleUploadClick}
        fileInputRef={fileInputRef}
        handleFileSelect={handleFileSelect}
      />
    );
  }

  return (
    <div className="flex h-screen bg-neutral-950 text-white font-sans overflow-hidden">
      
      {/* 1. SIDEBAR */}
      <Sidebar 
        files={files} 
        activeId={activeId} 
        onSelect={(id) => { setActiveId(id); setViewMode("forensic"); }} 
        onUpload={handleUpload}
        onDelete={handleDeleteFile}
        viewMode={viewMode}
        setViewMode={setViewMode}
      />

      <div className="flex-1 flex flex-col bg-opacity-5 relative">
        
        {/* 2. TOP NAVIGATION (Separated) */}
        <TopNav 
          user={user} 
          fileCount={files.length} 
          onLogout={handleLogout} 
        />

        {/* 3. MAIN CONTENT AREA */}
        <main className="flex-1 overflow-y-auto p-8 scrollbar-thin scrollbar-thumb-neutral-800">
          {viewMode === "forensic" ? (
             activeFile ? (
               <ForensicView file={activeFile} />
             ) : (
               <div className="flex h-full items-center justify-center text-neutral-500 flex-col gap-2">
                 <Activity className="w-8 h-8 opacity-20" />
                 <p>Select a file to begin analysis</p>
               </div>
             )
          ) : (
            <ContextView files={files} />
          )}
        </main>
      </div>
    </div>
  );
}