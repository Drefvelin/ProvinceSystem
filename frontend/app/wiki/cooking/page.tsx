import {
  DataTable,
  SeeAlso,
  WikiPage,
  WikiSectionHeading,
} from "@/app/components/wiki";
import { WikiItemLink, WikiItemText } from "@/app/components/wiki";

const furnitureLink = (name: string, piece: string) => (
  <WikiItemLink name={name} key={piece}>{name}</WikiItemLink>
);

const itemLink = (name: string) => <WikiItemLink name={name}>{name}</WikiItemLink>;

export default function CookingPage() {
  return (
    <WikiPage
      title="Cooking"
      width="lg"
      intro={
        <>
          <WikiItemText text="Cooking has no menu and no crafting table. It is a set of real furniture props you place in the world: a pan, a pot, a cutting board, an oven, a milling stone, a fire pit with a spit, a butter churn, a sausage maker. Put ingredients on them, work the station, and the food item you get back tracks its own freshness, cooked state, seasoning and a 1–5 star quality rating: all shown in the item's name and lore. There is nothing to type; everything is a right-click." />
        </>
      }

    >
      <WikiSectionHeading id="loop" intro="The furniture and the two clicks that drive every station.">
        The basic loop
      </WikiSectionHeading>
      <ol className="mt-4 flex flex-col gap-2 text-sm text-[var(--tfmc-mist)]">
        <li>1. <WikiItemText text="Place the furniture you need: Frying Pan, Pot, Cutting Board, Fire Pit, Milling Stone, Mixing Bowl, Oven Bottom + Oven Top with a Bread Tray, Butter Churn, Sausage Maker, Meat Hook, or a plain vanilla Cauldron." /></li>
        <li>2. <strong>Right-click the furniture while holding an ingredient</strong> to place it into one of the furniture&apos;s slots.</li>
        <li>3. <strong>Right-click with an empty hand</strong> to take the item back out, or to operate the station (churn, turn the spit, stir).</li>
        <li>4. Stations that need heat (the <WikiItemLink name="Frying Pan" />) only cook while a heat source sits underneath: the server&apos;s only configured chain is an <WikiItemLink name="Oven Bottom" /> (heat source) under an <WikiItemLink name="Oven Top" />.</li>
        <li>5. Cooking ticks once per second, so every time listed below is in real seconds, not ticks.</li>
      </ol>

      <WikiSectionHeading id="stations" intro="What to hold and what happens at each station.">
        Station by station
      </WikiSectionHeading>
      <DataTable
        className="mt-4"
        minWidth="46rem"
        columns={[
          { header: "Station", width: "10rem" },
          { header: "Held item / action" },
          { header: "Result" },
        ]}
        rows={[
          [
            furnitureLink("Cutting Board", "cutting_board"),
            <WikiItemText key="cutting-knife" text="Hold the Cutting Knife and interact" />,
            "Runs a cutting/chopping recipe on up to 4 slots at once: all 4 must be the same ingredient.",
          ],
          [furnitureLink("Frying Pan", "frying_pan"), "Place food, needs heat below; take out by hand", "Cooks over time; burns if left on too long."],
          [furnitureLink("Pot", "pot"), <WikiItemText key="water-bucket" text="Add a Water Bucket, then cut vegetables" />, "Makes boiled foods and soups."],
          [
            furnitureLink("Fire Pit", "fire_pit"),
            <WikiItemText key="fire-pit-turner" text="Put a roast on the spit, then right-click with the Fire Pit Turner" />,
            "Rotates and roasts a whole joint (chicken, beef, venison).",
          ],
          [<>{furnitureLink("Meat Hook", "meat_hook")} + {itemLink("Cutting Knife")}</>, "Carve a cooked roast", "Yields cuts one at a time, in a fixed order."],
          [
            furnitureLink("Milling Stone", "milling_stone"),
            "Insert 8 Wheat, then perform 4 revolutions",
            <WikiItemText key="flour-output" text="1 batch of Flour, over 60 ticks (3 s)." />,
          ],
          [
            furnitureLink("Mixing Bowl", "mixing_bowl"),
            <WikiItemText key="mixing-inputs" text="Add Flour + Cup of Water + Yeast, then stir 3 times" />,
            <WikiItemText key="dough-output" text="Dough (10 ticks per stir)." />,
          ],
          [
            <>{furnitureLink("Bread Tray", "bread_tray")} (in an Oven)</>,
            <WikiItemText key="bread-input" text="Fill both moulds with Dough, light the oven with logs" />,
            "2 Bread per mould.",
          ],
          [
            furnitureLink("Butter Churn", "butter_churn"),
            <WikiItemText key="milk-input" text="Right-click with a Milk Bucket to load it, then repeatedly right-click the stick" />,
            <WikiItemText key="butter-output" text="3 churns deliver Butter onto a carried Butter Plate." />,
          ],
          [furnitureLink("Sausage Maker", "sausage_maker"), "Feed 3 meats, then crank", <WikiItemText key="sausage-output" text="A Sausage Chain you carve for 5 sausages." />],
          [
            "Cauldron (vanilla block)",
            "Right-click while holding a sauce or soup item",
            "Empties/serves the liquid.",
          ],
        ]}
      />

      <WikiSectionHeading id="cutting-board" intro={<>Every recipe the <WikiItemLink name="Cutting Board" /> can run.</>}>
        <WikiItemLink name="Cutting Board" /> recipes
      </WikiSectionHeading>
      <DataTable
        className="mt-4"
        minWidth="40rem"
        columns={[
          { header: "Recipe", width: "12rem" },
          { header: "Input" },
        ]}
        rows={[
          ["cut_vegetables", <WikiItemText key="raw-vegetables" text="Any raw vegetable (Carrot, Potato, Tomato, Onion, Lettuce, Cucumber, Corn, Beetroot, Pumpkin)" />],
          ["chop_vegetables", "Any cut vegetable"],
          ["chop_olive", <WikiItemText key="olive" text="Olive" />],
          ["chop_pistachio", <WikiItemText key="pistachio" text="Pistachio" />],
          ["chop_rhubarb", <WikiItemText key="rhubarb" text="Rhubarb" />],
          ["chop_garlic", <WikiItemText key="garlic" text="Garlic" />],
        ]}
      />
      <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
        <WikiItemText text="Olive, Pistachio, Rhubarb and Garlic skip the cutting step and go straight to chopped : every other vegetable above is cut first, then optionally chopped again." />
      </p>

      <WikiSectionHeading id="cook-times">Cooking stations</WikiSectionHeading>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <article className="rounded border border-[color-mix(in_srgb,var(--tfmc-cream)_14%,transparent)] p-4">
          <h3 className="font-semibold">{furnitureLink("Fire Pit", "fire_pit")}</h3>
          <p className="mt-2 text-sm text-[var(--tfmc-mist)]"><WikiItemText text="Whole Chicken, Beef Roast, Venison Roast" /></p>
        </article>
        <article className="rounded border border-[color-mix(in_srgb,var(--tfmc-cream)_14%,transparent)] p-4">
          <h3 className="font-semibold">{furnitureLink("Frying Pan", "frying_pan")}</h3>
          <p className="mt-2 text-sm text-[var(--tfmc-mist)]"><WikiItemText text="Chicken, Chicken Leg, Steak, Beef, Venison, Pork, Sausage, Cut vegetables" /></p>
        </article>
        <article className="rounded border border-[color-mix(in_srgb,var(--tfmc-cream)_14%,transparent)] p-4">
          <h3 className="font-semibold">{furnitureLink("Pot", "pot")}</h3>
          <p className="mt-2 text-sm text-[var(--tfmc-mist)]">Cut vegetables</p>
        </article>
      </div>
      <WikiSectionHeading id="carving" intro="Each right-click with the Cutting Knife on a roast or sausage chain takes one cut off, in this order.">
        Carving sequences
      </WikiSectionHeading>
      <DataTable
        className="mt-4"
        minWidth="34rem"
        columns={[
          { header: "Sequence", width: "14rem" },
          { header: "Cuts" },
          { header: "Yields in order" },
        ]}
        rows={[
          ["Whole Chicken", "6", "Chicken Leg ×2, Chicken ×3, then 2 Bone"],
          ["Beef / Venison Roast", "8", "Beef ×7, then 4 Bone"],
          ["Sausage Chain", "5", "Sausage ×5"],
        ]}
      />

      <SeeAlso hrefs={["/wiki/farming", "/wiki/drink-builder", "/wiki/materials", "/wiki/stations", "/wiki/commands"]} />
    </WikiPage>
  );
}
