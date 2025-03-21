"use client";

import { useState, useEffect, useRef } from "react";
import { useMapObjects } from "./core/mapengine";

const MapViewer = () => {
  const [mapType, setMapType] = useState<string>("county");
  const [regionData, setRegionData] = useState<Record<string, any> | null>(null);
  const [hoveredColor, setHoveredColor] = useState<string | null>(null);
  const [regionInfo, setRegionInfo] = useState<{
    title: string;
    tier: string;
    size: number;
    subject_size: number;
    overlord: string;
    subjects: string[];
    description: string;
  } | null>(null);
  const [loading, setLoading] = useState<boolean>(true); // Initially true
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const hoveredRegionRef = useRef<HTMLImageElement | null>(null);
  const { mapObjects, loadData, getHoverRegion, drillDownRegion  } = useMapObjects(); // Import hover logic
  const [selectedRegionId, setSelectedRegionId] = useState<string | null>(null);

  // Fetch JSON Data from API when mapType changes
  useEffect(() => {
    const fetchRegionData = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://localhost:8000/data/${mapType}`);
        if (!response.ok) throw new Error("Failed to fetch region data");
        const data = await response.json();
        setRegionData(data);
        loadData(data); // Load the map objects dynamically
      } catch (error) {
        console.error("Error fetching region data:", error);
        setRegionData(null);
      }
      setLoading(false);
    };

    fetchRegionData();
  }, [mapType]);

  useEffect(() => {
    console.log("Map Objects Updated:", mapObjects);
  }, [mapObjects]);

  // Generate overlay image paths
  useEffect(() => {
    if (!regionData) return;
    
    setLoading(true); // Ensure loading stays true while processing overlays
    loadData(regionData);
    console.log(mapObjects);
    setLoading(false); // Done loading once overlays are ready
  }, [regionData, mapType]);

  // 🎨 Draw the map onto the hidden canvas
  useEffect(() => {
    if (loading) return;

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

    setHoveredColor(null);
    setRegionInfo(null);
    drawImage();
  }, [mapType, loading]);

  // 🖱️ Get pixel color & find region in JSON
  const getPixelColor = (event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    if (loading) return;
  
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
    const regionRGB = `${pixel[0]},${pixel[1]},${pixel[2]}`;
    const foundRegion = Object.keys(regionData).find(
      (regionId) => regionData[regionId].rgb === regionRGB
    );
  
    if (!foundRegion) {
      setHoveredColor(null);
      setRegionInfo(null);
      return;
    }
  
    // Get the correct hover image AND region info (fallback to overlord if needed)
    const { imagePath, region } = getHoverRegion(mapType, foundRegion, regionData);

    setHoveredColor(imagePath);
    setSelectedRegionId(foundRegion); // track real region ID for drill-down
  
    if (region) {
      const capitalizedTier = mapType.charAt(0).toUpperCase() + mapType.slice(1);
      const overlordName = region.overlord ? regionData[region.overlord]?.name : null;
  
      setRegionInfo({
        title: region.name,
        tier: capitalizedTier,
        size: region.size,
        subject_size: region.subject_size,
        overlord: overlordName,
        subjects: region.subjects ?? [],
        description: region.description || `A ${capitalizedTier} in Calavorn`,
      });
    }
  };
  

  // Prevent rendering the map while loading
  if (loading) {
    return (
      <div className="w-full flex justify-center items-center min-h-screen bg-gray-100">
        <p className="text-lg font-semibold text-gray-700">Loading Map...</p>
      </div>
    );
  }

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
          <option value="nation">Nation Map</option>
          <option value="county">County Map</option>
          <option value="duchy">Duchy Map</option>
          <option value="kingdom">Kingdom Map</option>
        </select>
      </div>

      {/* Center: Map Viewer */}
      <div
        className="relative w-3/5 max-w-4xl"
        onMouseMove={getPixelColor}
        onClick={() => {
          if (selectedRegionId && regionInfo?.subjects && regionInfo?.subjects.length > 0) {
            drillDownRegion(selectedRegionId, regionData!);
          }
        }}
      >
        <img src={`http://localhost:8000/map`} alt="Base Map" className="w-full h-auto" />
        <canvas ref={canvasRef} className="absolute top-0 left-0 w-full h-auto opacity-0 pointer-events-none" />

        {hoveredColor && <img ref={hoveredRegionRef} src={hoveredColor} alt="Hovered Region" className="absolute top-0 left-0 w-full h-auto opacity-100 pointer-events-none" />}
        {/* Render only images where visible === true */}
        {mapObjects
          .filter((obj) => obj.visible) // Only show visible images
          .map((obj) => (
            <img
              key={obj.id}
              id={obj.id}
              src={`/data/regions/${mapType}/${obj.path}.png`}
              alt={`Overlay ${obj.id}`}
              className="absolute top-0 left-0 w-full h-auto opacity-80 pointer-events-none"
              onError={(e) => (e.currentTarget.style.display = "none")}
            />
        ))}
      </div>

      {/* Right Side: Region Info Panel */}
      <div className="w-1/5">
        {regionInfo && (
          <div className="bg-white shadow-lg rounded-lg p-4 transition-opacity duration-300 ease-in-out">
            <h2 className="text-xl font-bold text-gray-800">{regionInfo.title}</h2>

            {/* Tier Display */}
            <p className="text-md text-gray-400 font-semibold">
              <span className="text-gray-400">Tier:</span> 
              <span className="text-gray-600"> {regionInfo.tier}</span>
            </p>

            {/* Overlord Status */}
            {mapType === "nation" && (
              <p className="text-md text-gray-400 font-semibold">
                <span className="text-gray-400">Type:</span> 
                <span className="text-gray-600"> {regionInfo.overlord ? `Subject of ${regionInfo.overlord}` : "Independent"}</span>
              </p>
            )}

            {/* Realm Size */}
            {mapType === "nation" && (
              <p className="text-md text-gray-400 font-semibold">
                <span className="text-gray-400">Realm Size:</span> 
                <span className="text-gray-600">{regionInfo.subject_size > 0 ? ` ${regionInfo.size} (${regionInfo.subject_size} from subjects)`: ` ${regionInfo.size}`}</span>
              </p>
            )}

            {/* Subjects List (Only if the nation has subjects) */}
            {mapType === "nation" && regionInfo.subjects && regionInfo.subjects.length > 0 && (
              <div className="mt-2">
                <p className="text-md text-gray-400 font-semibold">Subjects:</p>
                <ul className="list-disc list-inside text-gray-600">
                  {regionInfo.subjects.map((subjectId) => {
                    // Lookup the subject's name from regionData, fallback to the ID if not found
                    const subjectName = regionData?.[subjectId]?.name || subjectId;
                    return <li key={subjectId}>{subjectName}</li>;
                  })}
                </ul>
              </div>
            )}
            {/* Description */}
            <p className="text-sm text-gray-500 mt-2">{regionInfo.description}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default MapViewer;
