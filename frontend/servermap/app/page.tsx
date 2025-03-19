"use client";

import { useState, useEffect, useRef } from "react";

const MapViewer = () => {
  const [mapType, setMapType] = useState<string>("county");
  const [regionData, setRegionData] = useState<Record<string, any> | null>(null); // JSON Data
  const [hoveredColor, setHoveredColor] = useState<string | null>(null);
  const [regionInfo, setRegionInfo] = useState<{ title: string; tier: string; description: string } | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const hoveredRegionRef = useRef<HTMLImageElement | null>(null);

  // 📡 Fetch JSON Data from API when mapType changes
  useEffect(() => {
    const fetchRegionData = async () => {
      try {
        const response = await fetch(`http://localhost:8000/data/${mapType}`);
        if (!response.ok) throw new Error("Failed to fetch region data");
        const data = await response.json();
        setRegionData(data);
      } catch (error) {
        console.error("Error fetching region data:", error);
        setRegionData(null);
      }
    };

    fetchRegionData();
  }, [mapType]);

  // 🎨 Draw the map onto the hidden canvas
  useEffect(() => {
    const drawImage = async () => {
      try {
        const imageUrl = `/data/${mapType}_map.png`;

        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        const img = new Image();
        img.src = imageUrl;
        img.onload = () => {
          canvas.width = img.width;
          canvas.height = img.height;
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.globalAlpha = 1.0;
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        };

        img.onerror = () => {
          console.error("Failed to load image:", imageUrl);
        };
      } catch (error) {
        console.error("Error loading overlay image:", error);
      }
    };

    drawImage();
  }, [mapType]);

  // 🖱️ Get pixel color & find region in JSON
  const getPixelColor = (event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    const canvas = canvasRef.current;
    if (!canvas || !regionData) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const x = Math.floor((event.clientX - rect.left) * scaleX);
    const y = Math.floor((event.clientY - rect.top) * scaleY);

    const pixel = ctx.getImageData(x, y, 1, 1).data;
    const rgbString = `${pixel[0]}_${pixel[1]}_${pixel[2]}`;
    const regionRGB = `${pixel[0]},${pixel[1]},${pixel[2]}`;
    const foundRegion = Object.values(regionData).find((region: any) => region.rgb === regionRGB);
    // Ignore black pixels (0,0,0) and transparent pixels (alpha = 0)
    if (rgbString === "0_0_0" || !foundRegion) {
      setHoveredColor(null);
      setRegionInfo(null);
      return;
    }
    

    if (foundRegion) {
      const regionImagePath = `/data/regions/${rgbString}_hover.png`;
      setHoveredColor(regionImagePath);

      const capitalizedTier = mapType.charAt(0).toUpperCase() + mapType.slice(1);

      setRegionInfo({
        title: foundRegion.name,
        tier: capitalizedTier, // Use the copied & capitalized string
        description: foundRegion.description || `A ${capitalizedTier} in Calavorn`,
      });
    } else {
      setHoveredColor(null);
      setRegionInfo(null);
    }
  };

  return (
    <div className="flex flex-row justify-center items-start min-h-screen bg-gray-100 p-6 gap-6">
      {/* Left Side: Map Mode Selector */}
      <div className="w-1/5 bg-white shadow-md rounded-lg p-4">
        <h2 className="text-lg font-bold text-gray-800 mb-2">Map Mode</h2>
        <select
          onChange={(e) => setMapType(e.target.value)}
          value={mapType}
          className="w-full p-2 text-md border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="county">County Map</option>
          <option value="duchy">Duchy Map</option>
          <option value="kingdom">Kingdom Map</option>
        </select>
      </div>

      {/* Center: Map Viewer */}
      <div className="relative w-3/5 max-w-4xl" onMouseMove={getPixelColor}>
        {/* Base Map */}
        <img
          src={`http://localhost:8000/map`}
          alt="Base Map"
          className="w-full h-auto"
        />

        {/* Overlay Map */}
        <img
          src={`http://localhost:8000/map/${mapType}`}
          alt={`${mapType} map`}
          className="absolute top-0 left-0 w-full h-auto opacity-80 pointer-events-none"
        />

        {/* 🔹 Hidden Canvas (Used for Pixel Checking) */}
        <canvas
          ref={canvasRef}
          className="absolute top-0 left-0 w-full h-auto opacity-0 pointer-events-none"
        />

        {/* 🖼️ Hovered Region Overlay */}
        {hoveredColor && (
          <img
            ref={hoveredRegionRef}
            src={hoveredColor}
            alt="Hovered Region"
            className="absolute top-0 left-0 w-full h-auto opacity-100 pointer-events-none"
          />
        )}
      </div>

      {/* Right Side: Region Info Panel */}
      <div className="w-1/5">
        {regionInfo && (
          <div className="bg-white shadow-lg rounded-lg p-4 transition-opacity duration-300 ease-in-out">
            <h2 className="text-xl font-bold text-gray-800">{regionInfo.title}</h2>
            <p className="text-md text-gray-400 font-semibold">
              <span className="text-gray-400">Tier:</span> <span className="uppercase text-gray-600">{regionInfo.tier}</span>
            </p>
            <p className="text-sm text-gray-500 mt-2">{regionInfo.description}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default MapViewer;
