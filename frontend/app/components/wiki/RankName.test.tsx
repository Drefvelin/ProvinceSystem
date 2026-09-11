// @vitest-environment node
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import RankName from "./RankName";

describe("RankName", () => {
  it.each(["Noble", "Gilded", "Ascended"] as const)("links %s to the supporter page", (rank) => {
    const html = renderToStaticMarkup(<RankName rank={rank} />);
    expect(html).toContain('href="https://patreon.com/c/tfmcrp"');
    expect(html).toContain('target="_blank"');
    expect(html).toContain('rel="noopener noreferrer"');
    expect(html).toContain(`aria-label="${rank}"`);
  });

  it.each(["Commoner", "Legacy"] as const)("keeps %s as unlinked styled text", (rank) => {
    const html = renderToStaticMarkup(<RankName rank={rank} />);
    expect(html).not.toContain("<a ");
    expect(html).toContain(`aria-label="${rank}"`);
  });
});
