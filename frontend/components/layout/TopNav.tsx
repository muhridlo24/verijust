"use client";

import React from "react";
import { User, Fingerprint, Activity, LogOut } from "lucide-react";

interface TopNavProps {
  user: {
    name: string;
    role: string;
    isGuest: boolean;
  };
  fileCount: number;
  onLogout: () => void;
}

export default function TopNav({ user, fileCount, onLogout }: TopNavProps) {
  return (
    <header className="h-16 border-b border-neutral-800 flex items-center justify-between px-8 bg-neutral-900/20 backdrop-blur-md sticky top-0 z-20">
      
      {/* Left Side: User & Case Info */}
      <div className="flex items-center gap-4 text-sm">
        
        {/* User Badge */}
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border transition-colors ${
          user.isGuest 
            ? 'bg-neutral-800 border-neutral-700 text-neutral-400' 
            : 'bg-indigo-500/10 border-indigo-500/30 text-indigo-300'
        }`}>
          <User className="w-3 h-3" />
          <span className="font-medium">{user.name}</span>
          <span className="text-[10px] opacity-60 border-l border-white/10 pl-2 ml-1">
            {user.role}
          </span>
        </div>

        <span className="text-neutral-600">/</span>
        
        <div className="flex items-center gap-2 text-neutral-400">
          <Fingerprint className="w-4 h-4 opacity-50" />
          {/* In a real app, this ID would come from the backend/URL */}
          <span>Case #SESSION-{new Date().getFullYear()}</span> 
        </div>
      </div>
      
      {/* Right Side: Status & Actions */}
      <div className="flex items-center gap-4">
         {/* Engine Status Indicator */}
         {fileCount > 0 && (
            <span className="flex items-center gap-2 text-xs font-mono text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20 animate-in fade-in">
              <Activity className="w-3 h-3" /> ENGINE ONLINE
            </span>
         )}
         
         {/* Logout Button */}
         <button 
           onClick={onLogout}
           className="p-2 hover:bg-neutral-800 rounded-lg text-neutral-500 hover:text-white transition"
           title="Sign Out"
         >
           <LogOut className="w-4 h-4" />
         </button>
      </div>
    </header>
  );
}