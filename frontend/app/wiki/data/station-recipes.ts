import { generatedStationRecipes } from "./generated/stationRecipes";
import type { Recipe } from "./types";

// ---------- Server crafting-station recipes ----------

/**
 * Player-facing notes preserved from the hand-written recipes that the server
 * YAML superseded. The YAML is authoritative for the recipe *data*; these are
 * prose the config cannot carry, so they are re-attached by recipe key.
 */
const CURATED_NOTES: Record<string, string> = {
  "gen-instrument-station-flute": "Shift: higher octave.",
  "gen-instrument-station-lute": "Shift: chords.",
  "gen-instrument-station-vielle": "Shift: chords.",
  "gen-instrument-station-trumpet": "Shift: higher octave.",
  "gen-instrument-station-celtic-harp": "Shift: chords.",
  "gen-instrument-station-kalimba": "Shift: chords.",
  "gen-instrument-station-dulcimer": "Shift: chords.",
  "gen-instrument-station-accordion": "Shift: chords.",
  "gen-instrument-station-bagpipe": "Shift: higher octave (same scale, one octave up).",
  "gen-engineer-station-fuel": "Yields 16 fuel per craft.",
  "gen-engineer-station-geiger_counter":
    "The same recipe recharges a dead detector: no need to re-craft the base item.",
};

/**
 * Every recipe read off the server's crafting-station configs, with curated
 * notes applied. This is THE list of station recipes: pages that used to keep
 * their own hand-written copies now select out of this array by key, so a
 * recipe can never be documented twice with two different sets of ingredients.
 */
export const stationRecipes: Recipe[] = generatedStationRecipes.map((recipe) =>
  CURATED_NOTES[recipe.key] ? { ...recipe, note: CURATED_NOTES[recipe.key] } : recipe
);

const byKey = new Map(stationRecipes.map((r) => [r.key, r]));

/**
 * Looks a generated recipe up by key, throwing if it is gone. A page that
 * names a recipe that the server config no longer contains is a build failure,
 * not a silently missing card.
 */
export function stationRecipe(key: string): Recipe {
  const recipe = byKey.get(key);
  if (!recipe) {
    throw new Error(
      `No generated station recipe "${key}". Re-run scripts/build-station-recipes.mjs, ` +
        "or update the caller if the server config dropped it."
    );
  }
  return recipe;
}
