import { ReactNode } from "react";
import { cn } from "@/lib/utils";

export interface Column<T> {
  key: string;
  header: string;
  align?: "left" | "right" | "center";
  width?: string;
  render: (row: T) => ReactNode;
}

export function DataTable<T>({
  columns,
  rows,
  rowKey,
}: {
  columns: Column<T>[];
  rows: T[];
  rowKey: (row: T) => string;
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-[13px]">
        <thead>
          <tr className="hairline-top border-b border-line">
            {columns.map((col) => (
              <th
                key={col.key}
                style={{ width: col.width }}
                className={cn(
                  "px-4 py-2.5 text-2xs font-medium text-ink-600 tracking-wide whitespace-nowrap",
                  col.align === "right" && "text-right",
                  col.align === "center" && "text-center",
                  (!col.align || col.align === "left") && "text-left"
                )}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr
              key={rowKey(row)}
              className="border-b border-line/60 last:border-0 hover:bg-graphite-700/40 transition-colors"
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  className={cn(
                    "px-4 py-2.5 text-ink-100 align-middle",
                    col.align === "right" && "text-right",
                    col.align === "center" && "text-center"
                  )}
                >
                  {col.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
