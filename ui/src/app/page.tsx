"use client";

import { Send, Github, SquarePen, Bot, User, ChevronDown, ChevronRight } from "lucide-react";
import { useState, useRef } from "react";

interface ChatMessage {
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

interface ParsedContent {
  thinking?: string;
  response: string;
}

// Component to render formatted text with markdown and math
const FormattedText = ({ text }: { text: string }) => {
  const formatText = (input: string) => {
    const elements: React.ReactElement[] = [];
    let currentIndex = 0;
    
    // Regex patterns for different formatting
    const patterns = [
      { 
        regex: /\\\[([\s\S]*?)\\\]/g, 
        type: 'block-math' 
      },
      { 
        regex: /\\\(([\s\S]*?)\\\)/g, 
        type: 'inline-math' 
      },
      { 
        regex: /\*\*(.*?)\*\*/g, 
        type: 'bold' 
      },
      { 
        regex: /\*(.*?)\*/g, 
        type: 'italic' 
      },
      { 
        regex: /```([\s\S]*?)```/g, 
        type: 'code-block' 
      },
      { 
        regex: /`(.*?)`/g, 
        type: 'inline-code' 
      }
    ];

    // Find all matches and their positions
    const allMatches: Array<{ 
      match: RegExpMatchArray; 
      type: string; 
      start: number; 
      end: number; 
    }> = [];

    patterns.forEach(pattern => {
      let match;
      const regex = new RegExp(pattern.regex.source, pattern.regex.flags);
      while ((match = regex.exec(input)) !== null) {
        allMatches.push({
          match,
          type: pattern.type,
          start: match.index!,
          end: match.index! + match[0].length
        });
      }
    });

    // Sort matches by position
    allMatches.sort((a, b) => a.start - b.start);

    // Remove overlapping matches (keep the first one)
    const validMatches = [];
    let lastEnd = 0;
    for (const match of allMatches) {
      if (match.start >= lastEnd) {
        validMatches.push(match);
        lastEnd = match.end;
      }
    }

    // Build the result
    let elementIndex = 0;
    validMatches.forEach((matchInfo, index) => {
      // Add text before this match
      if (matchInfo.start > currentIndex) {
        const textBefore = input.slice(currentIndex, matchInfo.start);
        if (textBefore) {
          elements.push(<span key={`text-${elementIndex++}`}>{textBefore}</span>);
        }
      }

      // Add the formatted element
      const content = matchInfo.match[1] || matchInfo.match[0];
      switch (matchInfo.type) {
        case 'block-math':
          elements.push(
            <div key={`math-block-${elementIndex++}`} className="my-4 p-3 bg-neutral-800 rounded border overflow-x-auto">
              <div className="font-mono text-sm text-center">{content}</div>
            </div>
          );
          break;
        case 'inline-math':
          elements.push(
            <span key={`math-inline-${elementIndex++}`} className="inline-block px-1 bg-neutral-800 rounded font-mono text-sm">
              {content}
            </span>
          );
          break;
        case 'bold':
          elements.push(<strong key={`bold-${elementIndex++}`}>{content}</strong>);
          break;
        case 'italic':
          elements.push(<em key={`italic-${elementIndex++}`}>{content}</em>);
          break;
        case 'code-block':
          elements.push(
            <pre key={`code-block-${elementIndex++}`} className="my-4 p-3 bg-neutral-800 rounded border overflow-x-auto">
              <code className="text-sm">{content}</code>
            </pre>
          );
          break;
        case 'inline-code':
          elements.push(
            <code key={`code-inline-${elementIndex++}`} className="px-1 bg-neutral-800 rounded text-sm font-mono">
              {content}
            </code>
          );
          break;
      }

      currentIndex = matchInfo.end;
    });

    // Add remaining text
    if (currentIndex < input.length) {
      const remainingText = input.slice(currentIndex);
      if (remainingText) {
        elements.push(<span key={`text-final-${elementIndex++}`}>{remainingText}</span>);
      }
    }

    return elements.length > 0 ? elements : [<span key="default">{input}</span>];
  };

  return <div className="whitespace-pre-wrap">{formatText(text)}</div>;
};

export default function Home() {
  const [message, setMessage] = useState("");
  const [conversation, setConversation] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedThinking, setExpandedThinking] = useState<Set<number>>(new Set());
  const abortControllerRef = useRef<AbortController | null>(null);

  const parseContent = (content: string): ParsedContent => {
    const thinkMatch = content.match(/<think>([\s\S]*?)<\/think>/);
    if (thinkMatch) {
      const thinking = thinkMatch[1].trim();
      const response = content.replace(/<think>[\s\S]*?<\/think>/, '').trim();
      return { thinking, response };
    }
    return { response: content };
  };

  const getStreamingThinking = (content: string): string => {
    const thinkMatch = content.match(/<think>([\s\S]*?)(?:<\/think>|$)/);
    return thinkMatch ? thinkMatch[1] : '';
  };

  const getStreamingResponse = (content: string): string => {
    if (content.includes('</think>')) {
      const response = content.replace(/<think>[\s\S]*?<\/think>/, '').trim();
      return response.replace(/^\s+/, ''); // Remove leading whitespace/newlines
    }
    if (content.includes('<think>')) {
      return '';
    }
    return content;
  };

  const isThinkingComplete = (content: string): boolean => {
    return content.includes('</think>');
  };

  const hasThinkingStarted = (content: string): boolean => {
    return content.includes('<think>');
  };

  const getThinkingButtonText = (msg: ChatMessage, content: string): string => {
    if (msg.isStreaming) {
      if (content.length === 0) {
        return "Processing...";
      } else if (hasThinkingStarted(content)) {
        const thinkingContent = getStreamingThinking(content);
        if (thinkingContent.length === 0) {
          return "Processing...";
        } else if (!isThinkingComplete(content)) {
          return "Thinking...";
        } else {
          return "Click here to see the thought process";
        }
      }
      return "Processing...";
    }
    return "Click here to see the thought process";
  };

  const shouldShowChevron = (msg: ChatMessage, content: string): boolean => {
    if (msg.isStreaming) {
      if (content.length === 0) return false; // No chevron during processing
      return hasThinkingStarted(content) && getStreamingThinking(content).length > 0;
    }
    return true;
  };

  const isProcessing = (msg: ChatMessage, content: string): boolean => {
    return msg.isStreaming && content.length === 0;
  };

  const shouldShowResponseBox = (msg: ChatMessage, content: string): boolean => {
    if (msg.type !== 'ai') return true;
    if (msg.isStreaming && content.length === 0) return false; // Hide during processing
    if (!hasThinkingStarted(content)) return true;
    if (msg.isStreaming && hasThinkingStarted(content) && !isThinkingComplete(content)) return false;
    return isThinkingComplete(content);
  };

  const toggleThinking = (index: number) => {
    const newExpanded = new Set(expandedThinking);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedThinking(newExpanded);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      const userMessage = message.trim();
      setMessage("");
      setIsLoading(true);

      const userMsg: ChatMessage = {
        type: 'user',
        content: userMessage,
        timestamp: new Date()
      };

      setConversation(prev => [...prev, userMsg]);

      // Create AI message placeholder
      const aiMsgId = Date.now();
      const aiMsg: ChatMessage = {
        type: 'ai',
        content: '',
        timestamp: new Date(),
        isStreaming: true
      };

      setConversation(prev => [...prev, aiMsg]);

      try {
        abortControllerRef.current = new AbortController();
        
        const response = await fetch('http://localhost:5000/ask', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ question: userMessage }),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          throw new Error('Failed to get response');
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (reader) {
          while (true) {
            const { done, value } = await reader.read();
            
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6));
                  
                  if (data.chunk) {
                    // Update the streaming message
                    setConversation(prev => 
                      prev.map((msg, index) => 
                        index === prev.length - 1 && msg.type === 'ai' && msg.isStreaming
                          ? { ...msg, content: msg.content + data.chunk }
                          : msg
                      )
                    );
                  } else if (data.done) {
                    // Mark streaming as complete
                    setConversation(prev => 
                      prev.map((msg, index) => 
                        index === prev.length - 1 && msg.type === 'ai' && msg.isStreaming
                          ? { ...msg, isStreaming: false }
                          : msg
                      )
                    );
                  } else if (data.error) {
                    // Handle error
                    setConversation(prev => 
                      prev.map((msg, index) => 
                        index === prev.length - 1 && msg.type === 'ai' && msg.isStreaming
                          ? { ...msg, content: `Error: ${data.error}`, isStreaming: false }
                          : msg
                      )
                    );
                  }
                } catch (parseError) {
                  // Ignore JSON parse errors for incomplete chunks
                }
              }
            }
          }
        }
        
      } catch (error: any) {
        if (error.name !== 'AbortError') {
          setConversation(prev => 
            prev.map((msg, index) => 
              index === prev.length - 1 && msg.type === 'ai' && msg.isStreaming
                ? { ...msg, content: 'Sorry, I encountered an error while processing your request. Please try again.', isStreaming: false }
                : msg
            )
          );
        }
      } finally {
        setIsLoading(false);
        abortControllerRef.current = null;
      }
    }
  };

  const handleNewChat = () => {
    // Abort any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setConversation([]);
    setMessage("");
    setIsLoading(false);
    setExpandedThinking(new Set());
  };

  return (
    <div className="flex flex-col h-screen bg-neutral-800">
      {/* Navigation Bar */}
      <nav className="border-b border-neutral-700 bg-neutral-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <img src="/nose-llm-logo.png" alt="Nose-LLM" className="h-8 w-8" />
              <h1 className="text-xl font-semibold text-white">Nose-LLM</h1>
            </div>
            <div className="flex items-center gap-2">
        <button
                onClick={handleNewChat}
          aria-label="New Chat"
                className="rounded-full p-2 text-neutral-400 hover:text-white hover:bg-neutral-700/50 focus:outline-none focus:ring-2 focus:ring-neutral-500 transition-colors cursor-pointer"
        >
                <SquarePen className="h-5 w-5" />
        </button>
        <a
          href="https://github.com/mcnvr/pv-curve-llm"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="GitHub Repository"
                className="rounded-full p-2 text-neutral-400 hover:text-white hover:bg-neutral-700/50 focus:outline-none focus:ring-2 focus:ring-neutral-500 transition-colors"
        >
                <Github className="h-5 w-5" />
        </a>
      </div>
          </div>
        </div>
      </nav>

      {/* Main content area */}
      <div className="flex-1 flex flex-col">
        {conversation.length === 0 ? (
      <div className="flex-1 flex flex-col items-center justify-center px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-medium text-white mb-2">
            Create a PV-Curve
          </h1>
          <p className="text-neutral-400 text-lg">
                Conduct PV-Curve Voltage Stability Analysis with Natural Language
          </p>
        </div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto px-4 py-6">
            <div className="max-w-4xl mx-auto space-y-6">
              {conversation.map((msg, index) => {
                const parsedContent = msg.type === 'ai' ? parseContent(msg.content) : null;
                const hasThinking = msg.type === 'ai' && (parsedContent?.thinking || (msg.isStreaming && (msg.content.length === 0 || hasThinkingStarted(msg.content))));
                const showResponseBox = shouldShowResponseBox(msg, msg.content);
                
                return (
                  <div key={index} className={`flex gap-3 items-start ${msg.type === 'user' ? 'flex-row-reverse' : ''}`}>
                    <div className="flex-shrink-0">
                      {msg.type === 'user' ? (
                        <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center">
                          <User className="w-5 h-5 text-white" />
                        </div>
                      ) : (
                        <div className="w-10 h-10 rounded-full bg-neutral-600 flex items-center justify-center">
                          <Bot className="w-5 h-5 text-white" />
                        </div>
                      )}
                    </div>
                    
                    <div className={`flex-1 max-w-3xl ${msg.type === 'user' ? 'flex justify-end' : 'flex justify-start'}`}>
                      <div className="max-w-fit">
                        {hasThinking && (
                          <div className={`${showResponseBox ? 'mb-3' : 'flex items-center h-10'}`}>
                            {isProcessing(msg, msg.content) ? (
                              <div className="flex items-center gap-2 text-neutral-400">
                                <span className="text-base animate-pulse">
                                  {getThinkingButtonText(msg, msg.content)}
                                </span>
                              </div>
                            ) : (
                              <button
                                onClick={() => toggleThinking(index)}
                                className="flex items-center gap-2 text-neutral-400 hover:text-neutral-300 transition-colors"
                              >
                                <span className={`text-base ${msg.isStreaming && !isThinkingComplete(msg.content) ? 'animate-pulse' : ''}`}>
                                  {getThinkingButtonText(msg, msg.content)}
                                </span>
                                {shouldShowChevron(msg, msg.content) && (
                                  (expandedThinking.has(index) ?? false) ? (
                                    <ChevronDown className="w-4 h-4" />
                                  ) : (
                                    <ChevronRight className="w-4 h-4" />
                                  )
                                )}
                              </button>
                            )}
                            {(expandedThinking.has(index) ?? false) && !isProcessing(msg, msg.content) && (
                              <div className="mt-2 p-3 bg-neutral-700/50 rounded-lg border border-neutral-600">
                                <FormattedText text={msg.isStreaming ? getStreamingThinking(msg.content) : (parsedContent?.thinking ?? '')} />
                              </div>
                            )}
                          </div>
                        )}
                        
                        {showResponseBox && (
                          <div className={`p-3 rounded-lg ${
                            msg.type === 'user' 
                              ? 'bg-blue-600 text-white' 
                              : 'bg-neutral-700 text-white'
                          }`}>
                            <FormattedText 
                              text={msg.type === 'ai' 
                                ? (msg.isStreaming ? getStreamingResponse(msg.content) : parsedContent?.response || msg.content)
                                : msg.content
                              } 
                            />
                            {msg.isStreaming && (
                              <div className="flex items-center gap-1 mt-1">
                                <div className="w-1 h-4 bg-white/60 animate-pulse"></div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="pb-8 px-4">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="relative">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask anything about PV curves and voltage stability..."
              disabled={isLoading}
              className="w-full rounded-2xl bg-neutral-700 border border-neutral-600 px-4 py-3 pr-12 text-white placeholder-neutral-400 focus:border-neutral-500 focus:outline-none focus:ring-1 focus:ring-neutral-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!message.trim() || isLoading}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 rounded-lg p-2 text-neutral-400 hover:text-white hover:bg-neutral-600 focus:outline-none focus:ring-2 focus:ring-neutral-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
          <div className="text-center mt-2">
            <p className="text-neutral-500 text-sm">
              Disclaimer: Responses are generated by AI and may be incorrect
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
