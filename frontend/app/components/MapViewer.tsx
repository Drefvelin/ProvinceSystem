"use client";

import { useState, useEffect, useRef } from "react";
import { useMapEngine } from "../core/MapEngineContext";
import { useMapHover } from "../hooks/useMapHover";
import { useMapModeData } from "../hooks/useMapModeData";
import { useGuildCache } from "../hooks/useGuildCache";

type MapViewerProps = {
  mapId: "main" | "dev";
};

const MAP_BOUNDS: Record<string, number> = {
  main: 4096,
  dev: 6400,
};

const MapViewer = ({ mapId }: MapViewerProps) => {

  //TODO GOD PLEASE SOMEONE FIX THIS MESS IT NEEDS TO BE SEPARATED DEAR GOD HELP

  const [mapType, setMapType] = useState<string>("nation");
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

  const mapDisplayName = mapId === "dev" ? "Adavaar" : "Calavorn";

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const hoveredRegionRef = useRef<HTMLImageElement | null>(null);

  const lastProvinceIdRef = useRef<number | null>(null);

  const guildNameCacheRef = mapId === "dev" ? useGuildCache(mapId) : null;

  const [cursorTooltip, setCursorTooltip] = useState<{
    x: number;
    y: number;
    text: string;
  } | null>(null);

  const {
    mapObjects,
    loadData,
    resetMapObjects,
    getHoverRegion,
    drillDownRegion,
  } = useMapEngine();
  const { regionData, loading } = useMapModeData({
    mapId,
    mapType,
    loadData,
  });

  

  {/* Vote Links Array */}
  const voteLinks = [
    { name: "MinecraftServers", url: "https://tinyurl.com/23bw2ce4" },
    { name: "Best Minecraft Servers", url: "https://tinyurl.com/2fpz37ru" },
    { name: "Minecraft Server List", url: "https://tinyurl.com/2pcase24" },
    { name: "Minecraft Menu", url: "https://tinyurl.com/a6nm8bb4" },
    { name: "Minecraft-MP", url: "https://tinyurl.com/mr2x4fzk" },
    { name: "Minebrowse", url: "https://tinyurl.com/5f8pnddn" },
    { name: "PlanetMinecraft", url: "https://tinyurl.com/yc5av8rd" },
  ];

  useEffect(() => {
      if (!pendingDrillId || !regionData) return;

      // Perform delayed drill-down
      drillDownRegion(pendingDrillId, regionData);

      const region = regionData[pendingDrillId];
      const name = region?.name || pendingDrillId;

      setDrillStack([name]);

      // Clear pending state
      setPendingDrillId(null);
    }, [pendingDrillId, regionData, drillDownRegion]);

  // === Draw base map on canvas ===
  useEffect(() => {
    if (loading) return;

    const drawImage = async () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      const img = new Image();
      img.crossOrigin = "anonymous";
      img.src = `${process.env.NEXT_PUBLIC_API_URL}/${mapId}/mapdata/${mapType}`;
      img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
      };
    };

    setCursorTooltip(null);
    
    setDrillStack([]);
    setHoveredColor(null);
    setRegionInfo(null);
    drawImage();
  }, [mapId, mapType, loading]);

  // === Hover logic ===
  const { onMouseMove } = useMapHover({
    mapId,
    mapType,
    loading,
    regionData,
    canvasRef,
    guildNameCacheRef,
    setCursorTooltip,
    setHoveredColor,
    setRegionInfo,
    setSelectedRegionId,
    getHoverRegion,
    mapDisplayName,
  });

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
          onMouseMove={onMouseMove}
          onMouseLeave={() => {
            setCursorTooltip(null);
            setHoveredColor(null);
            setRegionInfo(null);
            lastProvinceIdRef.current = null;
          }}
          onClick={handleClick}
        >
          {cursorTooltip && (
            <div
              className="fixed z-50 pointer-events-none bg-[#2b2218] text-[#f0eed9] text-sm px-3 py-1 rounded-md shadow-lg whitespace-pre-line"
              style={{
                left: cursorTooltip.x + 12,
                top: cursorTooltip.y + 12,
              }}
            >
              {cursorTooltip.text}
            </div>
          )}
          <img src={`${process.env.NEXT_PUBLIC_API_URL}/${mapId}/map`} alt="Base Map" className="w-full h-auto" />
          <canvas ref={canvasRef} className="absolute top-0 left-0 w-full h-auto opacity-0 pointer-events-none" />
          {/* Terrain / Fertility Overlay */}
          {(mapType === "terrain" || mapType === "fertility" || mapType === "prosperity") && (
            <img
              src={`${process.env.NEXT_PUBLIC_API_URL}/${mapId}/mapdata/${mapType}`}
              alt={`${mapType} overlay`}
              className="absolute top-0 left-0 w-full h-auto opacity-80 pointer-events-none"
            />
          )}
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
                crossOrigin="anonymous"
                src={`${process.env.NEXT_PUBLIC_API_URL}/${mapId}/regions/${mapType}/${obj.path}`}
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
              onChange={(e) => {
                resetMapObjects();
                setMapType(e.target.value);
              }}
              value={mapType}
              className="w-full p-2 text-md rounded-md border border-[#3a2f23] bg-[#f0eed9] text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#3a2f23] shadow-sm"
            >
              <option value="nation">Nation Map</option>
              <option value="county">County Map</option>
              <option value="duchy">Duchy Map</option>
              <option value="kingdom">Kingdom Map</option>
              <option value="empire">Empire Map</option>
              {mapId === "dev" && (
                <>
                  <option value="trade">Trade</option>
                  <option value="prosperity">Prosperity</option>
                  <option value="terrain">Terrain</option>
                  <option value="fertility">Fertility</option>
                </>
              )}
            </select>
          </div>
  
          {/* Region Info Panel */}
          <div
            className={`bg-[#657c4c] border border-[#3a2f23] rounded-lg shadow-md overflow-hidden transition-all duration-500 ${
              regionInfo ? "max-h-[600px] opacity-100 p-5" : "max-h-0 opacity-0 p-0"
            }`}
          >
            {mapType !== "terrain" && mapType !== "fertility" && regionInfo && (
              <div className="flex">
                {/* Left: All Text Content */}
                <div className="flex-1 pr-4">
                  <h2 className="text-xl font-bold text-[#e7e2c2]">{regionInfo.title}</h2>
                  <p className="text-md text-gray-200 mt-1">
                    <strong>{mapType === "trade" ? "Type:" : "Tier:"}</strong> {regionInfo.tier}
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
                      src={`${process.env.NEXT_PUBLIC_API_URL}/${mapId}/banners/${mapType}/${regionInfo.banner}.png`}
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
