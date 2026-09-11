import type { ReactNode } from "react";
import type { CommandAccess, CommandRow } from "@/app/wiki/data";
import DataTable from "./DataTable";

export type { CommandAccess, CommandRow } from "@/app/wiki/data";

export interface CommandTableProps {
  commands: CommandRow[];
  excludedStaffCommands?: string[];
  showAliases?: boolean;
  showNotes?: boolean;
  caption?: ReactNode;
  className?: string;
}

export default function CommandTable({ commands, showAliases = true, showNotes = true, caption, className }: CommandTableProps) {
  const playerCommands = commands.filter((command) => (command.access ?? "player") === "player");
  const rows = playerCommands.map((command) => {
    const cells: ReactNode[] = [
      <code key="command" className="break-words font-mono text-[var(--tfmc-accent)] [overflow-wrap:anywhere]">{command.command}</code>,
    ];
    if (showAliases) {
      cells.push(command.aliases?.length ? <span key="aliases" className="break-words font-mono text-[var(--tfmc-mist)] [overflow-wrap:anywhere]">{command.aliases.join(", ")}</span> : "None");
    }
    cells.push(<span key="description" className="break-words [overflow-wrap:anywhere]">{command.description}</span>);
    if (showNotes) {
      cells.push(<span key="notes" className="break-words [overflow-wrap:anywhere]">{command.notes ?? "None"}</span>);
    }
    return cells;
  });

  const columns = [
    { header: "Command", width: showAliases ? (showNotes ? "18%" : "24%") : (showNotes ? "22%" : "28%") },
    ...(showAliases ? [{ header: "Aliases", width: showNotes ? "16%" : "20%" }] : []),
    { header: "What it does", width: showAliases ? (showNotes ? "44%" : "56%") : (showNotes ? "50%" : "72%") },
    ...(showNotes ? [{ header: "Notes", width: showAliases ? "22%" : "28%" }] : []),
  ];

  return (
    <div className={className}>
      <DataTable caption={caption} minWidth="0" fixedLayout rowKey={(_row, index) => playerCommands[index].command}
        columns={columns}
        rows={rows} emptyMessage="This feature has no player commands." />
    </div>
  );
}
