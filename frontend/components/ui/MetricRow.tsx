import { MetricRowProps } from "../../lib/types";

function MetricRow({ label, value, icon }: MetricRowProps) {
  return (
    <div className="flex items-center justify-between p-2 rounded hover:bg-white/5 transition">
      <div className="flex items-center gap-2 text-sm text-neutral-400">
        {icon} {label}
      </div>
      <div className="font-mono text-sm">{value}</div>
    </div>
  );
}

export default MetricRow;