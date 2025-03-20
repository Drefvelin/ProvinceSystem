let mapObjects: { id: string; visible: boolean }[] = [];

const createMapObjects = (regionData: Record<string, any>): { id: string; visible: boolean }[] => {
  return Object.keys(regionData).map((regionId) => ({
    id: regionId, // Use the region's ID
    visible: true, // Default to visible (you can modify this logic)
  }));
};

export function loadData(regionData: any) {
  mapObjects = createMapObjects(regionData); // Update mapObjects
}

export default mapObjects;



