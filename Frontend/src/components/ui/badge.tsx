import * as React from "react"
import { cn } from "../../lib/utils"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "outline";
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        {
          "border-transparent bg-zinc-900 text-zinc-50 hover:bg-zinc-900/80": variant === "default",
          "border-transparent bg-zinc-100 text-zinc-900 hover:bg-zinc-100/80": variant === "secondary",
          "text-zinc-950": variant === "outline",
        },
        className
      )}
      {...props}
    />
  )
}

export { Badge }
