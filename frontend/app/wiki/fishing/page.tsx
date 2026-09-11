import { DataTable, SeeAlso, WikiPage, WikiSectionHeading } from "@/app/components/wiki";
import CraftingGrid from "@/app/components/wiki/CraftingGrid";
import type { Recipe } from "../data/types";

const rodRecipes: Recipe[] = [
  {key:"fishing-rod",title:"Fishing Rod",station:"Fishing Station",time:10,ingredients:[{name:"Stick",qty:2,texture:"/wiki/textures/vanilla/stick.png"}], output:{name:"Fishing Rod",qty:1,texture:"/wiki/textures/fishing-rods/fishing_rod.png"}},
  {key:"steel-rod",title:"Steel Rod",station:"Fishing Station",time:10,ingredients:[{name:"Steel Ingot",qty:2,texture:"/wiki/textures/materials/steel_ingot.png"},{name:"String",qty:2,texture:"/wiki/textures/vanilla/string.png"}], output:{name:"Steel Rod",qty:1,texture:"/wiki/textures/fishing-rods/steel_rod.png"}, requirement:"Fisher profession"},
  {key:"abyssalite-rod",title:"Abyssalite Rod",station:"Fishing Station",time:10,ingredients:[{name:"Abyssalite Ingot",qty:2,texture:"/wiki/textures/materials/abyssalite_ingot.png"},{name:"String",qty:2,texture:"/wiki/textures/vanilla/string.png"}], output:{name:"Abyssalite Rod",qty:1,texture:"/wiki/textures/fishing-rods/abyssalite_rod.png"}, requirement:"Fisher profession"},
  {key:"mythril-rod",title:"Mythril Rod",station:"Fishing Station",time:10,ingredients:[{name:"Mythril Ingot",qty:2,texture:"/wiki/textures/materials/mythril_ingot.png"},{name:"String",qty:2,texture:"/wiki/textures/vanilla/string.png"}], output:{name:"Mythril Rod",qty:1,texture:"/wiki/textures/fishing-rods/mythril_rod.png"}, requirement:"Fisher profession"},
];

export default function FishingPage() {
  return (
    <WikiPage
      title="Fishing"
      width="lg"
      intro={
        <>
          CustomFishing replaces vanilla fishing with a skill minigame: when something bites, you
          play a timing minigame, and what you get depends on your rod tier, the biome you&apos;re
          fishing in, and any hook and bait you have equipped. Win the minigame and you get the
          loot; lose it and the fish gets away.
        </>
      }
    >
      <WikiSectionHeading id="loop">The basic loop</WikiSectionHeading>
      <ol className="mt-4 flex flex-col gap-2 text-sm text-[var(--tfmc-mist)]">
        <li>1. Get a rod: there are four tiers (below).</li>
        <li>2. Optionally right-click the rod while holding a hook to attach it; right-click the rod again to remove it. Its remaining uses show in the rod&apos;s lore.</li>
        <li>3. Optionally put bait in your off-hand.</li>
        <li>4. Cast normally. The wait for a bite is 5–30 seconds base, and never less than 2.5 s or more than 60 s after every modifier is applied.</li>
        <li>5. When it bites, one of 17 minigames fires, at a difficulty set by your rod tier.</li>
      </ol>

      <WikiSectionHeading
        id="tiers"
        intro="Each rod pairs with one hook. The hook adds durability and shaves time off the wait."
      >
        Rod and hook tiers
      </WikiSectionHeading>
      <DataTable
        className="mt-4"
        minWidth="40rem"
        columns={[
          { header: "Rod", width: "10rem" },
          { header: "Hook" },
          { header: "Hook durability", align: "right" },
          { header: "Wait-time ×", align: "right" },
          { header: "Minigame tier" },
        ]}
        rows={[
          ["Fishing Rod", "Iron Hook", "250 uses", "0.9", "Easy"],
          ["Steel Rod", "Steel Hook", "500 uses", "0.8", "Normal"],
          ["Abyssalite Rod", "Abyssalite Hook", "1000 uses", "0.7", "Hard"],
          ["Mythril Rod", "Mythril Hook", "1500 uses", "0.6", "Very hard"],
        ]}
      />
      <div className="mt-4 grid gap-4 xl:grid-cols-2">{rodRecipes.map(recipe=><CraftingGrid key={recipe.key} recipe={recipe}/>)}</div>

      <SeeAlso hrefs={["/wiki/cooking", "/wiki/materials", "/wiki/commands"]} />
    </WikiPage>
  );
}
