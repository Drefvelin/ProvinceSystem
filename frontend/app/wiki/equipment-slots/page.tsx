import { Callout, DataTable, SeeAlso, StatGrid, WikiPage, WikiSectionHeading } from "@/app/components/wiki";
import { equipmentSlots } from "../data/equipment-slots";

export default function EquipmentSlotsPage() {
  return (
    <WikiPage lastModified="2026-09-11" title="Equipment Slots" intro="Equip one Ring, one Amulet and two Artifacts in the extra slots inside your normal inventory.">
      <WikiSectionHeading id="equip" intro="Match each accessory to the slot with the same item type.">Equip an accessory</WikiSectionHeading>
      <ol className="mt-4 list-decimal space-y-2 pl-5 text-sm text-[var(--tfmc-mist)]"><li>Press E to open your normal inventory.</li><li>Drag and click a matching MMOItems accessory into the matching accessory slot.</li><li>Keep accessories unstacked; stacked items cannot be equipped.</li></ol>
      <DataTable className="mt-4" columns={[{header:"Slot"}]} rows={equipmentSlots.map(x=>[x.slot])} />
      <StatGrid className="mt-4" columns={2} stats={[{label:"Jewelry slots",value:"4"},{label:"Matching catalogue",value:"10 rings · 9 amulets · 11 artifacts"}]} />
      <Callout variant="warning" className="mt-4">These slots replace four ordinary storage spaces. Keep each equipped accessory unstacked.</Callout>
      <SeeAlso hrefs={["/wiki/classes","/wiki/advanced-crafting"]} />
    </WikiPage>
  );
}
