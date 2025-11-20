# ProvinceSystem
ProvinceSystem is a two-part system for displaying nation borders for the TFMC server, consisting of a Python backend (image generation and data processing) and a Next.js frontend (interactive map display).

The system is not designed to be run locally, so no startup guide is included. You can view the live map here:  
https://www.tfminecraft.net/

## Why This Project Is Interesting
This project uses an unusual but effective technique to generate natural-looking world borders for the TFMC Minecraft server.

- **Python Backend** - Receives JSON input from the [SimpleFactions](https://github.com/Drefvelin/simplefactions) plugin and generates multiple map layers used by the frontend. It also enriches the incoming JSON by reconstructing hierarchical structures (such as nested subjects) that are intentionally omitted to avoid redundancy.
- **Next.js Frontend** - Renders the generated images and provides an interactive map. Players can drill down into subjects, hover to reveal region information, and explore multiple layers of territorial data.

This was my first major web project outside of university coursework. It allowed me to solve a real-world problem in my plugin ecosystem: generating and displaying dynamic borders without manual image editing. While there are architectural decisions I would now improve (such as containerization and production builds), the core ideas-image-based territory generation, data reconstruction, and an interactive web map-are both functional and technically interesting.

## Features
- Python loaders that parse incoming JSON and compile it into in-memory representations, along with map generators that create image layers  
  ([loader](backend/src/scripts/loader/), [mapgen](backend/src/scripts/mapgen/))
- Banner generator that creates images from JSON data or generates random banners  
  ([bannergen](backend/src/scripts/bannergen/))
- Interactive frontend map composed of multiple layered PNGs, with drill-down logic and hover detection  
  ([MapViewer.tsx](frontend/app/MapViewer.tsx), [MapEngineContext.tsx](frontend/app/core/MapEngineContext.tsx))

## Technical Overview
- **Python 3.x**, **FastAPI**, **Pillow** (image generation)
- **Next.js**, **React**, **Node.js**
- Uses **Nginx** for serving image files and exposing API endpoints
- Communicates with the SimpleFactions plugin through REST

### Architecture
- The backend receives JSON data from the Java plugin, compiles hierarchical faction relationships, and generates updated map layers.
- Generated images are written directly into the frontend directory so that the Next.js application can serve and update them immediately.
- The frontend loads these layers, composes them into a single rendered map, and provides hover and click interactions through a custom MapEngine.

## Key Challenges Solved

### Image Transfer
Sending images through API endpoints introduced CORS and middleware issues that were difficult to solve at the time. I opted for direct filesystem writes into the frontend directory, which ensured reliability and simplicity.  
When switching TFMC to HTTPS, browsers initially refused to load updated images due to caching rules, so I configured Nginx endpoints to correctly serve the generated files and prevent stale data from persisting.

### Hover Detection and Drill-Down Logic
I wanted an interactive map where hovering over a region would reveal its name and allow drilling into sub-regions. My first implementation used a single PNG, which made it impossible to determine which province was under the cursor.

To solve this, I:
- Generated a hidden “region-color” canvas with unique RGB values for each province.
- Performed RGB lookups on hover to determine the active region.
- Split the map into multiple per-region PNG layers instead of one monolithic image.

This redesign enabled the drill-down mechanic and greatly improved clarity and performance.

## AI Tools
I used **ChatGPT** extensively throughout this project. I was unfamiliar with technologies in the stack (FastAPI, Nginx, Next.js), so AI assistance helped me understand syntax and generate boilerplate code.

Almost every component includes some AI-assisted sections, but the architectural decisions, data model design, and overall system concept were my own. **ChatGPT** was also used to help refine this README.
