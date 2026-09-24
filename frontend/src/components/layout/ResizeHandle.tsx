import { PanelResizeHandle } from "react-resizable-panels";
import { cn } from "../../lib/utils";

interface ResizeHandleProps {
  className?: string;
}

export function ResizeHandle({ className }: ResizeHandleProps) {
  return (
    <PanelResizeHandle
      className={cn(
        "group relative flex w-2 shrink-0 items-center justify-center bg-canvas transition-colors",
        "hover:bg-accent-soft/60 data-[resize-handle-active]:bg-accent-soft",
        className
      )}
    >
      <div
        className={cn(
          "h-10 w-1 rounded-full bg-line transition-colors",
          "group-hover:bg-accent/50 group-data-[resize-handle-active]:bg-accent"
        )}
      />
    </PanelResizeHandle>
  );
}
