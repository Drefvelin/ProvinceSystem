"use client";

import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

export type CubeFaces = {
  up: string;
  down: string;
  north: string;
  south: string;
  east: string;
  west: string;
};

export default function SimpleCubeViewer({
  faces,
  variant = "full",
}: {
  faces: CubeFaces;
  /** "thumb" renders a small, non-interactive, borderless preview for use inside a crafting-grid slot. */
  variant?: "full" | "thumb";
}) {
  const mountRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let disposed = false;
    let renderer: THREE.WebGLRenderer | null = null;
    let frameId: number;
    let controls: OrbitControls | null = null;

    async function init() {
      const mount = mountRef.current;
      if (!mount) return;

      const width = mount.clientWidth;
      const height = mount.clientHeight;

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(45, width / height, 0.05, 100);

      renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        preserveDrawingBuffer: true,
      });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setSize(width, height);
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      mount.appendChild(renderer.domElement);

      const texLoader = new THREE.TextureLoader();
      const loadTex = (url: string) =>
        new Promise<THREE.Texture | null>((resolve) => {
          texLoader.load(
            url,
            (tex) => {
              tex.magFilter = THREE.NearestFilter;
              tex.minFilter = THREE.NearestFilter;
              tex.colorSpace = THREE.SRGBColorSpace;
              resolve(tex);
            },
            undefined,
            () => resolve(null)
          );
        });

      // BoxGeometry material group order: px, nx, py, ny, pz, nz
      // Minecraft axes: +x=east, -x=west, +y=up, -y=down, +z=south, -z=north
      const [east, west, up, down, south, north] = await Promise.all([
        loadTex(faces.east),
        loadTex(faces.west),
        loadTex(faces.up),
        loadTex(faces.down),
        loadTex(faces.south),
        loadTex(faces.north),
      ]);
      if (disposed) return;

      const mkMat = (tex: THREE.Texture | null) =>
        new THREE.MeshLambertMaterial({ map: tex ?? undefined, color: tex ? 0xffffff : 0x88a088 });

      const materials = [east, west, up, down, south, north].map(mkMat);
      const geo = new THREE.BoxGeometry(1, 1, 1);
      const mesh = new THREE.Mesh(geo, materials);
      scene.add(mesh);

      camera.position.set(1.3, 1.1, 1.3);
      camera.lookAt(0, 0, 0);

      scene.add(new THREE.AmbientLight(0xffffff, 1.4));
      const dir = new THREE.DirectionalLight(0xffffff, 1.2);
      dir.position.set(3, 5, 2);
      scene.add(dir);
      const dir2 = new THREE.DirectionalLight(0xffffff, 0.6);
      dir2.position.set(-3, 2, -2);
      scene.add(dir2);

      controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.08;
      controls.autoRotate = true;
      controls.autoRotateSpeed = variant === "thumb" ? 3 : 1.2;
      controls.minDistance = 0.8;
      controls.maxDistance = 4;
      if (variant === "thumb") {
        controls.enabled = false;
      }

      function animate() {
        frameId = requestAnimationFrame(animate);
        controls?.update();
        if (renderer) renderer.render(scene, camera);
      }
      animate();

      function handleResize() {
        if (!mount || !renderer) return;
        const w = mount.clientWidth;
        const h = mount.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
      }
      window.addEventListener("resize", handleResize);

      return () => {
        window.removeEventListener("resize", handleResize);
      };
    }

    let cleanupResize: (() => void) | undefined;
    init()
      .then((cleanup) => {
        cleanupResize = cleanup;
      })
      .catch(() => {
        if (!disposed) setError("Could not load model.");
      });

    return () => {
      disposed = true;
      cleanupResize?.();
      if (frameId) cancelAnimationFrame(frameId);
      controls?.dispose();
      if (renderer) {
        renderer.dispose();
        renderer.domElement.remove();
      }
    };
  }, [faces, variant]);

  if (variant === "thumb") {
    return (
      <div
        ref={mountRef}
        className="pointer-events-none relative h-8 w-8 shrink-0 overflow-hidden sm:h-10 sm:w-10"
      >
        {error ? (
          <span className="absolute inset-0 flex items-center justify-center text-[8px] text-[var(--tfmc-mist)]">
            ?
          </span>
        ) : null}
      </div>
    );
  }

  return (
    <div
      ref={mountRef}
      className="relative h-64 w-full overflow-hidden rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest-deep)_60%,transparent)] sm:h-80"
    >
      {error ? (
        <p className="absolute inset-0 flex items-center justify-center text-sm text-[var(--tfmc-mist)]">
          {error}
        </p>
      ) : null}
    </div>
  );
}
