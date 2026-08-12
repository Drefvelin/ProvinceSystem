# Kit default skins

Default editable-kit PNGs live here as `{skin_png}.png` (for example `knife_skin.png`).

**Production:** RPCharacters uploads these on creation-catalog sync via
`PUT /characters/plugin/kit-skins/{name}` from `plugins/RPCharacters/assets/`.
Do not hand-copy assets onto the website host.

**Local fallbacks:** the API also checks `KIT_SKINS_DIR` and the monorepo path
`Workspace/rpcharacters/src/main/resources/assets/{skin_png}.png` when present.
