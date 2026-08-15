"use client";

import type { CSSProperties, SyntheticEvent } from "react";

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

  if (!url) return null;

  return (
    <img
      key={url}
      src={url}
      alt={alt}
      className={className}
      style={style}
      crossOrigin={crossOrigin}
      ref={(node) => {
        imgRef?.(node);
        if (node?.complete) {
          onLoad?.({ currentTarget: node } as SyntheticEvent<HTMLImageElement>);
        }
      }}
      onLoad={onLoad}
      onError={onError}
    />
  );
}
