"use client";

import { useState, useEffect, useRef } from "react";

const MapViewer = () => {
  const [mapType, setMapType] = useState<string>("county");
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [imageSrc, setImageSrc] = useState<string | null>(null);

  // Function to fetch and store the map image locally
  const fetchMapImage = async () => {
    try {
      const response = await fetch(`http://localhost:8000/map/png/${mapType}`, {
        mode: "cors", // Ensure CORS is handled properly
      });
  
      if (!response.ok) throw new Error("Failed to fetch image");
  
      const blob = await response.blob(); // Convert response to Blob
      const imageUrl = URL.createObjectURL(blob); // Create object URL
      setImageSrc(imageUrl); // Store image URL for rendering
    } catch (error) {
      console.error("Error loading map image:", error);
    }
  };

  // Function to draw the fetched image onto the canvas
  const drawImageToCanvas = () => {
    if (!imageSrc) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const img = new Image();
    img.src = imageSrc;

    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
    };
  };

  // Function to log RGB color of pixel under cursor
  const getPixelColor = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const pixel = ctx.getImageData(x, y, 1, 1).data; // Get pixel color
    console.log(`RGB: (${pixel[0]}, ${pixel[1]}, ${pixel[2]})`);
  };

  // Fetch the map image when the map type changes
  useEffect(() => {
    fetchMapImage();
  }, [mapType]);

  // Draw the image onto the canvas when the imageSrc is updated
  useEffect(() => {
    drawImageToCanvas();
  }, [imageSrc]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Province Map Viewer</h1>

      {/* Dropdown to Select Map Type */}
      <select
        onChange={(e) => setMapType(e.target.value)}
        value={mapType}
        className="p-3 text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
      >
        <option value="county">County Map</option>
        <option value="duchy">Duchy Map</option>
        <option value="kingdom">Kingdom Map</option>
      </select>

      {/* Map Display Container */}
      <div className="relative w-full max-w-4xl mt-6">
        {/* Base Map (Static Background) */}
        <img
          src="http://localhost:8000/map"
          alt="Base Map"
          className="w-full h-auto"
        />

        {/* Canvas for Hover Detection */}
        <canvas
          ref={canvasRef}
          className="absolute top-0 left-0 w-full h-auto pointer-events-auto"
          onMouseMove={getPixelColor} // Log pixel color on hover
        />
      </div>
    </div>
  );
};

export default MapViewer;
