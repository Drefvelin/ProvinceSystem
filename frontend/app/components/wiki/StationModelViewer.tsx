"use client";

import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

type Face = { uv: [number, number, number, number]; texture: string };

type Element = {
  from: [number, number, number];
  to: [number, number, number];
  rotation?: { angle: number; axis: "x" | "y" | "z"; origin: [number, number, number] };
  faces: Partial<Record<"north" | "south" | "east" | "west" | "up" | "down", Face>>;
};

type BlockModel = {
  texture_size: [number, number];
  elements: Element[];
};

function buildGeometryForElement(el: Element) {
  const [x1, y1, z1] = el.from;
  const [x2, y2, z2] = el.to;
  const sizeX = (x2 - x1) / 16;
  const sizeY = (y2 - y1) / 16;
  const sizeZ = (z2 - z1) / 16;
  const geo = new THREE.BoxGeometry(sizeX, sizeY, sizeZ);

  // BoxGeometry face groups order: px, nx, py, ny, pz, nz
  const order: Array<keyof Element["faces"]> = ["east", "west", "up", "down", "south", "north"];
  const uvAttr = geo.getAttribute("uv") as THREE.BufferAttribute;

  order.forEach((dir, faceIdx) => {
    const face = el.faces[dir];
    const vertOffset = faceIdx * 4;
    if (!face) {
      for (let i = 0; i < 4; i++) uvAttr.setXY(vertOffset + i, 0, 0);
      return;
    }
    // Blockbench stores UV in the classic 0-16 grid regardless of texture_size —
    // texture_size only affects pixel snapping in the editor, not the exported UV scale.
    const [u1, v1, u2, v2] = face.uv;
    const a = u1 / 16;
    const b = 1 - v1 / 16;
    const c = u2 / 16;
    const d = 1 - v2 / 16;
    // BoxGeometry default UV layout per face: (0,1) (1,1) (0,0) (1,0)
    uvAttr.setXY(vertOffset + 0, a, b);
    uvAttr.setXY(vertOffset + 1, c, b);
    uvAttr.setXY(vertOffset + 2, a, d);
    uvAttr.setXY(vertOffset + 3, c, d);
  });
  uvAttr.needsUpdate = true;

  const cx = (x1 + x2) / 2 / 16;
  const cy = (y1 + y2) / 2 / 16;
  const cz = (z1 + z2) / 2 / 16;

  return { geo, center: new THREE.Vector3(cx, cy, cz) };
}

export default function StationModelViewer({
  modelUrl,
  textureUrl,
  variant = "full",
}: {
  modelUrl: string;
  textureUrl: string;
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

      let model: BlockModel;
      try {
        const res = await fetch(modelUrl);
        model = await res.json();
      } catch {
        if (!disposed) setError("Could not load model.");
        return;
      }
      if (disposed) return;

      const width = mount.clientWidth;
      const height = mount.clientHeight;

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(45, width / height, 0.05, 100);
      camera.position.set(1.6, 1.4, 1.6);

      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setSize(width, height);
      renderer.outputColorSpace = THREE.SRGBColorSpace;
      mount.appendChild(renderer.domElement);

      const texLoader = new THREE.TextureLoader();
      const texture = await new Promise<THREE.Texture>((resolve, reject) => {
        texLoader.load(textureUrl, resolve, undefined, reject);
      }).catch(() => null);

      if (texture) {
        texture.magFilter = THREE.NearestFilter;
        texture.minFilter = THREE.NearestFilter;
        texture.colorSpace = THREE.SRGBColorSpace;
      }

      const material = new THREE.MeshLambertMaterial({
        map: texture ?? undefined,
        color: texture ? 0xffffff : 0x88a088,
        side: THREE.DoubleSide,
        transparent: true,
        alphaTest: 0.3,
      });

      const group = new THREE.Group();

      for (const el of model.elements) {
        const { geo, center } = buildGeometryForElement(el);
        const mesh = new THREE.Mesh(geo, material);

        if (el.rotation && el.rotation.angle) {
          const origin = new THREE.Vector3(...el.rotation.origin).multiplyScalar(1 / 16);
          const axis =
            el.rotation.axis === "x"
              ? new THREE.Vector3(1, 0, 0)
              : el.rotation.axis === "y"
                ? new THREE.Vector3(0, 1, 0)
                : new THREE.Vector3(0, 0, 1);
          const rad = (el.rotation.angle * Math.PI) / 180;

          const pivot = new THREE.Object3D();
          pivot.position.copy(origin);
          pivot.rotateOnAxis(axis, rad);
          mesh.position.copy(center).sub(origin);
          pivot.add(mesh);
          group.add(pivot);
        } else {
          mesh.position.copy(center);
          group.add(mesh);
        }
      }

      // Center the group around its bounding box.
      const box = new THREE.Box3().setFromObject(group);
      const boxCenter = box.getCenter(new THREE.Vector3());
      group.position.sub(boxCenter);
      scene.add(group);

      const size = box.getSize(new THREE.Vector3());
      const maxDim = Math.max(size.x, size.y, size.z, 0.5);
      camera.position.set(maxDim * 1.3, maxDim * 1.1, maxDim * 1.3);
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
      controls.minDistance = maxDim * 0.6;
      controls.maxDistance = maxDim * 4;
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
    init().then((cleanup) => {
      cleanupResize = cleanup;
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
  }, [modelUrl, textureUrl, variant]);

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
