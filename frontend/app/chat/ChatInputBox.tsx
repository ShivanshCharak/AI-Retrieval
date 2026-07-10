"use client";

import React, { useState, useRef, useEffect, SetStateAction } from "react";
import { Paperclip, Globe, Mic, ArrowUp, Glasses } from "lucide-react";
import { MODELS } from "@/data/constants";

interface ChatInputBoxProps {
  onSend?: (
    message: string,
    model: string,
    file?: File,
    web_search?: boolean,
    deep_search?: boolean,
  
  ) => void;
  chatting: boolean;
  setChatting: boolean;
  setMessage: React.Dispatch<React.SetStateAction<{role:"user"|"assistant";content: string, loading:boolean, file?:{name:string, type:string}}[]>>;
  webSearch?: boolean;
  setStatus: React.Dispatch<SetStateAction<string>>
  status: string
}

export default function ChatInputBox({
  onSend,
  chatting = false,
  setMessage,
  setChatting,
  setStatus,
}: ChatInputBoxProps) {
  const [input, setInput] = useState("");
  const [selectedModel, setSelectedModel] = useState(MODELS[0]);
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [webSearch, setWebSearch] = useState<boolean>(false);
    const [deepSearch, setDeepSearch] = useState<boolean>(false);

  const handleSend = async () => {
    const formdata = new FormData();
    formdata.append("message", input.trim());
    formdata.append("model", selectedModel);
    formdata.append("web_search", String(webSearch));
    formdata.append("deep_search", String(deepSearch))

    if (!input.trim()) return;
    onSend?.(input.trim(), selectedModel, file, webSearch);
    if (file) {
      formdata.append("file", file);
    }

const res = await fetch("/api/chat", {
  credentials:"include",
  method: "POST",
  body: formdata,
});

if (!res.body) return;
const reader = res.body!.getReader();
const decoder = new TextDecoder();

let buffer = "";
let answer = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  buffer += decoder.decode(value, { stream: true });

  const events = buffer.split("\n\n");
  buffer = events.pop() ?? "";

  for (const event of events) {
    if (!event.startsWith("data: ")) continue;

    const data = JSON.parse(event.slice(6));

    switch (data.type) {
      case "status":
        console.log("Completed:", data.node);
        setStatus(data.node)
        break;

      case "token":
        answer += data.content;

        setMessage(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            content: answer,
            loading: false,
            file:file?{
              name: file.name,
              type: file.type
            }:undefined
          };
          return updated;
        });
        break;

      case "done":
        console.log("Finished");
        break;
    }
  }
}
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
      setInput("");
      setFile("");
      setChatting(true)
    }
  };

  return (
    <div
      className={` w-[1000px] bg-white rounded-2xl  shadow-sm border border-gray-200 overflow-hidden ${chatting ? "bottom-0 fixed" : ""}`}
    >
      {console.log("chatting",chatting)}
      {/* Upgrade banner */}
      <div className="flex items-center gap-1 px-4 pt-3 pb-1">
        <span className="text-xs text-gray-500">
          Use our faster AI on Pro Plan
        </span>
        <span className="mx-1 text-gray-300">·</span>
        <button className="text-xs text-purple-500 font-semibold hover:underline">
          Upgrade
        </button>
      </div>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.doc,.docx,.txt"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (!file) return;

          console.log("Selected file:", file);
          setFile(file);
          // store it in state if needed
        }}
      />

      {file && (
        <div className="mx-4 mt-2 mb-1 flex items-center justify-between bg-gray-200 w-[200px] rounded-lg px-3 py-2 text-xs text-gray-700">
          <div className="flex items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="lucide lucide-book-open-icon lucide-book-open"
            >
              <path d="M12 7v14" />
              <path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z" />
            </svg>
            <span className="truncate max-w-[250px] w-[100px] font-semibold">
              {file.name}
            </span>
            <span>{file.type.split("/")[1]}</span>
          </div>

          <button
            onClick={() => setFile(null)}
            className="text-gray-500 hover:text-red-500"
          >
            ✕
          </button>
        </div>
      )}
      {/* Textarea */}
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask me anything..."
        rows={2}
        className="w-full px-4 py-2 text-sm text-gray-700 placeholder-gray-400 outline-none resize-none bg-transparent"
      />

      {/* Toolbar */}
      <div className="flex items-center justify-between px-3 pb-3 gap-2 ">
        <div className="flex items-center gap-2">
          <button
            onClick={() => fileInputRef.current?.click()}
            className=" cursor-pointer p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-400 hover:text-gray-600"
          >
            <Paperclip size={16} />
          </button>

          <div className="flex items-center gap-1 border border-gray-200 rounded-full px-3 py-1 text-xs text-gray-600 hover:bg-gray-50 transition-colors">
            <Globe size={12} className="text-gray-400" />
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="bg-transparent outline-none cursor-pointer text-xs text-gray-600"
            >
              {MODELS.map((m) => (
                <option key={m}>{m}</option>
              ))}
            </select>
          </div>
          <button
            onClick={() => setWebSearch(!webSearch)}
            className={`px-7 cursor-pointer flex align-middle py-2 rounded-full transition-colors duration-200 ${
              webSearch ? "bg-black text-white" : "bg-gray-200 text-black"
            }`}
          >
            <Globe size={14} color={webSearch ? "white" : "gray"} />
            <label
              className=" cursor-pointer ml-2 font-semibold text-xs"
              htmlFor=""
            >
              Web Search
            </label>
          </button>
          <button
            onClick={() => setDeepSearch(!deepSearch)}
            className={`px-7 cursor-pointer flex align-middle py-2 rounded-full transition-colors duration-200 ${
              deepSearch ? "bg-black text-white" : "bg-gray-200 text-black"
            }`}
          >
            <Glasses size={14} color={deepSearch ? "white" : "gray"} />
            <label
              className=" cursor-pointer ml-2 font-semibold text-xs"
              htmlFor=""
            >
              Deep Search
            </label>
          </button>
        </div>

        <div className="flex items-center gap-2 ml-auto">
          <button className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-400 hover:text-gray-600">
            <Mic size={16} />
          </button>

          <button
            onClick={handleSend}
            disabled={!input.trim()}
            className={`p-1.5 rounded-full transition-colors ${
              input.trim()
                ? "bg-gray-900 text-white hover:bg-gray-700"
                : "bg-gray-200 text-gray-400 cursor-not-allowed"
            }`}
          >
            <ArrowUp size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
