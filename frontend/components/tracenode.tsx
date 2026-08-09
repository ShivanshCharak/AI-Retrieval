"use client";

import { useState } from "react";
import { Info } from "lucide-react";

type TraceNode = {
  node: string;
  latency_ms: number;
};

export default function ResponseTime({ trace }: { trace: TraceNode[] }) {
  const [open, setOpen] = useState(false);

  const maxLatency = Math.max(...trace.map((item) => item.latency_ms));

  const total = trace.reduce((sum, item) => sum + item.latency_ms, 0);

  return (
    <div className="w-full max-w-2xl">
      

      {/* Response time */}
      <button
        onClick={() => setOpen(!open)}
        className="text-sm text-gray-500 cursor-pointer"
      >
        <span className="mt-[-10px]">
          Response time: {(total / 1000).toFixed(2)}s
        </span>
      </button>

      {/* Timeline */}
      {open && (
        <div>
          {trace.map((item, index) => {
            const width = (item.latency_ms / maxLatency) * 100;

            return (
              <div key={index} className="flex">
                <div className="flex flex-col items-center mr-3">
                  <div className="w-1 h-1  my-2 rounded-full bg-gray-300 shrink-0" />
                  {index !== trace.length - 1 && (
                    <div className="w-[1px] flex-1 bg-gray-300 " />
                  )}
                </div>

            
                <div className="flex-1  items-center flex justify-between text-xs pb-4">
                  
                  <span className="font-medium">{item.node}</span>

                  <span className="text-gray-500">
                    {item.latency_ms.toFixed(0)} ms
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
