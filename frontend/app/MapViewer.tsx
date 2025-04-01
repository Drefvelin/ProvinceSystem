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
    banner: string;
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

  {/* Vote Links Array */}
  const voteLinks = [
    { name: "Website 1", url: "https://example-vote1.com" },
    { name: "Website 2", url: "https://example-vote2.com" },
    { name: "Website 3", url: "https://example-vote3.com" },
  ];
  

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
        banner: region.banner,
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
      <div className="w-full h-16 bg-[#2f3327] sticky top-0 z-50 border-b border-[#2b2218] shadow-md relative flex items-center px-6">
        {/* Logo Inside Header */}
        <div className="ml-auto flex items-center gap-6">
          {/* Patreon Icon with Hover Effect */}
          <a
            href="https://patreon.com/TFMCRP"
            target="_blank"
            rel="noopener noreferrer"
            className="transition-transform transform hover:scale-110"
          >
            <img src="/patreon.png" alt="Patreon" className="h-32 w-auto drop-shadow-md" />
          </a>
          {/* Discord Icon with Hover Effect */}
          <a
            href="https://discord.gg/tfmc"
            target="_blank"
            rel="noopener noreferrer"
            className="transition-transform transform hover:scale-110"
          >
            <img src="/discord.png" alt="Discord" className="h-10 w-auto drop-shadow-md" />
          </a>

          {/* Main Logo */}
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
      <div className="flex flex-row justify-center items-start min-h-screen bg-gradient-to-t from-[#8f8b7e] to-[#bab6ab] p-8 gap-6">
        {/* Center: Map Display */}
        <div
          className="relative w-[90%] max-w-5xl rounded-xl border-12 border-[#2b2218] shadow-lg overflow-hidden"
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
        <div className="w-[18%] space-y-6">
          {/* Vote for TFMC Panel */ }
          <div className="bg-[#657c4c] border border-[#3a2f23] shadow-inner rounded-lg p-5">
            <h2 className="text-lg font-bold text-[#f0eed9] mb-3 tracking-wide">Vote for TFMC</h2>
            <ul className="space-y-2 text-sm">
              {voteLinks.map((link, index) => (
                <li key={index}>
                  <a
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[#f0eed9] hover:text-[#3a2f23] transition"
                  >
                    {link.name}: Vote Here
                  </a>
                </li>
              ))}
            </ul>
            {/* Join Discord Button */}
            <a
              href="https://discord.gg/tfmc"
              target="_blank"
              rel="noopener noreferrer"
              className="block mt-6 p-3 bg-[#948b69] rounded-md shadow-md text-center text-[#f0eed9] font-semibold tracking-wide transition-transform transform hover:scale-105 hover:bg-[#2b2218]"
            >
              Join our Discord to Play!
            </a>
          </div>
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
              <option value="empire">Empire Map</option>
            </select>
          </div>
  
          {/* Region Info Panel */}
          <div
            className={`bg-[#657c4c] border border-[#3a2f23] rounded-lg shadow-md overflow-hidden transition-all duration-500 ${
              regionInfo ? "max-h-[600px] opacity-100 p-5" : "max-h-0 opacity-0 p-0"
            }`}
          >
            {regionInfo && (
              <div className="flex">
                {/* Left: All Text Content */}
                <div className="flex-1 pr-4">
                  <h2 className="text-xl font-bold text-[#e7e2c2]">{regionInfo.title}</h2>
                  <p className="text-md text-gray-200 mt-1">
                    <strong>Tier:</strong> {regionInfo.tier}
                  </p>

                  {mapType === "nation" && (
                    <>
                      <p className="text-md text-gray-200">
                        <strong>Type:</strong>{" "}
                        {regionInfo.overlord ? `Subject of ${regionInfo.overlord}` : "Independent"}
                      </p>
                      <p className="text-md text-gray-200">
                        <strong>Realm Size:</strong>{" "}
                        {regionInfo.subject_size > 0
                          ? `${regionInfo.size} (${regionInfo.subject_size} from subjects)`
                          : regionInfo.size}
                      </p>
                    </>
                  )}

                  {/* Subjects */}
                  {regionInfo.subjects?.length > 0 && (
                    <div className="mt-4">
                      <p className="text-md font-semibold text-gray-100">Subjects:</p>
                      <ul className="list-disc list-inside text-gray-200">
                        {regionInfo.subjects.map((id) => (
                          <li key={id}>{regionData?.[id]?.name || id}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Description */}
                  <p className="text-sm text-gray-200 mt-3">{regionInfo.description}</p>
                </div>

                {/* Right: Flag Image */}
                {regionInfo.banner && (
                  <div className="flex flex-col items-center w-28 mt-1">
                    <img
                      src={`/data/banners/${mapType}/${regionInfo.banner}.png`}
                      alt={`${regionInfo.title} Banner`}
                      className="w-24 h-auto border border-[#3a2f23] rounded-md shadow-md image-render-pixel"
                    />
                    <p className="text-xs text-[#f0eed9] mt-1 text-center">Official Flag</p>
                  </div>
                )}
              </div>
            )}
          </div>
          {/* Drill Stack (Active Layers) */}
          {drillStack.length > 0 && (
            <div className="bg-[#657c4c] border border-[#3a2f23] p-5 rounded-lg shadow-md">
              <h3 className="text-md font-semibold text-[#f0eed9] mb-3">Active Layers</h3>
              <ul className="divide-y divide-[#3a2f23]">
                {drillStack.map((label, index) => (
                  <li key={index} className="py-2 text-sm text-gray-200 flex items-center gap-2">
                    {/* 🔴 Fix: Proper Dot Color */}
                    <span className="inline-block w-2 h-2 bg-[#2b2218] rounded-full"></span>
                    <span>
                      Inspecting
                    </span>
                    <span className="font-medium text-[#c7c185]">{label}</span>
                  </li>
                ))}
              </ul>
              {/* ✅ Fix: Correct Button Background Color */}
              <button
                onClick={() => {
                  setDrillStack([]);
                  if (regionData) loadData(regionData);
                }}
                className="mt-4 w-full bg-[#f0eed9] hover:bg-[#cfcdba] text-gray text-sm font-medium py-2 px-4 rounded-lg shadow transition duration-200"
              >
                Reset View
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MapViewer;
