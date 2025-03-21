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
  const { mapObjects, loadData } = useMapObjects(); // Use mapObjects state

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
    const rgbString = `${pixel[0]}_${pixel[1]}_${pixel[2]}`;
    const regionRGB = `${pixel[0]},${pixel[1]},${pixel[2]}`;
    const foundRegion = Object.values(regionData).find((region: any) => region.rgb === regionRGB);

    if (rgbString === "0_0_0" || !foundRegion) {
      setHoveredColor(null);
      setRegionInfo(null);
      return;
    }

    if (foundRegion) {
      const regionImagePath = `/data/regions/${mapType}/${rgbString}_hover.png`;
      setHoveredColor(regionImagePath);

      const capitalizedTier = mapType.charAt(0).toUpperCase() + mapType.slice(1);
      const overlordName = foundRegion.overlord ? regionData[foundRegion.overlord]?.name : null;

      setRegionInfo({
        title: foundRegion.name,
        tier: capitalizedTier,
        size: foundRegion.size,
        subject_size: foundRegion.subject_size,
        overlord: overlordName,
        subjects: foundRegion.subjects ?? [],
        description: foundRegion.description || `A ${capitalizedTier} in Calavorn`,
      });
    } else {
      setHoveredColor(null);
      setRegionInfo(null);
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
      <div className="relative w-3/5 max-w-4xl" onMouseMove={getPixelColor}>
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
