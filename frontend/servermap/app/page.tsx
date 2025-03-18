"use client";

import { useState } from "react";

const MapViewer = () => {
  const [mapType, setMapType] = useState<string>("county");

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
          src="http://localhost:8000/map"  // Base Map is always displayed
          alt="Base Map"
          className="w-full h-auto"
        />

        {/* Overlay Map (Foreground) */}
        <img
          src={`http://localhost:8000/map/png/${mapType}`}  // Selected Map (County, Duchy, Kingdom)
          alt={`${mapType} map`}
          className="absolute top-0 left-0 w-full h-auto opacity-80 pointer-events-none"
        />
      </div>
    </div>
  );
};

export default MapViewer;
