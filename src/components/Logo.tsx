"use client";

import React from "react";

export function Logo({ className = "" }: { className?: string }) {
  return (
    <div className={`flex items-center space-x-3 select-none ${className}`}>
      {/* Flagship Luxury Shield + Land Cadastral Icon */}
      <div className="relative w-10 h-10 flex items-center justify-center shrink-0">
        <svg
          viewBox="0 0 44 48"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-full h-full drop-shadow-sm"
        >
          <defs>
            <linearGradient id="shieldGrad" x1="4" y1="2" x2="40" y2="46" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#1E40AF" />
              <stop offset="60%" stopColor="#2563EB" />
              <stop offset="100%" stopColor="#1D4ED8" />
            </linearGradient>
            <linearGradient id="goldGrad" x1="12" y1="14" x2="32" y2="34" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#F59E0B" />
              <stop offset="100%" stopColor="#B45309" />
            </linearGradient>
          </defs>

          {/* Precision Shield Body */}
          <path
            d="M22 2L40 9V22C40 33.5 32.4 43.8 22 46.8C11.6 43.8 4 33.5 4 22V9L22 2Z"
            fill="url(#shieldGrad)"
          />

          {/* Inner Cadastral Grid Outline */}
          <path
            d="M22 6L36 12V22C36 31 30 39.5 22 42.5C14 39.5 8 31 8 22V12L22 6Z"
            stroke="#93C5FD"
            strokeWidth="1.2"
            strokeDasharray="2 2"
            opacity="0.6"
          />

          {/* Central Golden Land Anchor Diamond */}
          <path
            d="M22 13L31 20L22 27L13 20L22 13Z"
            fill="url(#goldGrad)"
          />
          <path
            d="M22 27L31 34L22 40L13 34L22 27Z"
            fill="#FFFFFF"
            opacity="0.95"
          />

          {/* Central Precision Survey Point */}
          <circle cx="22" cy="20" r="2.5" fill="#FFFFFF" />
        </svg>
      </div>

      {/* Brand Typography */}
      <div className="flex flex-col justify-center">
        <div className="flex items-center space-x-1.5">
          <span className="text-xl font-black tracking-tight text-slate-900 dark:text-white leading-none">
            Land<span className="text-[#2563eb] dark:text-[#3b82f6]">Shield</span>
          </span>
          <span className="text-[10px] font-extrabold uppercase tracking-widest px-1.5 py-0.5 rounded bg-blue-600 text-white leading-none">
            AI
          </span>
        </div>
        <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 tracking-tight mt-1">
          Autonomous Title Intelligence
        </span>
      </div>
    </div>
  );
}
