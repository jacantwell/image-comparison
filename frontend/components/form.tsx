"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { 
  Loader2, 
  Upload, 
  ArrowRight} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";


export default function ComparisonForm({ onSuccess }: { onSuccess: (id: string) => void }) {
  const [beforeImage, setBeforeImage] = useState<File | null>(null);
  const [afterImage, setAfterImage] = useState<File | null>(null);
  const [beforePreview, setBeforePreview] = useState<string>("");
  const [afterPreview, setAfterPreview] = useState<string>("");
  const [comparisonType, setComparisonType] = useState<string>("");
  const [visualisationType, setVisualisationType] = useState<string>("");
  const [sensitivity, setSensitivity] = useState<number>(50);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  
  const [comparisonTypes, setComparisonTypes] = useState<string[]>([]);
  const [visualisationTypes, setVisualisationTypes] = useState<string[]>([]);

  useEffect(() => {
    fetch(API_URL + "/comparisons/comparison_types")
      .then(res => res.json())
      .then(data => setComparisonTypes(data))
      .catch(console.error);

    fetch(API_URL + "/comparisons/visualisation_types")
      .then(res => res.json())
      .then(data => setVisualisationTypes(data))
      .catch(console.error);
  }, []);

  const handleImageUpload = (
    file: File,
    setImage: (file: File) => void,
    setPreview: (url: string) => void
  ) => {
    setImage(file);
    const reader = new FileReader();
    reader.onloadend = () => setPreview(reader.result as string);
    reader.readAsDataURL(file);
  };

  const handleSubmit = async () => {
    if (!beforeImage || !afterImage || !comparisonType || !visualisationType) return;
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("before_image", beforeImage);
      formData.append("after_image", afterImage);
      formData.append("comparison_type", comparisonType);
      formData.append("visualtion_type", visualisationType);
      formData.append("sensitivity", sensitivity.toString());

      const res = await fetch(API_URL + "/comparisons/", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to create comparison");
      }

      const newId = await res.json();
      onSuccess(newId); // Notify parent to switch view
    } catch (error) {
      alert(error instanceof Error ? error.message : "Error creating comparison");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="grid md:grid-cols-2 gap-8">
        {/* Upload Boxes */}
        {[
          { title: "Before Image", preview: beforePreview, setFile: setBeforeImage, setPrev: setBeforePreview },
          { title: "After Image", preview: afterPreview, setFile: setAfterImage, setPrev: setAfterPreview }
        ].map((item, idx) => (
          <div key={idx} className="space-y-3">
            <h3 className="font-semibold text-center text-lg">{item.title}</h3>
            <label className="group relative flex flex-col items-center justify-center w-full h-64 md:h-80 rounded-xl border-2 border-dashed border-gray-300 bg-white hover:bg-gray-50 hover:border-primary/50 transition-all cursor-pointer overflow-hidden">
              {item.preview ? (
                <img src={item.preview} alt={item.title} className="w-full h-full object-contain p-2" />
              ) : (
                <div className="flex flex-col items-center justify-center text-gray-400 group-hover:text-primary transition-colors">
                  <Upload className="w-10 h-10 mb-3" />
                  <p className="text-sm font-medium">Click to upload</p>
                </div>
              )}
              <input
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleImageUpload(file, item.setFile, item.setPrev);
                }}
              />
            </label>
          </div>
        ))}
      </div>

      {/* Controls */}
      <div className="bg-white p-6 rounded-xl shadow-sm border space-y-6 max-w-3xl mx-auto">
        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-medium">Method</label>
            <Select value={comparisonType} onValueChange={setComparisonType}>
              <SelectTrigger><SelectValue placeholder="Select method..." /></SelectTrigger>
              <SelectContent>
                {comparisonTypes.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Visualisation</label>
            <Select value={visualisationType} onValueChange={setVisualisationType}>
              <SelectTrigger><SelectValue placeholder="Select style..." /></SelectTrigger>
              <SelectContent>
                {visualisationTypes.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="space-y-4 pt-2">
            <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Sensitivity</span>
                <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">{sensitivity}%</span>
            </div>
            <Slider value={[sensitivity]} onValueChange={(v) => setSensitivity(v[0])} min={0} max={100} step={1} />
        </div>

        <div className="pt-4 flex justify-center">
          <Button 
            onClick={handleSubmit} 
            size="lg" 
            className="w-full md:w-auto min-w-[200px]"
            disabled={!beforeImage || !afterImage || !comparisonType || !visualisationType || isLoading}
          >
            {isLoading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Processing...</> : <><ArrowRight className="mr-2 h-4 w-4" /> Compare Images</>}
          </Button>
        </div>
      </div>
    </div>
  );
}