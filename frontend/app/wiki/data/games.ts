import type { WikiCommandSet, WikiSection } from "./types";

// ---------- Games (table card games) ----------

export const gamesCatalog = [
  {
    id: "blackjack",
    label: "Blackjack",
    cardSet: "french_52",
    rules: "min 10 / max 1000 denar, 6 boxes, auto-dealer on, stands on soft 17",
  },
  {
    id: "poker",
    label: "Tenceur Hold'em",
    cardSet: "french_52",
    rules: "small blind 5 / big blind 10 (advisory only), Ace plays as 14",
  },
  {
    id: "draw",
    label: "Five-Draw",
    cardSet: "french_52",
    rules: "no blinds, no ante, Ace plays as 14",
  },
  {
    id: "freeplay",
    label: "Free play",
    cardSet: "french_52",
    rules: "no rules; anyone can sneak-take the pot",
  },
];

/** "Numbers that matter to players", pulled verbatim from the plugin config. */
export const gamesStats = [
  { thing: "Leave distance (all four games)", value: "6 blocks" },
  { thing: "Display render range", value: "48 blocks" },
  { thing: "Blackjack min / max bet (the one live table)", value: "10 / 1000 denar" },
  { thing: "Blackjack boxes per table", value: "6" },
  { thing: "Hands per box after splits", value: "4 (three resplits)" },
  { thing: "Resplitting aces", value: "Not allowed" },
  { thing: "Dealer hits soft 17", value: "No" },
  { thing: "Blackjack betting window", value: "10 seconds" },
  { thing: "Round-end window", value: "10 seconds" },
  { thing: "Hold'em blinds (advisory)", value: "small 5 / big 10" },
  { thing: "Wager vote window", value: "30 seconds" },
  { thing: "Seconds to place an accepted loot wager", value: "10 seconds" },
  { thing: "Buy-ins needed for a wager to auto-accept", value: "1" },
  { thing: "Chip stack height", value: "6 per pile" },
  { thing: "Card set size", value: "52" },
  {
    thing: "Blackjack payouts",
    value: "Win returns double your stake; natural 21 pays 3:2; push returns your stake",
  },
];

/**
 * Three permissions cover every player-facing command, and all three are
 * default: true in the plugin's plugin.yml: granted to everyone. Everything
 * else at the table (placing, dealing, betting coins, drawing, discarding,
 * revealing, taking the free-play pot) is clicks and chat words, not commands.
 */
export const gamesCommands: WikiCommandSet = {
  system: "Games",
  href: "/wiki/games",
  commands: [
    {
      command: "/games",
      description: "Prints the usage line appropriate to your permissions.",
    },
    {
      command: "/games help",
      description: 'Opens the "Table games" index book.',
      notes: "games.help, default true for everyone.",
    },
    {
      command: "/games help <blackjack|poker|draw|freeplay>",
      description: "Opens that game's rule book.",
      notes: "games.help, default true for everyone.",
    },
    {
      command: "/games bet min <n>",
      description: "Sets the table minimum, as the dealer standing at the shoe.",
      notes: "games.bet, default true for everyone.",
    },
    {
      command: "/games bet max <n>",
      description: "Sets the table maximum.",
      notes: "games.bet, default true for everyone.",
    },
    {
      command: "/games bet open",
      description: "Opens betting for a round.",
      notes: "games.bet, default true for everyone.",
    },
    {
      command: "/games bet close",
      description: "Closes betting.",
      notes: "games.bet, default true for everyone.",
    },
    {
      command: "/games bet hit | stand | double | split",
      description: "Blackjack action on your turn.",
      notes: "games.bet, default true. Identical to typing the word in chat on your turn.",
    },
    {
      command: "/games bet check | call | fold | raise",
      description: "Tenceur Hold'em / Five-Draw action on your turn.",
      notes:
        "games.bet, default true. Put coins on the felt before using raise: the table only reads coins actually on the felt.",
    },
    {
      command: "/wager <amount>",
      description: "Proposes the item you are currently holding as a stake; the table votes on it.",
      notes: "games.wager, default true.",
    },
    {
      command: "/wager accept",
      description: "Votes yes on a proposed wager.",
      notes: "games.wager, default true.",
    },
    {
      command: "/wager decline",
      description: "Votes no on a proposed wager.",
      notes: "games.wager, default true.",
    },
  ],
  excludedStaffCommands: [
    "/games reload",
    "/games deck",
    "/games deck test",
    "/games display",
    "/games place [poker|draw|blackjack|freeplay]",
    "/games payout [player]",
    "/games session start|stop",
    "/games deal",
    "/games deal table",
  ],
};

export const gamesSection: WikiSection = {
  nav: {
    href: "/wiki/games",
    label: "Games",
    category: "combat",
    blurb: "Place a table with a Deck of Cards and bet real denars at Blackjack, Hold'em, Five-Draw, or Free play.",
  },
  commands: gamesCommands,
};
