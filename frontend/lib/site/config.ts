/** Site-wide dev gate and public links. */

export function isSiteDevGateEnabled(): boolean {
  return process.env.NEXT_PUBLIC_SITE_DEV_GATE === "1";
}

export const SITE_DISCORD_URL = "https://discord.gg/tfmc";
