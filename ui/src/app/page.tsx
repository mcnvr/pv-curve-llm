"use client";

import { Send, Github } from "lucide-react";
import { useState } from "react";

export default function Home() {
  const [message, setMessage] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      // TODO: Handle message submission
      console.log("Message:", message);
      setMessage("");
    }
  };

  return (
    <div className="flex flex-col h-screen bg-neutral-800">
      {/* Top right GitHub link */}
      <div className="absolute top-4 right-4 z-10 w-16 h-16 flex items-center justify-center">
        <a
          href="https://github.com/mcnvr"
          target="_blank"
          rel="noopener noreferrer"
          className="rounded-full p-3 text-neutral-400 hover:text-white hover:bg-neutral-700/50 focus:outline-none focus:ring-2 focus:ring-neutral-500 transition-colors"
        >
          <Github className="h-6 w-6" />
        </a>
      </div>

      {/* Main content area */}
      <div className="flex-1 flex flex-col items-center justify-center px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-medium text-white mb-2">
            Create a PV-Curve
          </h1>
          <p className="text-neutral-400 text-lg">
            Describe what you need for your PV-Curve
          </p>
        </div>
      </div>

      {/* Input Area */}
      <div className="pb-8 px-4">
        <div className="max-w-2xl mx-auto">
          <form onSubmit={handleSubmit} className="relative">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask anything"
              className="w-full rounded-2xl bg-neutral-700 border border-neutral-600 px-4 py-3 pr-12 text-white placeholder-neutral-400 focus:border-neutral-500 focus:outline-none focus:ring-1 focus:ring-neutral-500"
            />
            <button
              type="submit"
              disabled={!message.trim()}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 rounded-lg p-2 text-neutral-400 hover:text-white hover:bg-neutral-600 focus:outline-none focus:ring-2 focus:ring-neutral-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
