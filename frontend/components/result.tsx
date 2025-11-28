"use-client"

import { useState, useEffect } from "react";
import { 
  Loader2, 
  AlertCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";


const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ComparisonResult({ id }: { id: string }) {
  const [imageUrl, setImageUrl] = useState<string>("");
  const [score, setScore] = useState<number | null>(null); // New State
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    let active = true;
    
    const fetchResult = async () => {
      setLoading(true);
      setError("");
      try {
        const response = await fetch(`${API_URL}/comparisons/${id}`);
        if (!response.ok) throw new Error("Failed to fetch comparison data");
        
        // CHANGED: Parse as JSON instead of Blob
        const data = await response.json();
        
        if (active) {
          // data.image_data is the Base64 string from backend
          setImageUrl(data.image_data); 
          setScore(data.score);
        }
      } catch (err) {
        if (active) setError("Could not load result");
        console.error(err);
      } finally {
        if (active) setLoading(false);
      }
    };

    fetchResult();
  }, [id]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-4 text-gray-500">
        <Loader2 className="w-8 h-8 animate-spin" />
        <p>Loading result...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-96 text-red-500 space-y-2">
        <AlertCircle className="w-8 h-8" />
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in zoom-in duration-300">
      
      <div className="flex justify-center">
        <div className="bg-white px-6 py-3 rounded-full shadow-sm border flex items-center gap-3">
          <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Difference Score</span>
          <div className="h-6 w-px bg-gray-200"></div>
          <span className={`text-xl font-bold ${
            (score || 0) > 90 ? "text-green-600" : 
            (score || 0) > 70 ? "text-yellow-600" : "text-red-600"
          }`}>
            {score !== null ? `${score.toFixed(1)}%` : "N/A"}
          </span>
        </div>
      </div>

      <div className="bg-white p-4 rounded-xl shadow-sm border">
        <div className="relative w-full h-[600px] bg-slate-100 rounded-lg overflow-hidden flex items-center justify-center">
          <img
            src={imageUrl}
            alt={`Comparison ${id}`}
            className="w-full h-full object-contain"
          />
        </div>
      </div>
      
      <div className="flex justify-center">
        <a href={imageUrl} download={`comparison-${id}.png`}>
          <Button variant="outline" size="lg">Download Image</Button>
        </a>
      </div>
    </div>
  );
}