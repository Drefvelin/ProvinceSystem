"use client";

import { useState, useEffect, useRef } from "react";
import { useMapEngine } from "./core/MapEngineContext";

const MapViewer = () => {
  const [mapType, setMapType] = useState<string>("nation");
  const [regionData, setRegionData] = useState<Record<string, any> | null>(null);
  const [hoveredColor, setHoveredColor] = useState<string | null>(null);
  const [selectedRegionId, setSelectedRegionId] = useState<string | null>(null);
  const [regionInfo, setRegionInfo] = useState<{
    title: string;
    tier: string;
    size: number;
    subject_size: number;
    overlord: string;
    subjects: string[];
    description: string;
  } | null>(null);
  const [drillStack, setDrillStack] = useState<string[]>([]);
  const [pendingDrillId, setPendingDrillId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const hoveredRegionRef = useRef<HTMLImageElement | null>(null);

  const { mapObjects, loadData, getHoverRegion, drillDownRegion } = useMapEngine();
  

  // === Fetch Region Data on mapType change ===
  useEffect(() => {
    const fetchRegionData = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://localhost:8000/data/${mapType}`);
        if (!response.ok) throw new Error("Failed to fetch region data");
        const data = await response.json();
        setRegionData(data);
        loadData(data); // ⬅️ context-driven
      } catch (error) {
        console.error("Error fetching region data:", error);
        setRegionData(null);
      }
      setLoading(false);
    };

    fetchRegionData();
  }, [mapType]);

  // === Draw base map on canvas ===
  useEffect(() => {
    if (loading) return;
    const drawImage = async () => {
      try {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        const img = new Image();
        img.src = `/data/${mapType}_map.png`;
        img.onload = () => {
          canvas.width = img.width;
          canvas.height = img.height;
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(img, 0, 0);
        };
        img.onerror = () => console.error("Failed to load base map");
      } catch (e) {
        console.error("Error drawing base image:", e);
      }
    };
    setDrillStack([]);
    setHoveredColor(null);
    setRegionInfo(null);
    drawImage();
  }, [mapType, loading]);

  useEffect(() => {
    if (pendingDrillId && regionData) {
      drillDownRegion(pendingDrillId, regionData);
  
      const region = regionData[pendingDrillId];
      const name = region?.name || pendingDrillId;
  
      setDrillStack(prev =>
        prev.includes(name) ? prev : [...prev, name]
      );
  
      setPendingDrillId(null); // clear
    }
  }, [mapObjects, pendingDrillId, regionData]);

  // === Hover logic (uses getHoverRegion from context) ===
  const getPixelColor = (event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    if (loading || !regionData) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = Math.floor((event.clientX - rect.left) * scaleX);
    const y = Math.floor((event.clientY - rect.top) * scaleY);

    const pixel = ctx.getImageData(x, y, 1, 1).data;
    const regionRGB = `${pixel[0]},${pixel[1]},${pixel[2]}`;

    const foundRegionId = Object.keys(regionData).find(
      (id) => regionData[id].rgb === regionRGB
    );
    if (!foundRegionId) {
      setHoveredColor(null);
      setRegionInfo(null);
      return;
    }

    setSelectedRegionId(foundRegionId);

    const { imagePath, region } = getHoverRegion(mapType, foundRegionId, regionData);
    setHoveredColor(imagePath);

    if (region) {
      const capitalizedTier = mapType.charAt(0).toUpperCase() + mapType.slice(1);
      setRegionInfo({
        title: region.name,
        tier: capitalizedTier,
        size: region.size,
        subject_size: region.subject_size,
        overlord: region.overlord ? regionData[region.overlord]?.name : null,
        subjects: region.subjects ?? [],
        description: region.description || `A ${capitalizedTier} in Calavorn`,
      });
    }
  };

  // === Drill-down click ===
  const getAncestryChain = (regionId: string, data: Record<string, any>): string[] => {
    const chain: string[] = [];
    let currentId: string | null = regionId;
    while (currentId && data[currentId]) {
      chain.push(currentId);
      currentId = data[currentId].overlord || null;
    }
    return chain;
  };

  const handleClick = () => {
    if (!selectedRegionId || !regionData) return;
  
    const nextTargetId = getNextDrillTarget(selectedRegionId, regionData, drillStack);
    if (!nextTargetId) return;
  
    const region = regionData[nextTargetId];
    if (!region?.subjects?.length) return;
  
    const ancestry = getAncestryChain(selectedRegionId, regionData);
    const isInsideStack = ancestry.some(id => drillStack.includes(regionData[id]?.name));
  
    if (!isInsideStack) {
      setDrillStack([]);
      loadData(regionData); // reset visibility
      setPendingDrillId(nextTargetId); // 🧠 drill AFTER reset finishes
      return;
    }
  
    // ✅ Otherwise, drill immediately
    drillDownRegion(nextTargetId, regionData);
  
    const name = region.name || nextTargetId;
    setDrillStack((prev) =>
      prev.includes(name) ? prev : [...prev, name]
    );
  };
  

  const getNextDrillTarget = (
    regionId: string,
    regionData: Record<string, any>,
    drillStack: string[]
  ): string | null => {
    let currentId: string | null = regionId;
  
    while (currentId) {
      const region = regionData[currentId] as {
        name?: string;
        overlord?: string;
      };
      if (!region) return null;
  
      const name = region.name || currentId;

      if(region.overlord){
        const overlord = regionData[region.overlord] as {
          name?: string;
          overlord?: string;
        };
        const overlord_name = overlord.name || currentId;
        if (drillStack.includes(overlord_name)) {
          return currentId; // ✅ Found the next eligible target
        }
      } else if (!drillStack.includes(name)) {
        return currentId; // ✅ Found the next eligible target
      }
  
      currentId = region.overlord || null;
    }
  
    return null; // No suitable target found
  };

  // === Render ===
  if (loading) {
    return (
      <div className="w-full flex justify-center items-center min-h-screen bg-gray-100">
        <p className="text-lg font-semibold text-gray-700">Loading Map...</p>
      </div>
    );
  }

  return (
    <div className="font-serif text-gray-900">
      {/* Sticky Header */}
      <div className="w-full h-16 bg-[#2f3327] sticky top-0 z-50 border-b border-[#2b2218] shadow-md relative">
        {/* Logo Inside Header */}
        <div className="absolute right-6 top-1/2 transform -translate-y-1/2">
          <img src="/logo.png" alt="Logo" className="h-14 w-auto drop-shadow-md" />
        </div>
      </div>
  
      {/* Banner with Logo Overlay */}
      <div className="w-full h-[350px] overflow-hidden relative">
        <img
          src="/background.png"
          alt="Banner"
          className="w-full h-full object-cover object-center opacity-90"
        />
        {/* Logo Overlay Centered */}
        <div className="absolute left-1/9 top-1/2 transform -translate-x-1/2 -translate-y-1/2 opacity-60">
          <img src="/logo.png" alt="Logo" className="h-60 w-auto drop-shadow-lg" />
        </div>
      </div>
  
      {/* Main Layout */}
      <div className="flex flex-row justify-center items-start min-h-screen bg-[#d4cfb4] p-8 gap-10">
        {/* Center: Map Display */}
        <div
          className="relative w-[70%] max-w-5xl rounded-xl border-12 border-[#2b2218] shadow-lg overflow-hidden"
          onMouseMove={getPixelColor}
          onClick={handleClick}
        >
          <img src={`http://localhost:8000/map`} alt="Base Map" className="w-full h-auto" />
          <canvas ref={canvasRef} className="absolute top-0 left-0 w-full h-auto opacity-0 pointer-events-none" />
          {hoveredColor && (
            <img
              ref={hoveredRegionRef}
              src={hoveredColor}
              alt="Hovered Region"
              className="absolute top-0 left-0 w-full h-auto opacity-100 pointer-events-none"
            />
          )}
          {mapObjects
            .filter(obj => obj.visible)
            .map(obj => (
              <img
                key={obj.id}
                src={`/data/regions/${mapType}/${obj.path}.png`}
                alt={`Overlay ${obj.id}`}
                className="absolute top-0 left-0 w-full h-auto opacity-80 pointer-events-none"
                onError={(e) => (e.currentTarget.style.display = "none")}
              />
            ))}
        </div>
  
        {/* Right Panel */}
        <div className="w-[25%] space-y-6">
          {/* Map Mode Selector */}
          <div className="bg-[#657c4c] border border-[#3a2f23] shadow-inner rounded-lg p-5">
            <h2 className="text-lg font-bold text-gray-100 mb-3 tracking-wide">Map Mode</h2>
            <select
              onChange={(e) => setMapType(e.target.value)}
              value={mapType}
              className="w-full p-2 text-md rounded-md border border-[#3a2f23] bg-[#f0eed9] text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#3a2f23] shadow-sm"
            >
              <option value="nation">Nation Map</option>
              <option value="county">County Map</option>
              <option value="duchy">Duchy Map</option>
              <option value="kingdom">Kingdom Map</option>
            </select>
          </div>
  
          {/* Region Info Panel */}
          <div
            className={`bg-[#657c4c] border border-[#3a2f23] rounded-lg shadow-md overflow-hidden transition-all duration-500 ${
              regionInfo ? "max-h-[600px] opacity-100 p-5" : "max-h-0 opacity-0 p-0"
            }`}
          >
            {regionInfo && (
              <>
                <h2 className="text-xl font-bold text-[#e7e2c2]">{regionInfo.title}</h2>
                <p className="text-md text-gray-200 mt-1"><strong>Tier:</strong> {regionInfo.tier}</p>
  
                {mapType === "nation" && (
                  <>
                    <p className="text-md text-gray-200">
                      <strong>Type:</strong> {regionInfo.overlord ? `Subject of ${regionInfo.overlord}` : "Independent"}
                    </p>
                    <p className="text-md text-gray-200">
                      <strong>Realm Size:</strong> {regionInfo.subject_size > 0 ? `${regionInfo.size} (${regionInfo.subject_size} from subjects)` : regionInfo.size}
                    </p>
                  </>
                )}
  
                {regionInfo.subjects?.length > 0 && (
                  <div className="mt-2">
                    <p className="text-md font-semibold text-gray-100">Subjects:</p>
                    <ul className="list-disc list-inside text-gray-200">
                      {regionInfo.subjects.map((id) => (
                        <li key={id}>{regionData?.[id]?.name || id}</li>
                      ))}
                    </ul>
                  </div>
                )}
  
                <p className="text-sm text-gray-200 mt-3">{regionInfo.description}</p>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
  
};

export default MapViewer;
