"use client";
import { forceCenter, forceCollide, forceManyBody, forceSimulation, forceX, forceY } from "d3-force";
import { useMemo } from "react";

type Props = {
  weights: Record<string, number>;
  labels: Record<string, string>;
  selected: string | null;
  onSelect: (id: string) => void;
  /** union of topic ids, so node positions stay stable between "before" and "now" */
  ids: string[];
};

const W = 900, H = 520;

type N = { id: string; x: number; y: number };

export default function InterestGraph({ weights, labels, selected, onSelect, ids }: Props) {
  // Positions depend on the full topic set (stable between views); only radius/colour change on toggle -> CSS transitions animate it.
  const nodes = useMemo<N[]>(() => {
    const ns = ids.map((id, i) => ({ id, x: W / 2 + Math.cos(i) * 120, y: H / 2 + Math.sin(i) * 120 }));
    const sim = forceSimulation(ns as never[])
      .force("charge", forceManyBody().strength(-14))
      .force("center", forceCenter(W / 2, H / 2))
      .force("x", forceX(W / 2).strength(0.06))
      .force("y", forceY(H / 2).strength(0.1))
      .force("collide", forceCollide<N>().radius(() => 40))
      .stop();
    for (let i = 0; i < 260; i++) sim.tick();
    return ns;
  }, [ids.join("|")]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="graph-box">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Interest graph: bigger circles mean stronger interests">
        {nodes.map((n) => {
          const w = weights[n.id] ?? 0;
          const r = 6 + Math.pow(w, 0.9) * 42;
          const on = selected === n.id;
          const strong = w >= 0.5;
          return (
            <g key={n.id} onClick={() => onSelect(n.id)} tabIndex={0} role="button" aria-label={`${labels[n.id] ?? n.id}: ${Math.round(w * 100)}%`}
               onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onSelect(n.id)}>
              <circle cx={n.x} cy={n.y} r={r}
                fill={strong ? "var(--accent)" : "var(--ink)"} fillOpacity={strong ? 0.85 : 0.18 + w * 0.5}
                stroke={on ? "var(--ink)" : "none"} strokeWidth={2} />
              {r > 22 && (() => {
                const words = (labels[n.id] ?? n.id).replace("&", "and").split(" ");
                const half = Math.ceil(words.length / 2);
                const lines = words.length > 1 ? [words.slice(0, half).join(" "), words.slice(half).join(" ")] : words;
                return (
                  <text style={{ fill: strong ? "#fff" : undefined }}>
                    {lines.map((l, i) => <tspan key={i} x={n.x} y={n.y + 4 + (i - (lines.length - 1) / 2) * 13}>{l}</tspan>)}
                  </text>
                );
              })()}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
