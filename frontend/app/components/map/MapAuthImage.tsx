"use client";

import { useEffect, useState, type CSSProperties, type SyntheticEvent } from "react";

import type { MapId } from "./types";
import { useMapAssetUrl } from "@/app/hooks/useMapAssetUrl";

type MapAuthImageProps = {
  mapId: MapId;
  path: string;
  sessionToken?: string | null;
  alt: string;
  className?: string;
  style?: CSSProperties;
  crossOrigin?: "" | "anonymous" | "use-credentials";
  onLoad?: (event: SyntheticEvent<HTMLImageElement>) => void;
  onError?: (event: SyntheticEvent<HTMLImageElement>) => void;
  imgRef?: (node: HTMLImageElement | null) => void;
};

// Only the base map (`/{mapId}/map`) has a low-res preview artifact generated
// alongside it. Overlays, banners, editor pick layers, etc. don't, so this
// intentionally does not match those paths and skips the extra request there.
const BASE_MAP_PATH_RE = /\/map$/;

const FILL_STYLE: CSSProperties = {
  position: "absolute",
  inset: 0,
  width: "100%",
  height: "100%",
};

export default function MapAuthImage({
  mapId,
  path,
  sessionToken,
  alt,
  className,
  style,
  crossOrigin,
  onLoad,
  onError,
  imgRef,
}: MapAuthImageProps) {
  const { url } = useMapAssetUrl(mapId, path, sessionToken, Boolean(path));

  const hasPreview = BASE_MAP_PATH_RE.test(path);
  const previewPath = hasPreview ? `${path}/preview` : "";
  // Fires alongside the full-resolution request above (not after it) so the
  // placeholder never delays the real image. If the preview route 404s or
  // isn't deployed yet, `previewUrl` just stays null and we render exactly
  // what this component rendered before the preview existed.
  const { url: previewUrl } = useMapAssetUrl(
    mapId,
    previewPath,
    sessionToken,
    hasPreview && Boolean(path)
  );

  const [fullLoaded, setFullLoaded] = useState(false);
  const [previewFailed, setPreviewFailed] = useState(false);

  // Reset the crossfade state whenever the underlying asset changes so a map
  // switch doesn't briefly show the previous image's "loaded" state.
  useEffect(() => {
    setFullLoaded(false);
  }, [url]);
  useEffect(() => {
    setPreviewFailed(false);
  }, [previewUrl]);

  if (!url) return null;

  const fullImage = (
    <img
      key={url}
      src={url}
      alt={alt}
      className={hasPreview ? undefined : className}
      style={hasPreview ? { ...FILL_STYLE, zIndex: 1 } : style}
      crossOrigin={crossOrigin}
      ref={(node) => {
        imgRef?.(node);
        if (node?.complete) {
          setFullLoaded(true);
          onLoad?.({ currentTarget: node } as SyntheticEvent<HTMLImageElement>);
        }
      }}
      onLoad={(event) => {
        setFullLoaded(true);
        onLoad?.(event);
      }}
      onError={onError}
    />
  );

  if (!hasPreview) {
    return fullImage;
  }

  const showPlaceholder = Boolean(previewUrl) && !previewFailed;

  return (
    <div className={className} style={{ ...style, position: "relative" }}>
      {showPlaceholder && (
        <img
          key={previewUrl}
          src={previewUrl ?? undefined}
          alt=""
          aria-hidden="true"
          crossOrigin={crossOrigin}
          style={{
            ...FILL_STYLE,
            zIndex: 0,
            opacity: fullLoaded ? 0 : 1,
            transition: "opacity 150ms ease-out",
          }}
          // A placeholder that fails to load (404, network error, etc.) should
          // never surface as a broken-image icon or a visible flash — just
          // stop rendering it and fall back to today's plain full-image path.
          onError={() => setPreviewFailed(true)}
        />
      )}
      {fullImage}
    </div>
  );
}
