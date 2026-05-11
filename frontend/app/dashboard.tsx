"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

// --- IMPORTS ---
import Sidebar from "@/components/layout/Sidebar";
import ForensicView from "@/components/forensics/ForensicView";
import ContextView from "@/components/contextual/ContextView";
import LandingPage from "@/components/LandingPage";
import { useAuth } from "@/lib/useAuth";
import { AudioFile } from "@/lib/types";
import { Activity, LogOut } from "lucide-react";
import { apiGet } from "@/lib/api";

export default function Dashboard() {
  const router = useRouter();
  const { user, token, loading, isAuthenticated, logout } = useAuth();

  // --- State ---
  const [files, setFiles] = useState<AudioFile[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [fetchingData, setFetchingData] = useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  // --- Auth Check ---
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, loading, router]);

  // --- Fetch User's Evidence Files ---
  useEffect(() => {
    if (token && isAuthenticated) {
      fetchUserEvidence();
    }
  }, [token, isAuthenticated]);

  const fetchUserEvidence = async () => {
    try {
      setFetchingData(true);
      // This now includes the Authorization header automatically
      const data = await apiGet("/api/v1/forensics/evidence");
      setFiles(data.files || []);
    } catch (err) {
      console.error("Failed to fetch evidence:", err);
    } finally {
      setFetchingData(false);
    }
  };

  // --- Landing Page Handlers ---
  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;

    const file = e.target.files[0];
    try {
      setFetchingData(true);
      // Create FormData for file upload
      const formData = new FormData();
      formData.append("file", file);
      
      // Upload with token included automatically
      await fetch(`http://localhost:8000/api/v1/forensics/upload`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: formData
      });
      
      // Refresh the files list
      await fetchUserEvidence();
    } catch (err) {
      console.error("Upload failed:", err);
    } finally {
      setFetchingData(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.replace("/login");
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-neutral-950">
        <Activity className="animate-spin w-8 h-8 text-indigo-500" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null; // Will redirect via useEffect
  }

  // --- Render ---
  return (
    <div className="min-h-screen bg-neutral-950 text-white flex flex-col">
      {/* Header with Logout */}
      <div className="border-b border-neutral-800 bg-neutral-900/50 backdrop-blur-xl">
        <div className="flex items-center justify-between p-4">
          <div className="text-xl font-bold">VeriJust</div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-neutral-400">
              {user.name} ({user.role})
            </span>
            <button
              onClick={handleLogout}
              className="p-2 rounded-lg bg-neutral-800 hover:bg-red-500/20 transition"
              title="Logout"
            >
              <LogOut className="w-4 h-4 text-red-400" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar 
          files={files}
          activeId={activeId}
          onSelect={setActiveId}
          onUpload={handleUploadClick}
        />
        <main className="flex-1 overflow-auto">
          {files.length === 0 && !fetchingData ? (
            <LandingPage 
              onUploadClick={handleUploadClick}
              fileInputRef={fileInputRef}
              handleFileSelect={handleFileSelect}
            />
          ) : (
            <div className="flex h-full">
              <div className="flex-1">
                {activeId && files.find(f => f.id === activeId) && (
                  <ForensicView 
                    file={files.find(f => f.id === activeId)!}
                  />
                )}
              </div>
              <div className="w-1/3 border-l border-neutral-800">
                <ContextView 
                  files={files}
                />
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="audio/*,video/*"
        onChange={handleFileSelect}
        className="hidden"
      />
    </div>
  );
}
