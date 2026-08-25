# Step 76.02 — VF `VehiclePreInteractEvent`

**Depends on:** [76.01](./01-planning-lock.md)  
**Repo:** `vehicleframework`  
**Status:** done (2026-08-24)

## Goal

Add a cancellable Bukkit event fired before default vehicle right-click handling. If cancelled, `VehicleManager` must not open seat selection or run later interact branches for that click.

Authority: [01-planning-lock.md](./01-planning-lock.md#vf-event-contract-7602).

## Tasks

1. Add [`VehiclePreInteractEvent.java`](../../../../vehicleframework/src/main/java/net/tfminecraft/VehicleFramework/Events/VehiclePreInteractEvent.java).
2. Fire from [`VehicleManager.vehicleInteract`](../../../../vehicleframework/src/main/java/net/tfminecraft/VehicleFramework/Managers/VehicleManager.java) after admin `pendingTakeover`, before cooldown/containers/fuel/tow/`seatInteract`.
3. Bump VF version `1.1.7` → `1.1.8` in [`pom.xml`](../../../../vehicleframework/pom.xml).

## Code changes

### Event

- Package: `net.tfminecraft.VehicleFramework.Events.VehiclePreInteractEvent`
- Extends `PlayerEvent`, implements `Cancellable`
- `getVehicle()` → `ActiveVehicle`

### Hook

```java
VehiclePreInteractEvent preInteract = new VehiclePreInteractEvent(p, v);
Bukkit.getPluginManager().callEvent(preInteract);
if (preInteract.isCancelled()) {
    e.setCancelled(true);
    return;
}
```

### Not fired / unchanged

- Clicks on non-vehicle entities
- Passenger-on-vehicle early return
- Pending entity mount flow
- Admin takeover (runs before pre-interact)

## Deploy

```powershell
cd vehicleframework
mvn test
mvn package
```

Copy `target/vehicleframework-1.1.8.jar` to the TFMC libs path. Update [`simplefactions/pom.xml`](../../../../simplefactions/pom.xml) `systemPath` when SF adds a listener (76.05).

## Manual smoke

On dev server with a plugin that registers:

```java
@EventHandler
public void onPreInteract(VehiclePreInteractEvent event) {
    event.setCancelled(true);
    event.getPlayer().sendMessage("Pre-interact cancelled (test).");
}
```

Right-click any vehicle: seat GUI must **not** open; player sees test message.

Remove test listener before 76.05 ships production transfer flow.

## Done when

- [x] `VehiclePreInteractEvent` public in VF 1.1.8
- [x] Cancelled event skips `seatInteract` and prior branches on that click
- [x] `mvn test` and `mvn package` green in `vehicleframework`
- [x] This doc + [00-index](./00-index.md) updated

## Out of scope

- SimpleFactions transfer listener (76.05)
- Automated MockBukkit interact test (deferred; VF has no interact test harness)
