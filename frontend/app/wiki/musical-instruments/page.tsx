import Link from "next/link";
import {
  CommandTable,
  DataTable,
  SeeAlso,
  StatGrid,
  WikiPage,
  WikiSectionHeading,
} from "@/app/components/wiki";
import { bardWeaponLutes, instrumentCommands, instruments } from "../data/instruments";

export default function MusicalInstrumentsPage() {
  return (
    <WikiPage
      title="Musical Instruments"
      intro={
        <>
          Instruments turn your hotbar into a keyboard. Hold one in your off-hand and press 1
          through 8. Hold Shift for a second layer of chords or higher notes. There are nine
          instruments, each with a completely different sound. Other players hear you from about 64
          blocks away. All nine are crafted at the Instrument Station and crafting them requires the
          Bard class, but <strong>anyone can play one</strong>, so an instrument you are given or
          buy works fine.
        </>
      }
    >
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

      <WikiSectionHeading id="numbers">The numbers</WikiSectionHeading>
      <StatGrid
        stats={[
          { label: "Audible range", value: "64 blocks", note: "volume 4.0; 1 volume = 16 blocks" },
          { label: "Sound category", value: "Records", note: "the Jukebox / Note Blocks slider" },
          { label: "Craft time", value: "10 seconds", note: "all nine, at the Instrument Station" },
          { label: "Class needed to play", value: "None", note: "Bard is only a crafting gate" },
        ]}
      />

      <WikiSectionHeading id="how-to-play">How to play</WikiSectionHeading>
      <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-[var(--tfmc-mist)]">
        <li>Put the instrument in your off-hand. Your main hand is irrelevant.</li>
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
          After every note your selection snaps back to slot 9. This is deliberate, and lets you
          hit the same note twice in a row instead of the key doing nothing the second time.
          Whatever sits in slot 9 is therefore what bystanders see in your main hand while you play.
        </li>
        <li>A single note particle appears above your head with each note, so everyone can tell it is you.</li>
      </ul>

      <WikiSectionHeading
        id="lutes"
        intro="The Instrument Station is shared with four Bard weapons. They are not instruments and cannot be played."
      >
        The four Lutes that are not instruments
      </WikiSectionHeading>
      <DataTable
        columns={[{ header: "Item", nowrap: true }, { header: "What it is" }]}
        rows={bardWeaponLutes.map((l) => [
          l.name,
          "Bard weapon: shares the station and the Bard gate, but has no note keyboard.",
        ])}
        caption="A Bard browsing the Instrument Station sees 13+ entries, not 9."
        minWidth="40rem"
      />

      <WikiSectionHeading id="commands">Commands</WikiSectionHeading>
      <CommandTable
        commands={instrumentCommands.commands}
        excludedStaffCommands={instrumentCommands.excludedStaffCommands}
      />

      <WikiSectionHeading id="faq">FAQ</WikiSectionHeading>
      <dl className="mt-2 space-y-3 text-sm">
        <div>
          <dt className="text-[var(--tfmc-cream)]">&quot;My instrument makes no sound.&quot;</dt>
          <dd className="text-[var(--tfmc-mist)]">
            Three things, in order. One: your <em>Jukebox/Note Blocks</em> volume slider must not be
            at zero: notes play in the Records category, not Master or Ambient. Two: the instrument
            must be in your <strong>off-hand</strong>. Three: press 1&ndash;8; slot 9 is the reset
            slot and plays nothing.
          </dd>
        </div>
        <div>
          <dt className="text-[var(--tfmc-cream)]">
            &quot;Can I craft an instrument without being a Bard?&quot;
          </dt>
          <dd className="text-[var(--tfmc-mist)]">
            No: all nine recipes require the Bard class.
          </dd>
        </div>
        <div>
          <dt className="text-[var(--tfmc-cream)]">
            &quot;Can I <em>play</em> an instrument without being a Bard?&quot;
          </dt>
          <dd className="text-[var(--tfmc-mist)]">
            Yes. The instrument items carry no class requirement and no stat requirement of any
            kind, and nothing checks your class when you press a key. Instruments are tradeable, so
            a non-Bard handed one plays it exactly as well as its maker.
          </dd>
        </div>
        <div>
          <dt className="text-[var(--tfmc-cream)]">&quot;Do I need a permission?&quot;</dt>
          <dd className="text-[var(--tfmc-mist)]">
            No. Both instrument commands are available to every player.
          </dd>
        </div>
      </dl>

      <SeeAlso hrefs={[/* TEMPORARILY DISABLED: Stations section - re-enable by uncommenting. "/wiki/stations", */ "/wiki/materials", "/wiki/commands"]} />
    </WikiPage>
  );
}
