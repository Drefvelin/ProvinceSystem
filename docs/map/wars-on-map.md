# Wars on the web map

Website-side war visualization only. War **gameplay**, FSM, and export schema live in SimpleFactions: [`../../simplefactions/docs/wars.md`](../../simplefactions/docs/wars.md).

## Shipped (website)

| Layer | Description |
|-------|-------------|
| **Campaign route line** | Axis/path between campaign waypoints from SF `wars` export |
| **Battle pins** | Scheduled battle locations on the map with tooltip metadata |

Data arrives via SimpleFactions nation/war upload and is rendered by MapViewer war overlay components. The website **does not infer** frontlines from territory diffs alone.

## Planned

| Layer | Description | Blocker |
|-------|-------------|---------|
| **Occupation tint** | Contested/occupied province fill on political modes | SF occupation zone export not yet available to the web pipeline |

See [roadmap.md](../roadmap.md).

## Data contract (summary)

From SF war export (see SimpleFactions docs):

- Belligerent nation ids
- Campaign route polyline or waypoint list for the route line layer
- Battle schedule entries with map coordinates for pins
- Occupation zones (planned) - province id lists or RGB masks per belligerent

ProvinceSystem reads war JSON from the same upload/regen path as other map markers. Pipeline detail: [generation.md](./generation.md).

## Rendering rules

- War overlays compose **above** political fills but respect pick-layer separation (hover still uses pick canvas).
- Multiple concurrent wars may each get a `war_{id}` layer key.
- Pins and route lines use muted cartography colours consistent with [overview.md](./overview.md) ink style.

## Staff / public access

War layers follow the same map access rules as the parent `mapId`. Staff-only maps hide war data from players without `tfmc.map.staff`. See [identity/auth-security.md](../identity/auth-security.md).

## See also

- [map/overview.md](./overview.md) - full layer model
- [integrations/simplefactions.md](../integrations/simplefactions.md) - upload and regen contract
