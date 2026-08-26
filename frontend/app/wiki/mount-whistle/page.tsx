import CraftingGrid from "../../components/wiki/CraftingGrid";
import { whistleMessages, whistleRecipe } from "../data";

export default function MountWhistlePage() {
  return (
    <article className="max-w-3xl">
      <h1 className="font-[family-name:var(--font-fraunces)] text-3xl text-[var(--tfmc-cream)] sm:text-4xl">
        Mount Whistle
      </h1>
      <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
        In-game item id: <code className="text-[var(--tfmc-accent)]">ANIMAL_WHISTLE</code>. Right-click
        it and every mount within 64 blocks lights up with a glowing outline you can see straight
        through walls, hills, and trees.
      </p>

      <h2 className="mt-8 font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
        Step 1 — Get one
      </h2>
      <div className="mt-4">
        <CraftingGrid recipe={whistleRecipe} />
      </div>

      <h2 className="mt-8 font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
        Step 2 — Use it
      </h2>
      <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-[var(--tfmc-mist)]">
        <li>Hold the Mount Whistle in your main hand.</li>
        <li>Right-click — a whistle sound plays at your location, audible to everyone nearby.</li>
        <li>Every mount within 64 blocks glows for 5 seconds.</li>
        <li>Chat tells you how many it found — follow the outlines to locate your mount.</li>
        <li>There is a short 3-second cooldown before you can whistle again.</li>
      </ul>

      <div className="mt-4 overflow-x-auto rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)]">
        <table className="w-full text-left text-sm">
          <tbody>
            <tr className="border-b border-[color-mix(in_srgb,var(--tfmc-cream)_10%,transparent)]">
              <td className="px-3 py-2 text-[var(--tfmc-cream)]">Range</td>
              <td className="px-3 py-2 text-[var(--tfmc-mist)]">64 blocks in every direction</td>
            </tr>
            <tr className="border-b border-[color-mix(in_srgb,var(--tfmc-cream)_10%,transparent)]">
              <td className="px-3 py-2 text-[var(--tfmc-cream)]">Glow duration</td>
              <td className="px-3 py-2 text-[var(--tfmc-mist)]">5 seconds</td>
            </tr>
            <tr className="border-b border-[color-mix(in_srgb,var(--tfmc-cream)_10%,transparent)]">
              <td className="px-3 py-2 text-[var(--tfmc-cream)]">Cooldown</td>
              <td className="px-3 py-2 text-[var(--tfmc-mist)]">3 seconds</td>
            </tr>
            <tr>
              <td className="px-3 py-2 text-[var(--tfmc-cream)]">Detects</td>
              <td className="px-3 py-2 text-[var(--tfmc-mist)]">Horses, Donkeys, Mules and Llamas</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h2 className="mt-8 font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
        Messages
      </h2>
      <div className="mt-2 overflow-x-auto rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)]">
        <table className="w-full text-left text-sm">
          <thead className="bg-[color-mix(in_srgb,var(--tfmc-forest)_60%,transparent)] text-[var(--tfmc-cream)]">
            <tr>
              <th className="px-3 py-2 font-medium">Message</th>
              <th className="px-3 py-2 font-medium">Meaning</th>
            </tr>
          </thead>
          <tbody>
            {whistleMessages.map((row) => (
              <tr key={row.message} className="border-t border-[color-mix(in_srgb,var(--tfmc-cream)_10%,transparent)]">
                <td className="whitespace-nowrap px-3 py-2 text-[var(--tfmc-accent)]">{row.message}</td>
                <td className="px-3 py-2 text-[var(--tfmc-mist)]">{row.meaning}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2 className="mt-8 font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">FAQ</h2>
      <dl className="mt-2 space-y-3 text-sm">
        <div>
          <dt className="text-[var(--tfmc-cream)]">&quot;The whistle says no animals but I know they are close.&quot;</dt>
          <dd className="text-[var(--tfmc-mist)]">
            The range is a flat 64 blocks. Move to a new spot and whistle again — if they were in
            range, you would see them.
          </dd>
        </div>
      </dl>
    </article>
  );
}
