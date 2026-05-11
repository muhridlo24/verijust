"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { 
  Activity, Lock, Mail, Key, 
  User, ShieldCheck
} from "lucide-react";
import { 
  saveTokenToCookie, 
  saveUserProfile,
  saveTokenToStorage 
} from "@/lib/token";

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  // --- Actions ---

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // Simulate API Call
    setTimeout(() => {
      // Mock Success - In production, this would come from backend
      const mockToken = `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJBZG1pbiBJbnZlc3RpZ2F0b3IiLCJqdGkiOiJ1c3ItODgyMSIsImV4cCI6JHtEYXRlLm5vdygpICsgODY0MDAwMDB9fQ.mock`;
      const userProfile: { name: string; role: 'admin' | 'investigator' | 'viewer'; id: string; isGuest: boolean } = {
        name: "Admin Investigator",
        role: "investigator",
        id: "USR-8821",
        isGuest: false
      };
      
      // Save to cookies and storage
      saveTokenToCookie(mockToken, 1440); // 24 hours
      saveTokenToStorage(mockToken);
      saveUserProfile(userProfile);
      
      router.push("/");
    }, 1500);
  };

  const handleGuest = async () => {
    setLoading(true);
    const guestProfile: { name: string; role: 'admin' | 'investigator' | 'viewer'; id: string; isGuest: boolean; token?: string } = {
      name: "Guest User",
      role: "viewer",
      id: `GST-${Math.floor(Math.random() * 1000)}`,
      isGuest: true
    };

    try {
      const API_BASE = process.env.NEXT_PUBLIC_DJANGO_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_BASE}/api/v1/auth/guest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: guestProfile.name })
      });

      if (res.ok) {
        const data = await res.json();
        // Backend should store token to Supabase and return confirmation.
        const confirmed = data?.saved || data?.success || data?.confirmed;
        if (data?.access_token && confirmed) {
          // Save to cookies and storage
          saveTokenToCookie(data.access_token, 15); // 15 minutes for guest
          saveTokenToStorage(data.access_token);
          guestProfile['token'] = data.access_token;
        } else {
          console.warn("Guest token not confirmed by backend", data);
        }
      } else {
        console.error("Guest token request failed", res.status);
      }
    } catch (err) {
      console.error("Error requesting guest token", err);
    } finally {
      saveUserProfile(guestProfile);
      setLoading(false);
      router.push("/");
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white flex items-center justify-center relative overflow-hidden font-sans selection:bg-indigo-500/30">
      
      {/* Background Ambience */}
      <div className="absolute inset-0">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] bg-indigo-600/10 rounded-full blur-[128px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[128px]" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20" />
      </div>

      {/* Login Card */}
      <div className="relative z-10 w-full max-w-md p-8 bg-neutral-900/50 border border-neutral-800 backdrop-blur-xl rounded-3xl shadow-2xl animate-in zoom-in-95 duration-500">
        
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-indigo-500/20">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight mb-2">Welcome Back</h1>
          <p className="text-neutral-400 text-sm">Sign in to access the VeriJust Forensic Console</p>
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} className="space-y-4">
          
          <div className="space-y-2">
            <label className="text-xs font-semibold text-neutral-500 uppercase ml-1">Email Access ID</label>
            <div className="relative group">
              <Mail className="absolute left-4 top-3.5 w-4 h-4 text-neutral-500 group-focus-within:text-indigo-400 transition" />
              <input 
                type="email" 
                required
                placeholder="investigator@agency.gov"
                className="w-full bg-neutral-950 border border-neutral-800 rounded-xl py-3 pl-11 pr-4 text-sm focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-neutral-500 uppercase ml-1">Secure Key</label>
            <div className="relative group">
              <Key className="absolute left-4 top-3.5 w-4 h-4 text-neutral-500 group-focus-within:text-indigo-400 transition" />
              <input 
                type="password" 
                required
                placeholder="••••••••••••"
                className="w-full bg-neutral-950 border border-neutral-800 rounded-xl py-3 pl-11 pr-4 text-sm focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition"
              />
            </div>
          </div>

          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-white text-black font-bold py-3 rounded-xl hover:bg-neutral-200 transition flex items-center justify-center gap-2 mt-6 disabled:opacity-50"
          >
            {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Lock className="w-4 h-4" />}
            {loading ? "Authenticating..." : "Secure Sign In"}
          </button>
        </form>

        {/* Divider */}
        <div className="relative my-8">
          <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-neutral-800"></div></div>
          <div className="relative flex justify-center text-xs uppercase"><span className="bg-neutral-900 px-2 text-neutral-500">Or access via</span></div>
        </div>

        {/* Guest Button */}
        <button 
          onClick={handleGuest}
          className="w-full bg-neutral-800/50 text-white font-medium py-3 rounded-xl border border-neutral-700 hover:bg-neutral-800 hover:border-neutral-600 transition flex items-center justify-center gap-2"
        >
          <User className="w-4 h-4 text-neutral-400" />
          Continue as Guest
        </button>

        {/* Footer */}
        <div className="mt-8 text-center flex items-center justify-center gap-2 text-[10px] text-neutral-600 font-mono">
           <ShieldCheck className="w-3 h-3" />
           <span>256-BIT ENCRYPTION ACTIVE</span>
        </div>
      </div>
    </div>
  );
}