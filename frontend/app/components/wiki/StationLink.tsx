import Link from "next/link";
import type { ReactNode } from "react";

import { stations } from "@/app/wiki/data/stations";

export interface StationLinkProps {
  name: string;
  children?: ReactNode;
  className?: string;
}

const linkClass = "text-[var(--tfmc-accent)] underline-offset-2 hover:underline";

/** Link a verified station name to its canonical registered wiki route. */
export default function StationLink({ name, children, className = linkClass }: StationLinkProps) {
  const canonicalName = name === "Weapon Station" ? "Forging Station" : name;
  const station = stations.find((candidate) => candidate.name === canonicalName);

  if (!station) throw new Error(`Unknown station name: ${name}`);

  return (
    <Link href={`/wiki/stations/${station.slug}`} className={className}>
      {children ?? station.name}
    </Link>
  );
}
