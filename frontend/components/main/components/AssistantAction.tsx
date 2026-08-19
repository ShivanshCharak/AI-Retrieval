import {
  Copy,
  ThumbsDown,
  ThumbsUp,
  CloudLightning,
  Check,
} from "lucide-react";

import { useState } from "react";
import ResponseTime from "../MainArea";

interface AssistantActionsProps {
  traceNode: {
    node: string;
    latency_ms: number;
  }[];
}

export default function AssistantActions({
  traceNode,
}: AssistantActionsProps) {
  const [showCheck, setShowCheck] = useState<number | null>(
    null
  );

  const actions = [
    Copy,
    ThumbsDown,
    ThumbsUp,
    CloudLightning,
  ];

  const handleAction = (index: number) => {
    setShowCheck(index);

    setTimeout(() => {
      setShowCheck(null);
    }, 1500);
  };

  return (
    <div className="flex items-center gap-2 mt-2">
      {actions.map((Icon, index) => (
        <button
          key={index}
          onClick={() => handleAction(index)}
          className="bg-transparent hover:bg-gray-200 p-1 rounded-sm cursor-pointer"
        >
          {showCheck === index ? (
            <Check size={16} />
          ) : (
            <Icon size={16} />
          )}
        </button>
      ))}

      {traceNode.length > 0 && (
        <ResponseTime trace={traceNode} />
      )}
    </div>
  );
}