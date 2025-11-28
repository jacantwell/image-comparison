"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { 
  History, 
  PlusCircle, 
  ImageIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";
import ComparisonResult from "@/components/result"
import ComparisonForm from "@/components/form";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ComparePage() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [history, setHistory] = useState<string[]>([]);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Fetch History
  useEffect(() => {
    fetch(API_URL + "/comparisons")
      .then(res => res.json())
      .then(data => {
        setHistory(data); 
      })
      .catch(err => console.error("Failed to fetch history:", err));
  }, [refreshTrigger]);

  const handleNewComparison = useCallback((id: string) => {
    setSelectedId(id);
    setRefreshTrigger(prev => prev + 1); // Refresh sidebar list
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row font-sans">
      
      {/* --- SIDEBAR --- */}
      <aside className="w-full md:w-64 bg-white border-r border-gray-200 shrink-0 h-[300px] md:h-screen flex flex-col">
        <div className="p-4 border-b border-gray-100">
            <Button 
                onClick={() => setSelectedId(null)} 
                variant={selectedId === null ? "default" : "outline"}
                className="w-full justify-start gap-2"
            >
                <PlusCircle className="w-4 h-4" />
                New Comparison
            </Button>
        </div>
        
        <div className="p-4 overflow-y-auto flex-1">
            <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                <History className="w-3 h-3" /> History
            </h2>
            <div className="space-y-1">
                {history.length === 0 && <p className="text-sm text-gray-400 italic">No past comparisons</p>}
                
                {history.map((item) => (
                    <button
                        key={item}
                        onClick={() => setSelectedId(item)}
                        className={cn(
                            "w-full text-left px-3 py-2 rounded-md text-sm transition-colors flex items-center gap-2 truncate",
                            selectedId === item
                                ? "bg-slate-100 text-slate-900 font-medium" 
                                : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                        )}
                    >
                        <ImageIcon className="w-4 h-4 shrink-0 text-gray-400" />
                        <span className="truncate">ID: {item.substring(0, 8)}...</span>
                    </button>
                ))}
            </div>
        </div>
      </aside>

      {/* --- MAIN CONTENT AREA --- */}
      <main className="flex-1 p-4 md:p-8 overflow-y-auto h-screen">
        <div className="max-w-5xl mx-auto">
            <header className="mb-8">
                <h1 className="text-2xl md:text-3xl font-bold text-gray-900">
                    {selectedId ? "Comparison Result" : "New Comparison"}
                </h1>
                <p className="text-gray-500 mt-1">
                    {selectedId 
                        ? `Viewing historical result for ID: ${selectedId}` 
                        : "Upload images to detect differences"}
                </p>
            </header>

            {selectedId ? (
                <ComparisonResult id={selectedId} />
            ) : (
                <ComparisonForm onSuccess={handleNewComparison} />
            )}
        </div>
      </main>
    </div>
  );
}