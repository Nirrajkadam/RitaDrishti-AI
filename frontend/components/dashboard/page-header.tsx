import { ReactNode } from "react";

export function PageHeader({
  title,
  description,
  actions,
}: {
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="flex items-start justify-between gap-4 px-6 pt-6 pb-5">
      <div>
        <h1 className="text-lg font-semibold tracking-tight text-ink-100">
          {title}
        </h1>
        {description && (
          <p className="mt-1 text-[13px] text-ink-400 max-w-2xl">
            {description}
          </p>
        )}
      </div>
      {actions && <div className="flex items-center gap-2 shrink-0">{actions}</div>}
    </div>
  );
}
