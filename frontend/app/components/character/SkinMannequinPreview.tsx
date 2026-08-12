"use client";

import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { disposeObject3D, loadTextureFromFile } from "../../../lib/skins/javaModel";
import {
  applySteveArmPose,
  createSteveMannequin,
  inferArmModelFromTexture,
  setSteveOuterLayerVisible,
  type ArmModel,
  type SteveMannequin,
} from "../../../lib/skins/steveMannequin";

type Props = {
  /** Local File or remote blob/object URL for a 64×64 skin PNG. */
  source: File | string | null;
  className?: string;
  onModelDetected?: (model: ArmModel) => void;
};

/**
 * Standing Steve mannequin textured with a player skin (wardrobe / creation).
 */
export default function SkinMannequinPreview({
  source,
  className = "",
  onModelDetected,
}: Props) {
  const hostRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const onModelRef = useRef(onModelDetected);
  onModelRef.current = onModelDetected;

  useEffect(() => {
    const host = hostRef.current;
    if (!host || !source) {
      setError(null);
      if (host) host.replaceChildren();
      return;
    }

    let cancelled = false;
    let renderer: THREE.WebGLRenderer | null = null;
    let steveRoot: SteveMannequin | null = null;
    let steveTexture: THREE.Texture | null = null;
    let raf = 0;

    async function run() {
      setError(null);
      try {
        let file: File;
        if (typeof source === "string") {
          const res = await fetch(source);
          if (!res.ok) throw new Error("Could not load skin texture");
          const blob = await res.blob();
          file = new File([blob], "skin.png", { type: "image/png" });
        } else {
          file = source;
        }
        if (cancelled) return;

        const loaded = await loadTextureFromFile(file);
        steveTexture = loaded.texture;
        if (cancelled) {
          steveTexture.dispose();
          return;
        }

        const detected = inferArmModelFromTexture(steveTexture);
        onModelRef.current?.(detected);
        steveRoot = createSteveMannequin(steveTexture, detected);
        applySteveArmPose(steveRoot, "idle");
        setSteveOuterLayerVisible(steveRoot, true);

        if (cancelled) {
          disposeObject3D(steveRoot);
          return;
        }

        const widthPx = host.clientWidth || 160;
        const heightPx = host.clientHeight || 240;

        renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        renderer.setSize(widthPx, heightPx, false);
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        renderer.setClearColor(0x000000, 0);
        host.replaceChildren(renderer.domElement);
        renderer.domElement.className = "h-full w-full touch-none";
        renderer.domElement.style.display = "block";

        const camera = new THREE.PerspectiveCamera(
          32,
          widthPx / Math.max(heightPx, 1),
          0.1,
          500
        );
        const focus = new THREE.Vector3(0, 14, 0);
        camera.position.set(focus.x + 8, focus.y + 6, focus.z + 38);
        camera.lookAt(focus);

        const scene = new THREE.Scene();
        const amb = new THREE.AmbientLight(0xffffff, 0.85);
        const dir = new THREE.DirectionalLight(0xffffff, 0.55);
        dir.position.set(20, 40, 30);
        scene.add(amb, dir, steveRoot);

        const tick = () => {
          if (cancelled || !renderer || !steveRoot) return;
          steveRoot.rotation.y += 0.008;
          renderer.render(scene, camera);
          raf = window.requestAnimationFrame(tick);
        };
        tick();
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Preview failed");
          host.replaceChildren();
        }
      }
    }

    void run();

    return () => {
      cancelled = true;
      if (raf) window.cancelAnimationFrame(raf);
      if (renderer) {
        renderer.dispose();
        renderer = null;
      }
      if (steveRoot) {
        disposeObject3D(steveRoot);
        steveRoot = null;
      }
      steveTexture?.dispose();
      host.replaceChildren();
    };
  }, [source]);

  return (
    <div
      className={`relative overflow-hidden bg-[color-mix(in_srgb,var(--tfmc-forest)_70%,black)] ${className}`}
    >
      <div ref={hostRef} className="h-full w-full" />
      {!source ? (
        <p className="absolute inset-0 flex items-center justify-center px-2 text-center text-xs text-[var(--tfmc-mist)]">
          No skin
        </p>
      ) : null}
      {error ? (
        <p className="absolute inset-x-0 bottom-1 px-2 text-center text-[10px] text-red-300">
          {error}
        </p>
      ) : null}
    </div>
  );
}
