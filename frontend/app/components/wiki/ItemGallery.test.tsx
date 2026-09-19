// @vitest-environment jsdom

import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ItemGallery from "./ItemGallery";

const items = [
  { name: "Agate", image: "/agate.png" },
  { name: "Jasper", image: "/jasper.png", detail: "Produces: Armor" },
  { name: "Onyx", image: "/onyx.png" },
];

describe("ItemGallery", () => {
  it("shows one selected preview and supports arrow, Home, and End selection", () => {
    render(<ItemGallery items={items} />);
    const buttons = items.map((item) => screen.getByRole("button", { name: item.name }));

    expect(screen.getByRole("img").getAttribute("alt")).toBe("Agate");
    fireEvent.keyDown(buttons[0], { key: "ArrowRight" });
    expect(screen.getByRole("img").getAttribute("alt")).toBe("Jasper");
    expect(screen.getByText("Produces: Armor")).toBeTruthy();
    fireEvent.keyDown(buttons[1], { key: "End" });
    expect(screen.getByRole("img").getAttribute("alt")).toBe("Onyx");
    fireEvent.keyDown(buttons[2], { key: "Home" });
    expect(screen.getByRole("img").getAttribute("alt")).toBe("Agate");
  });
});
