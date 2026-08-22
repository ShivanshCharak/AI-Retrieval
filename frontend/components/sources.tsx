"use client";

import { useState } from "react";
import {
  FileText,
  ChevronDown,
  X,
  ExternalLink,
} from "lucide-react";

export interface Source {
  page?: string;
  label?: string;
  title?: string;
  source?: string;
}

interface SourcesProps {
  sources?: Source[];
}

const API_URL = "http://localhost:8000";

export default function Sources({
  sources = [],
}: SourcesProps) {
  const [selectedSource, setSelectedSource] =
    useState<Source | null>(null);

  const [expanded, setExpanded] = useState(false);

  if (!sources.length) return null;

  const uniqueSources = Array.from(
    new Map(
      sources.map((source) => [
        `${source.source}-${source.page}`,
        source,
      ])
    ).values()
  );

  const visibleSources = expanded
    ? uniqueSources
    : uniqueSources.slice(0, 4);

  return (
    <>
      <div className="mt-4 pt-3 border-t border-white/10">
        {/* Header */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-2 mb-2 text-xs text-zinc-400 hover:text-zinc-200"
        >
          <span>
            Sources · {uniqueSources.length}
          </span>

          <ChevronDown
            size={14}
            className={`transition-transform ${
              expanded ? "rotate-180" : ""
            }`}
          />
        </button>

        {/* Source cards */}
        <div className="flex flex-wrap gap-2">
          {visibleSources.map((source, index) => (
            <button
              key={`${source.source}-${source.page}-${index}`}
              onClick={() => setSelectedSource(source)}
              className="
                flex
                items-center
                gap-2
                max-w-[240px]
                px-3
                py-2
                rounded-lg
                border
                border-white/10
                bg-white/[0.03]
                hover:bg-white/[0.07]
                hover:border-white/20
                transition
                text-left
              "
            >
              <FileText
                size={14}
                className="shrink-0 text-zinc-500"
              />

              <div className="min-w-0">
                <div className="truncate text-xs text-zinc-300">
                  {source.title || "Document"}
                </div>

                {source.page && (
                  <div className="text-[11px] text-zinc-500">
                    Page {source.page}
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>

        {!expanded && uniqueSources.length > 4 && (
          <button
            onClick={() => setExpanded(true)}
            className="mt-2 text-xs text-zinc-500 hover:text-zinc-300"
          >
            + {uniqueSources.length - 4} more sources
          </button>
        )}
      </div>

      {/* PDF drawer */}
      {selectedSource && (
        <div
          className="fixed inset-0 z-50"
          onClick={() => setSelectedSource(null)}
        >
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/40" />

          {/* Drawer */}
          <div
            className="
              absolute
              right-0
              top-0
              h-full
              w-[45vw]
              min-w-[500px]
              bg-zinc-950
              border-l
              border-white/10
              shadow-2xl
              flex
              flex-col
            "
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="h-14 shrink-0 flex items-center justify-between px-4 border-b border-white/10">
              <div className="flex items-center gap-3 min-w-0">
                <FileText
                  size={17}
                  className="text-zinc-400 shrink-0"
                />

                <div className="min-w-0">
                  <div className="truncate text-sm text-zinc-200">
                    {selectedSource.title}
                  </div>

                  <div className="text-xs text-zinc-500">
                    Page {selectedSource.page}
                  </div>
                </div>
              </div>

              <button
                onClick={() => setSelectedSource(null)}
                className="
                  p-2
                  rounded-lg
                  text-zinc-500
                  hover:text-zinc-200
                  hover:bg-white/10
                "
              >
                <X size={18} />
              </button>
            </div>

            {/* PDF */}
            <div className="flex-1 min-h-0">
              <iframe
                src={`${API_URL}/${selectedSource.source}#page=${selectedSource.page}`}
                className="w-full h-full border-0"
                title={selectedSource.title}
              />
            </div>

            {/* Footer */}
            <div className="h-12 shrink-0 flex items-center justify-end px-4 border-t border-white/10">
              <a
                href={`${API_URL}/${selectedSource.source}#page=${selectedSource.page}`}
                target="_blank"
                rel="noopener noreferrer"
                className="
                  flex
                  items-center
                  gap-2
                  text-xs
                  text-zinc-400
                  hover:text-zinc-200
                "
              >
                Open full document
                <ExternalLink size={13} />
              </a>
            </div>
          </div>
        </div>
      )}
    </>
  );
}