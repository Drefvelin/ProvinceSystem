import Link from "next/link";
import { instruments } from "../data";

export default function MusicalInstrumentsPage() {
  return (
    <article className="max-w-3xl">
      <h1 className="font-[family-name:var(--font-fraunces)] text-3xl text-[var(--tfmc-cream)] sm:text-4xl">
        Musical Instruments
      </h1>
      <p className="mt-2 text-sm text-[var(--tfmc-mist)]">
        Instruments turn your hotbar into a keyboard. Hold one in your off-hand and press 1 through
        8. Hold Shift for a second layer of chords or higher notes. There are nine instruments,
        each with a completely different sound. Other players hear you from about 64 blocks away.
        All nine are crafted at the Instrument Station and require the Bard class.
      </p>

      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3">
        {instruments.map((inst) => (
          <Link
            key={inst.slug}
            href={`/wiki/musical-instruments/${inst.slug}`}
            className="group flex flex-col items-center gap-2 rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)] bg-[color-mix(in_srgb,var(--tfmc-forest)_45%,transparent)] p-4 transition-colors hover:border-[var(--tfmc-accent)]"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={inst.icon}
              alt={inst.name}
              className="h-10 w-10 [image-rendering:pixelated] transition-transform duration-150 group-hover:scale-110"
            />
            <p className="font-[family-name:var(--font-fraunces)] text-sm text-[var(--tfmc-cream)]">
              {inst.name}
            </p>
          </Link>
        ))}
      </div>

      <h2 className="mt-8 font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
        How to play
      </h2>
      <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-[var(--tfmc-mist)]">
        <li>Put the instrument in your off-hand.</li>
        <li>
          Press number keys 1 to 8 to play notes. The scale runs: 1=C, 2=D, 3=E, 4=F, 5=G, 6=A,
          7=B, 8=C (an octave up).
        </li>
        <li>
          Hold Shift and press 1 to 8 for the second layer. On most instruments that&apos;s a full
          chord; on the Flute, Trumpet and Bagpipe it&apos;s the same scale an octave higher, giving
          sixteen notes total.
        </li>
        <li>
          After every note your selection snaps back to slot 9 — this is deliberate, and lets you
          hit the same note twice in a row instead of the key doing nothing the second time.
        </li>
      </ul>

      <h2 className="mt-8 font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">
        Commands
      </h2>
      <div className="mt-2 overflow-x-auto rounded-md border border-[color-mix(in_srgb,var(--tfmc-cream)_12%,transparent)]">
        <table className="w-full text-left text-sm">
          <thead className="bg-[color-mix(in_srgb,var(--tfmc-forest)_60%,transparent)] text-[var(--tfmc-cream)]">
            <tr>
              <th className="px-3 py-2 font-medium">Command</th>
              <th className="px-3 py-2 font-medium">What it does</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-t border-[color-mix(in_srgb,var(--tfmc-cream)_10%,transparent)]">
              <td className="whitespace-nowrap px-3 py-2 text-[var(--tfmc-accent)]">
                /instruments keybinds
              </td>
              <td className="px-3 py-2 text-[var(--tfmc-mist)]">
                Prints the full note and chord layout for the instrument currently in your
                off-hand. Must be holding it.
              </td>
            </tr>
            <tr className="border-t border-[color-mix(in_srgb,var(--tfmc-cream)_10%,transparent)]">
              <td className="whitespace-nowrap px-3 py-2 text-[var(--tfmc-accent)]">
                /instruments list
              </td>
              <td className="px-3 py-2 text-[var(--tfmc-mist)]">
                Prints the name of every instrument that exists on the server.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <h2 className="mt-8 font-[family-name:var(--font-fraunces)] text-xl text-[var(--tfmc-cream)]">FAQ</h2>
      <dl className="mt-2 space-y-3 text-sm">
        <div>
          <dt className="text-[var(--tfmc-cream)]">&quot;My instrument makes no sound.&quot;</dt>
          <dd className="text-[var(--tfmc-mist)]">
            An instrument must be in your off-hand to be played. Also make sure you&apos;re pressing
            1-8 — slot 9 is the reset slot and doesn&apos;t play anything.
          </dd>
        </div>
        <div>
          <dt className="text-[var(--tfmc-cream)]">&quot;Can I craft an instrument without being a Bard?&quot;</dt>
          <dd className="text-[var(--tfmc-mist)]">No. All nine require the Bard class.</dd>
        </div>
      </dl>
    </article>
  );
}
