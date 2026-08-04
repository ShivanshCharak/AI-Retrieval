import { QUICK_ACTIONS } from "../../data/constants";
import OrbIcon from "../../app/chat/OrbIcon";
import Greeting from "../../app/chat/Greeting";
import ChatInputBox from "../../app/chat/ChatInputBox";
import QuickActions from "../../app/chat/QuickActions";
import ReactMarkdown from "react-markdown";
import { Paperclip } from "lucide-react";
import remarkGfm from "remark-gfm";

import { useState } from "react";
import { LoaderIcon } from "lucide-react";

interface MainAreaProps {
  userName?: string;
  sidebarVisibility: boolean;
}

export default function MainArea({
  userName = "Toby",
  sidebarVisibility,
}: MainAreaProps) {
  const [status, setStatus] = useState<{stage:string,title:string, description:string}[]>([]);
  const [message, setMessage] = useState<
    {
      role: "user" | "assistant";
      content: string;
      loading: boolean;
      file?: { name: string; type: string };
    }[]
  >([]);
  const [isChatting, setIsChatting] = useState<boolean>(false);
  const handleSend = (content: string, model: string, file?: File) => {
    setMessage((prev) => [
      ...prev,
      {
        role: "user",
        content,
        loading: false,
        file: file
          ? {
              name: file.name,
              type: file.type,
            }
          : undefined,
      },
      {
        role: "assistant",
        content: "",
        loading: true,
      },
    ]);
  };
  return (
    <main
      className={`flex-1 flex flex-col items-center justify-center gap-8 bg-gray-50 px-6 ${sidebarVisibility ? "w-[83%]" : "w-[97%]"} overflow-y-scroll`}
    >
      <div className="flex flex-col items-center gap-5">
        {message.length == 0 ? (
          <>
            <OrbIcon />
            <Greeting name={userName} />
          </>
        ) : (
          <></>
        )}
      </div>
      <div className="w-full top-20 absolute max-w-2xl flex flex-col gap-2 overflow-y-auto ">
        {message.map((msg, i) => (
          <div
            key={i}
            className={`px-3 py-2 rounded-lg text-sm w-fit max-w-[80%] ${
              msg.role === "user"
                ? "bg-black text-white ml-auto"
                : "bg-gray-200 text-black mr-auto"
            }`}
          >
            {msg.loading ? (
              <div className=" flex justify-around">
                <LoaderIcon className="animate-spin" />

                <label htmlFor="" className=" ml-3">
                  {status}
                </label>
              </div>
            ) : (
              <>
                {msg.role === "user" && msg.file && (
                  <div className="mb-2 flex items-center gap-2 rounded-lg border border-gray-500 bg-gray-800 px-3 py-2 w-fit">
                    <Paperclip size={14} />
                    <span>{msg.file.name}</span>
                  </div>
                )}

                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.content}
                </ReactMarkdown>
              </>
            )}
          </div>
        ))}
      </div>

      <ChatInputBox
        onSend={handleSend}
        setMessage={setMessage}
        chatting={isChatting}
        setChatting={setIsChatting}
        status={status}
        setStatus={setStatus}
      />

      {message.length > 0 ? "" : <QuickActions actions={QUICK_ACTIONS} />}
    </main>
  );
}
