"use client";

import { useState, useEffect, useRef } from "react";
import { useMapEngine } from "./core/MapEngineContext";

const MapViewer = () => {
  const [mapType, setMapType] = useState<string>("county");
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
    <div className="flex flex-row justify-center items-start min-h-screen bg-gray-100 p-6 gap-6">
      {/* Center: Map Display */}
      <div
        className="relative w-7/8 max-w-4xl"
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

      {/* Right: Info Panel */}
      <div className="w-1/8">
        {/* Left: Map Selector */}
        <div className="bg-white shadow-md rounded-lg p-4">
          <h2 className="text-lg font-bold text-gray-800 mb-2">Map Mode</h2>
          <select
            onChange={(e) => setMapType(e.target.value)}
            value={mapType}
            className="w-full p-2 text-md border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="nation">Nation Map</option>
            <option value="county">County Map</option>
            <option value="duchy">Duchy Map</option>
            <option value="kingdom">Kingdom Map</option>
          </select>
        </div>
        {regionInfo && (
          <div className="mt-6 bg-white shadow-lg rounded-lg p-4">
            <h2 className="text-xl font-bold text-gray-800">{regionInfo.title}</h2>
            <p className="text-md text-gray-500"><strong>Tier:</strong> {regionInfo.tier}</p>
            {mapType === "nation" && (
              <>
                <p className="text-md text-gray-500"><strong>Type:</strong> {regionInfo.overlord ? `Subject of ${regionInfo.overlord}` : "Independent"}</p>
                <p className="text-md text-gray-500"><strong>Realm Size:</strong> {regionInfo.subject_size > 0 ? `${regionInfo.size} (${regionInfo.subject_size} from subjects)` : regionInfo.size}</p>
              </>
            )}
            {regionInfo.subjects?.length > 0 && (
              <div className="mt-2">
                <p className="text-md font-semibold text-gray-600">Subjects:</p>
                <ul className="list-disc list-inside text-gray-700">
                  {regionInfo.subjects.map(id => (
                    <li key={id}>{regionData?.[id]?.name || id}</li>
                  ))}
                </ul>
              </div>
            )}
            <p className="text-sm text-gray-600 mt-2">{regionInfo.description}</p>
          </div>
        )}

        {/* Drill Stack UI */}
        {drillStack.length > 0 && (
          <div className="mt-6 bg-white p-4 rounded-xl shadow-lg border border-gray-200">
            <h3 className="text-md font-semibold text-gray-800 mb-3">Active Layers</h3>

            <ul className="divide-y divide-gray-200">
              {drillStack.map((label, index) => (
                <li
                  key={index}
                  className="py-2 text-sm text-gray-700 flex items-center gap-2"
                >
                  <span className="inline-block w-2 h-2 bg-blue-500 rounded-full"></span>
                  <span>Inspecting <span className="font-medium text-gray-900">{label}</span></span>
                </li>
              ))}
            </ul>

            <button
              onClick={() => {
                setDrillStack([]);
                if (regionData) loadData(regionData);
              }}
              className="mt-4 w-full bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium py-2 px-4 rounded-lg shadow transition duration-200"
            >
              Reset View
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MapViewer;
