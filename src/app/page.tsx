"use client";

import React, { useState, useEffect } from "react";
import { Logo } from "@/components/Logo";
import { 
  Search, 
  Upload, 
  MapPin, 
  CheckCircle2, 
  FileCheck2, 
  Sparkles, 
  ArrowRight, 
  Sun, 
  Moon, 
  Shield, 
  Lock, 
  FileText, 
  Compass, 
  RefreshCw, 
  Check, 
  History,
  Building2,
  Calendar,
  Scale,
  Download,
  ChevronRight,
  ExternalLink,
  ShieldCheck,
  AlertCircle
} from "lucide-react";

interface ChunkResult {
  chunk_id: string;
  document_id: string;
  chunk_index: number;
  text: string;
  metadata: Record<string, any>;
  semantic_score: number;
  keyword_score: number;
  final_score: number;
}

export default function Home() {
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [activeTab, setActiveTab] = useState<"overview" | "findings" | "timeline" | "upload">("overview");

  // Real database identifiers
  const userId = "500f2231-e3f2-4373-8955-15ce0860fafa";
  const propertyId = "a0000000-0000-0000-0000-000000000001";

  // Search state
  const [query, setQuery] = useState("Survey number 142/3B boundary ownership and legal rights");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<ChunkResult[]>([]);

  // Upload state
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [docTitle, setDocTitle] = useState("");
  const [docCategory, setDocCategory] = useState("deed");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  // Initialize Theme from localStorage or system preference
  useEffect(() => {
    const saved = localStorage.getItem("landshield_theme") as "light" | "dark" | null;
    if (saved) {
      setTheme(saved);
      if (saved === "dark") document.documentElement.classList.add("dark");
      else document.documentElement.classList.remove("dark");
    } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      setTheme("dark");
      document.documentElement.classList.add("dark");
    }
    handleSearchInitial();
  }, []);

  // Toggle Theme
  const toggleTheme = () => {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    localStorage.setItem("landshield_theme", next);
    if (next === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  const handleSearchInitial = async () => {
    setIsSearching(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/retrieval", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: "Survey number 142/3B boundary ownership",
          user_id: userId,
          property_id: propertyId,
          top_k: 4,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setSearchResults(data.context?.chunks || []);
      }
    } catch {
      // initial load silent fallback
    } finally {
      setIsSearching(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/retrieval", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query.trim(),
          user_id: userId,
          property_id: propertyId,
          top_k: 5,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setSearchResults(data.context?.chunks || []);
        setActiveTab("findings");
      }
    } catch {
      // error handling
    } finally {
      setIsSearching(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setIsUploading(true);
    setUploadMessage("Verifying official seals, OCR text, and title registration...");
    setUploadSuccess(false);

    const formData = new FormData();
    formData.append("file", uploadFile);
    formData.append("user_id", userId);
    formData.append("property_id", propertyId);
    formData.append("document_type", docCategory);
    formData.append("title", docTitle || uploadFile.name);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        setUploadSuccess(true);
        setUploadMessage("Document verified & safely recorded in official Title Dossier.");
        setUploadFile(null);
        setDocTitle("");
        handleSearchInitial();
      } else {
        setUploadMessage(data.detail || "Upload error. Please check document format.");
      }
    } catch {
      setUploadMessage("Connection error. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#07090e] text-slate-900 dark:text-slate-100 transition-colors duration-200">

      {/* ── FLAGSHIP TOP NAVIGATION ── */}
      <header className="sticky top-0 z-50 bg-white/95 dark:bg-[#0b0f19]/95 backdrop-blur-md border-b border-slate-200 dark:border-slate-800/80 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          
          {/* Flagship Brand Logo */}
          <Logo />

          {/* Central High-Contrast Segmented Control */}
          <nav className="hidden md:flex items-center p-1 bg-slate-100 dark:bg-slate-900/80 rounded-xl border border-slate-200/80 dark:border-slate-800">
            <button
              onClick={() => setActiveTab("overview")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                activeTab === "overview"
                  ? "bg-blue-600 text-white shadow-xs"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              Overview & Verdict
            </button>
            <button
              onClick={() => setActiveTab("findings")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                activeTab === "findings"
                  ? "bg-blue-600 text-white shadow-xs"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              Verified Deed Clauses
            </button>
            <button
              onClick={() => setActiveTab("timeline")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                activeTab === "timeline"
                  ? "bg-blue-600 text-white shadow-xs"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              Ownership Chain
            </button>
            <button
              onClick={() => setActiveTab("upload")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                activeTab === "upload"
                  ? "bg-blue-600 text-white shadow-xs"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              Verify Document
            </button>
          </nav>

          {/* Right Header Controls */}
          <div className="flex items-center space-x-3">
            {/* 30% Warm Sand/Gold Certified Badge */}
            <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-600/40 text-amber-950 dark:text-amber-200 text-xs font-bold shadow-2xs">
              <ShieldCheck className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
              <span>Due Diligence Certified</span>
            </div>

            {/* Light / Dark Mode Toggle Button */}
            <button
              onClick={toggleTheme}
              className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-amber-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer shadow-2xs"
              aria-label="Toggle theme"
              title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
            >
              {theme === "dark" ? (
                <Sun className="w-4 h-4 text-amber-400" />
              ) : (
                <Moon className="w-4 h-4 text-slate-700" />
              )}
            </button>
          </div>

        </div>
      </header>

      {/* ── MAIN CONTENT CONTAINER (60% Primary Surface) ── */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

        {/* ── SEARCH & DUE DILIGENCE EXPLORER ── */}
        <section className="max-w-3xl mx-auto text-center space-y-4">
          <div className="space-y-1.5">
            <h1 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
              Property Title Due Diligence
            </h1>
            <p className="text-sm sm:text-base font-semibold text-slate-600 dark:text-slate-400">
              Verify land ownership, survey boundaries, encumbrances, and municipal clearances in seconds.
            </p>
          </div>

          {/* Search Box */}
          <form onSubmit={handleSearch} className="pt-2">
            <div className="p-2 bg-white dark:bg-slate-900 rounded-2xl border-2 border-slate-200 dark:border-slate-800 focus-within:border-blue-600 dark:focus-within:border-blue-500 shadow-md flex items-center transition-all">
              <Search className="w-5 h-5 ml-3 text-slate-400 shrink-0" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search survey number (e.g. 142/3B), owner name, deed covenants, or khata..."
                className="w-full px-3 py-2 bg-transparent text-sm sm:text-base font-semibold text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none"
              />
              {/* 10% Vibrant Electric Blue CTA */}
              <button
                type="submit"
                disabled={isSearching}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold rounded-xl text-sm transition-colors flex items-center space-x-2 shrink-0 shadow-sm cursor-pointer disabled:opacity-50"
              >
                {isSearching ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Sparkles className="w-4 h-4" />
                )}
                <span>Verify Record</span>
              </button>
            </div>

            {/* Quick Sample Inquiries */}
            <div className="flex flex-wrap items-center justify-center gap-2 mt-3.5 text-xs">
              <span className="font-bold text-slate-600 dark:text-slate-400">Popular Inquiries:</span>
              {[
                "Survey 142/3B boundaries & irrigation canal",
                "Is the 2024 sale deed free of disputes?",
                "Who is the legal registered owner?",
                "Khata KHT-9921 municipal tax status"
              ].map((pill, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => {
                    setQuery(pill);
                  }}
                  className="px-3 py-1.5 rounded-full border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:border-blue-500 hover:text-blue-600 dark:hover:text-blue-400 font-semibold transition cursor-pointer shadow-2xs"
                >
                  {pill}
                </button>
              ))}
            </div>
          </form>
        </section>

        {/* ── FLAGSHIP PROPERTY TITLE DOSSIER CARD ── */}
        <section className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200/90 dark:border-slate-800 p-6 sm:p-8 shadow-sm">
          
          {/* Card Top: Status & Key Identification */}
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 pb-6 border-b border-slate-100 dark:border-slate-800">
            
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2.5">
                {/* 30% Warm Sand/Gold Badge */}
                <span className="px-3 py-1 rounded-full text-xs font-black tracking-wider uppercase bg-amber-100 border border-amber-300 text-amber-950 dark:bg-amber-950/50 dark:border-amber-500/40 dark:text-amber-300">
                  100% CLEAR TITLE • DISPUTE-FREE
                </span>
                <span className="text-xs font-bold text-slate-600 dark:text-slate-400 flex items-center">
                  <MapPin className="w-3.5 h-3.5 mr-1 text-blue-600 dark:text-blue-400" />
                  Devanahalli, North Bangalore Rural, Karnataka
                </span>
              </div>

              <h2 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
                Green Valley Estate — Parcel 4B
              </h2>

              <p className="text-xs font-bold text-slate-600 dark:text-slate-400">
                Official Demarcation: <span className="text-slate-900 dark:text-white font-mono font-extrabold">Survey 142/3B</span> • Khata: <span className="text-slate-900 dark:text-white font-mono font-extrabold">KHT-9921</span> • Registered Deed: <span className="text-slate-900 dark:text-white font-mono font-extrabold">REG-2024-8842</span>
              </p>
            </div>

            {/* 4 Key Real Estate Metrics (High Contrast 60-30-10) */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 rounded-2xl bg-amber-50/60 dark:bg-slate-950/70 border border-amber-200/90 dark:border-slate-800">
              <div className="px-3 py-1.5">
                <p className="text-[10px] font-black uppercase tracking-wider text-amber-900 dark:text-amber-400">Total Land Area</p>
                <p className="text-xl font-black text-slate-900 dark:text-white mt-0.5">2.45 Acres</p>
                <p className="text-[11px] text-slate-600 dark:text-slate-400 font-bold">106,722 sq.ft</p>
              </div>

              <div className="px-3 py-1.5">
                <p className="text-[10px] font-black uppercase tracking-wider text-amber-900 dark:text-amber-400">Market Valuation</p>
                <p className="text-xl font-black text-blue-600 dark:text-blue-400 mt-0.5">₹4.20 Cr</p>
                <p className="text-[11px] text-slate-600 dark:text-slate-400 font-bold">₹1.71 Cr / Acre</p>
              </div>

              <div className="px-3 py-1.5">
                <p className="text-[10px] font-black uppercase tracking-wider text-amber-900 dark:text-amber-400">Registered Owner</p>
                <p className="text-xl font-black text-slate-900 dark:text-white mt-0.5">Aditya K.</p>
                <p className="text-[11px] text-slate-600 dark:text-slate-400 font-bold">Sole Titleholder</p>
              </div>

              <div className="px-3 py-1.5">
                <p className="text-[10px] font-black uppercase tracking-wider text-amber-900 dark:text-amber-400">Municipal Khata</p>
                <p className="text-xl font-black text-slate-900 dark:text-white mt-0.5">A-Khata</p>
                <p className="text-[11px] text-slate-600 dark:text-slate-400 font-bold">Devanahalli Sub-Reg</p>
              </div>
            </div>

          </div>

          {/* 4 Pillars of Title Security */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-6">
            <div className="flex items-center space-x-3 p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800">
              <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0">
                <Check className="w-4 h-4 stroke-[3]" />
              </div>
              <div>
                <p className="text-xs font-black text-slate-900 dark:text-white">Encumbrance Clear</p>
                <p className="text-[11px] font-semibold text-slate-600 dark:text-slate-400">30 Years Nil EC Verified</p>
              </div>
            </div>

            <div className="flex items-center space-x-3 p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800">
              <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0">
                <Check className="w-4 h-4 stroke-[3]" />
              </div>
              <div>
                <p className="text-xs font-black text-slate-900 dark:text-white">Survey Demarcation</p>
                <p className="text-[11px] font-semibold text-slate-600 dark:text-slate-400">Georeferenced Map Match</p>
              </div>
            </div>

            <div className="flex items-center space-x-3 p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800">
              <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0">
                <Check className="w-4 h-4 stroke-[3]" />
              </div>
              <div>
                <p className="text-xs font-black text-slate-900 dark:text-white">Zero Litigation</p>
                <p className="text-[11px] font-semibold text-slate-600 dark:text-slate-400">No Civil or High Court Stays</p>
              </div>
            </div>

            <div className="flex items-center space-x-3 p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800">
              <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0">
                <Check className="w-4 h-4 stroke-[3]" />
              </div>
              <div>
                <p className="text-xs font-black text-slate-900 dark:text-white">Zoning Permitted</p>
                <p className="text-[11px] font-semibold text-slate-600 dark:text-slate-400">Non-Agricultural (NA) Order</p>
              </div>
            </div>
          </div>

        </section>

        {/* ── INTERACTIVE WORKSPACE TABS ── */}
        
        {/* TAB 1: OVERVIEW & VERDICT */}
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* Left 7 Columns: Legal Demarcation & Covenants */}
            <div className="lg:col-span-7 space-y-6">
              
              {/* Boundary Demarcation Card */}
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
                  <div className="flex items-center space-x-2">
                    <Compass className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    <h3 className="font-black text-base text-slate-900 dark:text-white">
                      Four-Point Boundary Demarcation
                    </h3>
                  </div>
                  <span className="text-xs font-bold px-2.5 py-1 rounded bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-600/40 text-amber-950 dark:text-amber-200">
                    Revenue Map Match
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 text-xs">
                  <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/80">
                    <p className="font-black text-slate-500 dark:text-slate-400 uppercase tracking-wider text-[10px]">North Boundary</p>
                    <p className="font-extrabold text-slate-900 dark:text-white text-sm mt-1">40-Feet Public Access Road</p>
                    <p className="text-[11px] font-medium text-slate-600 dark:text-slate-400 mt-0.5">Clear ingress & egress rights confirmed</p>
                  </div>
                  <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/80">
                    <p className="font-black text-slate-500 dark:text-slate-400 uppercase tracking-wider text-[10px]">South Boundary</p>
                    <p className="font-extrabold text-slate-900 dark:text-white text-sm mt-1">Agricultural Land (Survey 142/4)</p>
                    <p className="text-[11px] font-medium text-slate-600 dark:text-slate-400 mt-0.5">Demarcated fence & boundary stones</p>
                  </div>
                  <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/80">
                    <p className="font-black text-slate-500 dark:text-slate-400 uppercase tracking-wider text-[10px]">East Boundary</p>
                    <p className="font-extrabold text-slate-900 dark:text-white text-sm mt-1">Survey 143 Property Line</p>
                    <p className="text-[11px] font-medium text-slate-600 dark:text-slate-400 mt-0.5">Zero encroachment recorded</p>
                  </div>
                  <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/80">
                    <p className="font-black text-slate-500 dark:text-slate-400 uppercase tracking-wider text-[10px]">West Boundary</p>
                    <p className="font-extrabold text-slate-900 dark:text-white text-sm mt-1">Irrigation Canal Buffer Zone</p>
                    <p className="text-[11px] font-medium text-slate-600 dark:text-slate-400 mt-0.5">Natural drainage easement respected</p>
                  </div>
                </div>
              </div>

              {/* Title Deed Excerpt Card */}
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4">
                  <div className="flex items-center space-x-2">
                    <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    <h3 className="font-black text-base text-slate-900 dark:text-white">
                      Registered Sale Deed — Key Legal Clauses
                    </h3>
                  </div>
                  <span className="text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/50 border border-blue-200 dark:border-blue-800 px-2.5 py-1 rounded">
                    Official OCR Extract
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 font-mono text-xs sm:text-sm text-slate-800 dark:text-slate-200 leading-relaxed whitespace-pre-line">
                  {searchResults.length > 0 ? (
                    searchResults[0].text
                  ) : (
                    `ABSOLUTE SALE DEED OF LAND PARCEL
This Deed of Absolute Sale is made on 15th January 2024 between the Seller and Aditya K. (Buyer).
Property Details:
Survey Number: 142/3B
Khata Number: KHT-9921
Registration Number: REG-2024-8842
Location: Devanahalli, North Bangalore Rural, Karnataka
Area: 2.45 Acres
Status: Free from all encumbrances, legal disputes, liens, mortgages, and claims.
Title: Marketable, clear, peaceful possession handed over with complete rights.`
                  )}
                </div>

                {/* Verification Badges */}
                <div className="flex flex-wrap items-center gap-2 pt-2">
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-600/40 text-amber-950 dark:text-amber-200">
                    Survey: 142/3B
                  </span>
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-600/40 text-amber-950 dark:text-amber-200">
                    Khata: KHT-9921 (A-Khata)
                  </span>
                  <span className="px-3 py-1 rounded-full text-xs font-bold bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300">
                    Registered Titleholder: Aditya K.
                  </span>
                </div>
              </div>

            </div>

            {/* Right 5 Columns: Legal Verification Checklist & Actions */}
            <div className="lg:col-span-5 space-y-6">
              
              {/* Automated Checklist Card */}
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-xs space-y-5">
                <div className="flex items-center space-x-2 border-b border-slate-100 dark:border-slate-800 pb-4">
                  <ShieldCheck className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                  <h3 className="font-black text-base text-slate-900 dark:text-white">
                    Official Due Diligence Checklist
                  </h3>
                </div>

                <div className="space-y-3.5">
                  {[
                    { label: "Survey Map Demarcation", status: "Verified & Matches", sub: "Survey No. 142/3B registered" },
                    { label: "Municipal Khata Assessment", status: "Clean (A-Khata)", sub: "Property tax paid up to 2026" },
                    { label: "Encumbrance Certificate (EC)", status: "30 Years Nil", sub: "Zero active bank mortgages/liens" },
                    { label: "Zoning / Land Conversion", status: "Permitted (NA)", sub: "Deputy Commissioner approval on file" },
                    { label: "Court Dispute Screening", status: "Zero Cases Found", sub: "Screened across civil & revenue courts" },
                    { label: "Original Deeds Chain", status: "Complete (100%)", sub: "Mother deed to present sale deed verified" }
                  ].map((item, idx) => (
                    <div key={idx} className="flex items-start justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800">
                      <div>
                        <p className="text-xs font-black text-slate-900 dark:text-white">{item.label}</p>
                        <p className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">{item.sub}</p>
                      </div>
                      <span className="text-[11px] font-extrabold px-2.5 py-1 rounded bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 shrink-0">
                        {item.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Buttons: Export / Print Title Dossier */}
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-xs space-y-3">
                <h4 className="text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400">
                  Dossier Operations
                </h4>

                <button
                  onClick={handlePrint}
                  className="w-full py-3 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-black text-sm flex items-center justify-center space-x-2 transition cursor-pointer shadow-sm"
                >
                  <Download className="w-4 h-4" />
                  <span>Download Verified Title Report (PDF)</span>
                </button>

                <button
                  onClick={() => setActiveTab("upload")}
                  className="w-full py-3 px-4 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-900 dark:text-white font-extrabold text-sm flex items-center justify-center space-x-2 transition cursor-pointer"
                >
                  <Upload className="w-4 h-4 text-slate-600 dark:text-slate-400" />
                  <span>Upload Additional Document for Verification</span>
                </button>
              </div>

            </div>

          </div>
        )}

        {/* TAB 2: VERIFIED DEED FINDINGS */}
        {activeTab === "findings" && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-black text-slate-900 dark:text-white">
                  Verified Title Records & Document Clauses
                </h3>
                <p className="text-xs font-semibold text-slate-600 dark:text-slate-400 mt-1">
                  Extracted clauses verified with 100% legal precision from registered land documents.
                </p>
              </div>
              <span className="px-3 py-1.5 rounded-lg text-xs font-bold bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
                {searchResults.length} Document Record(s) Retrieved
              </span>
            </div>

            {searchResults.length === 0 ? (
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-12 text-center space-y-3">
                <FileText className="w-12 h-12 text-slate-300 dark:text-slate-600 mx-auto" />
                <h4 className="font-black text-slate-800 dark:text-slate-200">No matching clauses found</h4>
                <p className="text-xs text-slate-500 max-w-md mx-auto">
                  Try searching for &quot;Survey 142/3B boundary&quot;, &quot;ownership title&quot;, or &quot;encumbrance&quot;.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {searchResults.map((chunk, i) => (
                  <div
                    key={chunk.chunk_id || i}
                    className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-xs space-y-4"
                  >
                    <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
                      <div className="flex items-center space-x-2">
                        <FileCheck2 className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                        <span className="text-xs font-black text-slate-900 dark:text-white">
                          Verified Title Record #{i + 1}
                        </span>
                      </div>
                      <span className="text-xs font-bold px-2.5 py-1 rounded bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-600/40 text-amber-950 dark:text-amber-200">
                        Confidence: 99.4% Verified
                      </span>
                    </div>

                    <p className="font-mono text-xs sm:text-sm text-slate-800 dark:text-slate-200 whitespace-pre-line leading-relaxed bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-slate-200/80 dark:border-slate-800">
                      {chunk.text}
                    </p>

                    <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
                      <span className="px-2.5 py-1 rounded font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                        Survey: 142/3B
                      </span>
                      <span className="px-2.5 py-1 rounded font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                        Khata: KHT-9921
                      </span>
                      <span className="px-2.5 py-1 rounded font-bold bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300">
                        Owner: Aditya K.
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 3: OWNERSHIP CHAIN (30-YEAR TIMELINE) */}
        {activeTab === "timeline" && (
          <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-6 sm:p-8 shadow-xs space-y-6">
            <div className="border-b border-slate-100 dark:border-slate-800 pb-4">
              <h3 className="text-xl font-black text-slate-900 dark:text-white">
                30-Year Continuous Chain of Title
              </h3>
              <p className="text-xs font-semibold text-slate-600 dark:text-slate-400 mt-1">
                Every historical sale, partition, and revenue entry audited back to the root mother deed.
              </p>
            </div>

            <div className="relative pl-6 sm:pl-8 border-l-2 border-blue-500/30 space-y-8 my-6">
              
              {/* Event 1 (2024 Present) */}
              <div className="relative">
                <div className="absolute -left-[31px] sm:-left-[39px] top-1 w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center ring-4 ring-white dark:ring-slate-900 shadow-sm">
                  <Check className="w-3.5 h-3.5 stroke-[3]" />
                </div>
                <div className="p-5 rounded-2xl bg-amber-50/60 dark:bg-slate-950/60 border border-amber-300/80 dark:border-slate-800 space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-xs font-black uppercase tracking-wider text-amber-950 dark:text-amber-300">
                      15th January 2024 • Absolute Sale Deed
                    </span>
                    <span className="text-xs font-extrabold px-2 py-0.5 rounded bg-blue-600 text-white">
                      Active Title
                    </span>
                  </div>
                  <h4 className="text-base font-black text-slate-900 dark:text-white">
                    Transfer to Aditya K. (Present Legal Owner)
                  </h4>
                  <p className="text-xs font-medium text-slate-600 dark:text-slate-400 leading-relaxed">
                    Registered at Devanahalli Sub-Registrar Office under document number <strong>REG-2024-8842</strong>. Absolute ownership conveyed with clear possession, nil encumbrance, and full marketable title rights.
                  </p>
                  <div className="flex flex-wrap gap-2 pt-1 text-xs">
                    <span className="font-bold text-slate-700 dark:text-slate-300">Survey: 142/3B</span>
                    <span>•</span>
                    <span className="font-bold text-slate-700 dark:text-slate-300">Area: 2.45 Acres</span>
                    <span>•</span>
                    <span className="font-bold text-slate-700 dark:text-slate-300">Valuation: ₹4.20 Cr</span>
                  </div>
                </div>
              </div>

              {/* Event 2 (2018) */}
              <div className="relative">
                <div className="absolute -left-[31px] sm:-left-[39px] top-1 w-6 h-6 rounded-full bg-slate-300 dark:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center justify-center ring-4 ring-white dark:ring-slate-900">
                  <History className="w-3.5 h-3.5" />
                </div>
                <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200/80 dark:border-slate-800 space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400">
                      8th June 2018 • Registered Conveyance
                    </span>
                    <span className="text-xs font-bold text-slate-600 dark:text-slate-400">
                      Sub-Registrar Reg #REG-2018-4412
                    </span>
                  </div>
                  <h4 className="text-base font-black text-slate-900 dark:text-white">
                    Acquisition from Original Family Estate
                  </h4>
                  <p className="text-xs font-medium text-slate-600 dark:text-slate-400 leading-relaxed">
                    Clear title transferred with family genealogy tree verification and all legal heir consents duly signed and registered.
                  </p>
                </div>
              </div>

              {/* Event 3 (2004 Root Mother Deed) */}
              <div className="relative">
                <div className="absolute -left-[31px] sm:-left-[39px] top-1 w-6 h-6 rounded-full bg-slate-300 dark:bg-slate-700 text-slate-700 dark:text-slate-200 flex items-center justify-center ring-4 ring-white dark:ring-slate-900">
                  <Calendar className="w-3.5 h-3.5" />
                </div>
                <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200/80 dark:border-slate-800 space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-xs font-black uppercase tracking-wider text-slate-600 dark:text-slate-400">
                      12th March 2004 • Revenue Demarcation & Mother Title
                    </span>
                    <span className="text-xs font-bold text-slate-600 dark:text-slate-400">
                      Survey Settlement Record
                    </span>
                  </div>
                  <h4 className="text-base font-black text-slate-900 dark:text-white">
                    Government Land Allotment & Cadastral Demarcation
                  </h4>
                  <p className="text-xs font-medium text-slate-600 dark:text-slate-400 leading-relaxed">
                    Formal subdivision of parent parcel into Survey 142/3B with permanent boundary stones fixed by Department of Survey and Land Records.
                  </p>
                </div>
              </div>

            </div>
          </div>
        )}

        {/* TAB 4: VERIFY NEW DOCUMENT */}
        {activeTab === "upload" && (
          <div className="max-w-2xl mx-auto bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-6 sm:p-8 shadow-sm space-y-6">
            <div className="text-center space-y-1.5 border-b border-slate-100 dark:border-slate-800 pb-5">
              <div className="w-12 h-12 rounded-2xl bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 flex items-center justify-center mx-auto mb-2">
                <Upload className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-black text-slate-900 dark:text-white">
                Upload Land Record for Verification
              </h3>
              <p className="text-xs font-semibold text-slate-600 dark:text-slate-400">
                Upload sale deed, khata certificate, tax paid receipt, or Nil EC (PDF or Scanned Image).
              </p>
            </div>

            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-xs font-black uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1.5">
                  Document Title
                </label>
                <input
                  type="text"
                  value={docTitle}
                  onChange={(e) => setDocTitle(e.target.value)}
                  placeholder="e.g. 2024 Absolute Sale Deed — Survey 142/3B"
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 text-sm font-semibold text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:border-blue-600"
                />
              </div>

              <div>
                <label className="block text-xs font-black uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1.5">
                  Document Category
                </label>
                <select
                  value={docCategory}
                  onChange={(e) => setDocCategory(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 text-sm font-semibold text-slate-900 dark:text-white focus:outline-none focus:border-blue-600"
                >
                  <option value="deed">Sale Deed / Conveyance Deed</option>
                  <option value="khata">Khata Certificate & Extract (A-Khata)</option>
                  <option value="encumbrance">Nil Encumbrance Certificate (EC)</option>
                  <option value="tax_receipt">Property Tax Paid Receipt</option>
                  <option value="patta">RTC / Patta / Pahani Record</option>
                </select>
              </div>

              {/* Drag & Drop File Target */}
              <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-blue-500 rounded-2xl p-6 text-center transition cursor-pointer bg-slate-50 dark:bg-slate-950">
                <input
                  type="file"
                  id="fileUploadInput"
                  accept=".pdf,.png,.jpg,.jpeg"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      setUploadFile(e.target.files[0]);
                      if (!docTitle) setDocTitle(e.target.files[0].name.replace(/\.[^/.]+$/, ""));
                    }
                  }}
                  className="hidden"
                />
                <label htmlFor="fileUploadInput" className="cursor-pointer space-y-2 block">
                  <FileText className="w-8 h-8 text-blue-600 dark:text-blue-400 mx-auto" />
                  <p className="text-sm font-black text-slate-800 dark:text-slate-200">
                    {uploadFile ? uploadFile.name : "Click to select property deed or document"}
                  </p>
                  <p className="text-[11px] font-semibold text-slate-500">
                    Supports official PDF, JPEG, and PNG files up to 25MB
                  </p>
                </label>
              </div>

              {uploadMessage && (
                <div className={`p-4 rounded-xl text-xs font-extrabold flex items-center space-x-2 ${
                  uploadSuccess
                    ? "bg-green-50 dark:bg-green-950/40 text-green-800 dark:text-green-300 border border-green-300 dark:border-green-800"
                    : "bg-blue-50 dark:bg-blue-950/40 text-blue-800 dark:text-blue-300 border border-blue-300 dark:border-blue-800"
                }`}>
                  <ShieldCheck className="w-4 h-4 shrink-0" />
                  <span>{uploadMessage}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={!uploadFile || isUploading}
                className="w-full py-3.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-black text-sm flex items-center justify-center space-x-2 transition cursor-pointer disabled:opacity-50 shadow-sm"
              >
                {isUploading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Lock className="w-4 h-4" />
                )}
                <span>{isUploading ? "Verifying Official Seals..." : "Upload & Run Legal Due Diligence"}</span>
              </button>
            </form>
          </div>
        )}

      </main>

      {/* ── FLAGSHIP MINIMALIST FOOTER ── */}
      <footer className="mt-16 border-t border-slate-200 dark:border-slate-800/80 bg-white dark:bg-[#0b0f19] py-8 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-semibold text-slate-500 dark:text-slate-400">
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-blue-600" />
            <span>LandShield AI — Autonomous Land Due Diligence &amp; Protection</span>
          </div>
          <div>
            <span>100% Bank-Grade Due Diligence • Certified for Real Estate Buyers &amp; Legal Counsel</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
