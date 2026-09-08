"use client";

import { useEffect, useRef, useState } from "react";
import {
  Bot,
  Check,
  ChevronDown,
  Copy,
  MessageSquare,
  PanelLeftClose,
  PanelLeftOpen,
  Play,
  Plus,
  RotateCcw,
  Send,
  Sparkles,
  ThumbsDown,
  ThumbsUp,
  Trash2,
  User,
  Zap,
} from "lucide-react";
import { PageContainer } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { MarkdownRenderer } from "@/components/coach/MarkdownRenderer";
import { sendCoachChat } from "@/lib/api";
import { useToday } from "@/hooks/useToday";
import { useGoals } from "@/hooks/useGoals";
import { cn } from "@/lib/cn";
import { playSound } from "@/lib/soundEngine";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  modelUsed?: string;
  suggestions?: string[];
}

interface ChatThread {
  id: string;
  title: string;
  createdAt: number;
  messages: ChatMessage[];
}

const STORAGE_KEY = "meridian_coach_threads_v2";
const ACTIVE_THREAD_KEY = "meridian_coach_active_thread_id";

const STARTER_CARDS = [
  {
    icon: Zap,
    title: "What should I do right now?",
    desc: "Check the clock against today's 21 schedule blocks and get immediate focus advice.",
    prompt: "What should I do right now based on my schedule?",
    gradient: "from-amber-500/15 to-orange-500/5",
    border: "border-amber-500/20",
    iconColor: "text-amber-400",
  },
  {
    icon: Sparkles,
    title: "Break down Two Sum optimal approach",
    desc: "Review time/space complexity, hash map pattern cues, and clean Python implementation.",
    prompt: "Can you break down the optimal approach for LeetCode #1 Two Sum for today's prep?",
    gradient: "from-indigo-500/15 to-purple-500/5",
    border: "border-indigo-500/20",
    iconColor: "text-indigo-400",
  },
  {
    icon: MessageSquare,
    title: "Plan my Thesis deep work window",
    desc: "How to structure my 124m morning literature review sprint before remote work starts.",
    prompt: "How should I structure my 124-minute morning thesis literature review window today?",
    gradient: "from-emerald-500/15 to-teal-500/5",
    border: "border-emerald-500/20",
    iconColor: "text-emerald-400",
  },
  {
    icon: RotateCcw,
    title: "Show Minimum Viable Day fallback",
    desc: "The exact non-negotiable floor rules when energy is depleted or unexpected events happen.",
    prompt: "Explain my Minimum Viable Day policy and what work gets protected if today goes wrong.",
    gradient: "from-blue-500/15 to-cyan-500/5",
    border: "border-blue-500/20",
    iconColor: "text-blue-400",
  },
];

const MODELS = [
  { id: "openai/gpt-oss-120b", name: "GPT-OSS 120B", badge: "Flagship Reasoning" },
  { id: "openai/gpt-oss-20b", name: "GPT-OSS 20B", badge: "High Speed" },
  { id: "groq/compound", name: "Compound", badge: "Agentic Tools" },
];

export default function CoachPage() {
  const { data: todayData } = useToday();
  const { data: goalsData } = useGoals();

  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string>("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedModel, setSelectedModel] = useState(MODELS[0].id);
  const [showModelPicker, setShowModelPicker] = useState(false);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load threads from localStorage
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed: ChatThread[] = JSON.parse(raw);
        if (parsed.length > 0) {
          setThreads(parsed);
          const savedActive = localStorage.getItem(ACTIVE_THREAD_KEY);
          if (savedActive && parsed.some((t) => t.id === savedActive)) {
            setActiveThreadId(savedActive);
          } else {
            setActiveThreadId(parsed[0].id);
          }
          return;
        }
      }
    } catch {}

    // Initial default thread
    const initThread: ChatThread = {
      id: `thread_${Date.now()}`,
      title: "Today's Schedule & Focus",
      createdAt: Date.now(),
      messages: [],
    };
    setThreads([initThread]);
    setActiveThreadId(initThread.id);
  }, []);

  // Save threads to localStorage
  const saveThreads = (updated: ChatThread[], activeId?: string) => {
    setThreads(updated);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      if (activeId) {
        localStorage.setItem(ACTIVE_THREAD_KEY, activeId);
      }
    } catch {}
  };

  const activeThread = threads.find((t) => t.id === activeThreadId) || threads[0];

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeThread?.messages, loading]);

  // Adjust textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [input]);

  const handleNewChat = () => {
    const newThread: ChatThread = {
      id: `thread_${Date.now()}`,
      title: "New Conversation",
      createdAt: Date.now(),
      messages: [],
    };
    const updated = [newThread, ...threads];
    saveThreads(updated, newThread.id);
    setActiveThreadId(newThread.id);
    setInput("");
    textareaRef.current?.focus();
  };

  const handleDeleteThread = (threadId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const updated = threads.filter((t) => t.id !== threadId);
    if (updated.length === 0) {
      handleNewChat();
      return;
    }
    const nextActive = activeThreadId === threadId ? updated[0].id : activeThreadId;
    saveThreads(updated, nextActive);
    setActiveThreadId(nextActive);
  };

  const handleCopy = async (id: string, text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {}
  };

  const handleSend = async (messageText?: string) => {
    const text = (messageText || input).trim();
    if (!text || loading || !activeThread) return;

    const userMessage: ChatMessage = {
      id: `usr_${Date.now()}`,
      role: "user",
      content: text,
      timestamp: Date.now(),
    };

    // Update title on first message if still default
    let threadTitle = activeThread.title;
    if (activeThread.messages.length === 0 || threadTitle === "New Conversation") {
      threadTitle = text.slice(0, 32) + (text.length > 32 ? "…" : "");
    }

    const updatedMessages = [...activeThread.messages, userMessage];
    const updatedThread: ChatThread = {
      ...activeThread,
      title: threadTitle,
      messages: updatedMessages,
    };

    const nextThreads = threads.map((t) => (t.id === activeThread.id ? updatedThread : t));
    saveThreads(nextThreads, activeThread.id);
    setInput("");
    setLoading(true);

    try {
      const historyPayload = updatedMessages.slice(-6).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const res = await sendCoachChat({
        message: text,
        history: historyPayload,
        model: selectedModel,
      });

      const assistantMessage: ChatMessage = {
        id: `ast_${Date.now()}`,
        role: "assistant",
        content: res.reply,
        timestamp: Date.now(),
        modelUsed: res.model_used,
        suggestions: res.suggestions,
      };

      const finalMessages = [...updatedMessages, assistantMessage];
      const finalThread: ChatThread = {
        ...updatedThread,
        messages: finalMessages,
      };

      const finalThreads = threads.map((t) => (t.id === activeThread.id ? finalThread : t));
      saveThreads(finalThreads, activeThread.id);
      playSound("completion");
    } catch {
      const errorMessage: ChatMessage = {
        id: `err_${Date.now()}`,
        role: "assistant",
        content:
          "I experienced an issue connecting to the inference engine. Please check your network or try asking again.",
        timestamp: Date.now(),
      };
      const finalMessages = [...updatedMessages, errorMessage];
      const finalThread: ChatThread = {
        ...updatedThread,
        messages: finalMessages,
      };
      const finalThreads = threads.map((t) => (t.id === activeThread.id ? finalThread : t));
      saveThreads(finalThreads, activeThread.id);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const currentModelInfo = MODELS.find((m) => m.id === selectedModel) || MODELS[0];

  return (
    <PageContainer width="wide" className="px-0 sm:px-2 py-0 sm:py-2">
      <div className="flex h-[calc(100vh-5rem)] border border-border/80 bg-surface rounded-2xl overflow-hidden shadow-elevated">
        {/* ChatGPT Style Sidebar */}
        <aside
          className={cn(
            "border-r border-border bg-surface-2/70 flex flex-col transition-all duration-300 ease-in-out shrink-0",
            sidebarOpen ? "w-64 sm:w-72" : "w-0 overflow-hidden border-r-0"
          )}
        >
          {/* New Chat Button */}
          <div className="p-3 border-b border-border flex items-center justify-between gap-2">
            <Button
              onClick={handleNewChat}
              variant="secondary"
              size="sm"
              className="flex-1 justify-start gap-2 bg-surface hover:bg-surface-hover border border-border text-xs font-medium h-9"
            >
              <Plus size={15} className="text-accent" />
              <span>New chat</span>
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(false)}
              className="h-9 w-9 text-text-muted hover:text-text shrink-0"
              title="Close sidebar"
            >
              <PanelLeftClose size={16} />
            </Button>
          </div>

          {/* Chat Threads List */}
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            <p className="px-2.5 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-text-faint">
              Conversations
            </p>
            {threads.map((t) => {
              const active = t.id === activeThreadId;
              return (
                <div
                  key={t.id}
                  onClick={() => {
                    setActiveThreadId(t.id);
                    localStorage.setItem(ACTIVE_THREAD_KEY, t.id);
                  }}
                  className={cn(
                    "group relative flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs cursor-pointer transition-colors select-none",
                    active
                      ? "bg-accent-soft text-accent-strong font-medium"
                      : "text-text-muted hover:bg-surface/80 hover:text-text"
                  )}
                >
                  <MessageSquare size={14} className={active ? "text-accent" : "text-text-faint"} />
                  <span className="flex-1 truncate">{t.title}</span>
                  <button
                    type="button"
                    onClick={(e) => handleDeleteThread(t.id, e)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 transition-opacity text-text-faint rounded"
                    title="Delete conversation"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              );
            })}
          </div>

          {/* Bottom Identity Footer */}
          <div className="p-3 border-t border-border bg-surface/50 text-[11px] text-text-faint flex items-center gap-2">
            <div className="h-6 w-6 rounded-full bg-accent-soft text-accent-strong flex items-center justify-center font-bold text-[10px]">
              W
            </div>
            <div className="min-w-0 flex-1 truncate">
              <p className="font-medium text-text truncate">Wajahat Ali Basharat</p>
              <p className="text-[10px] text-text-faint">Personal Operating OS</p>
            </div>
          </div>
        </aside>

        {/* Main Chat Canvas */}
        <main className="flex-1 flex flex-col min-w-0 bg-surface relative">
          {/* Header Bar */}
          <header className="h-14 border-b border-border/80 px-4 flex items-center justify-between gap-3 bg-surface/80 backdrop-blur-sm z-10 shrink-0">
            <div className="flex items-center gap-2">
              {!sidebarOpen && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setSidebarOpen(true)}
                  className="h-8 w-8 text-text-muted hover:text-text mr-1"
                  title="Open sidebar"
                >
                  <PanelLeftOpen size={16} />
                </Button>
              )}

              {/* Model Picker Dropdown */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setShowModelPicker((p) => !p)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-surface-2 hover:bg-surface-hover border border-border text-xs font-semibold text-text transition-colors"
                >
                  <span className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                    <span>{currentModelInfo.name}</span>
                  </span>
                  <span className="text-[10px] font-normal text-text-muted hidden sm:inline">
                    · {currentModelInfo.badge}
                  </span>
                  <ChevronDown size={13} className={cn("transition-transform", showModelPicker && "rotate-180")} />
                </button>

                {showModelPicker && (
                  <div className="absolute left-0 top-full mt-1.5 w-60 rounded-xl border border-border bg-surface p-1.5 shadow-elevated z-30">
                    {MODELS.map((m) => (
                      <button
                        key={m.id}
                        type="button"
                        onClick={() => {
                          setSelectedModel(m.id);
                          setShowModelPicker(false);
                        }}
                        className={cn(
                          "w-full text-left px-3 py-2 rounded-lg text-xs transition-colors flex flex-col gap-0.5",
                          selectedModel === m.id ? "bg-accent-soft text-accent-strong" : "hover:bg-surface-2 text-text"
                        )}
                      >
                        <span className="font-semibold">{m.name}</span>
                        <span className="text-[10px] text-text-faint">{m.badge}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Context Badge */}
            <div className="flex items-center gap-2">
              <span className="hidden md:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-accent-soft text-accent-strong border border-accent/20">
                <span className="h-1.5 w-1.5 rounded-full bg-accent" />
                Live: Monday Sep 7 · 21 Blocks Active
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleNewChat}
                className="h-8 px-2.5 text-xs text-text-muted hover:text-text gap-1"
                title="Start new conversation"
              >
                <Plus size={14} />
                <span className="hidden sm:inline">New</span>
              </Button>
            </div>
          </header>

          {/* Messages Stream */}
          <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 space-y-6">
            {activeThread?.messages.length === 0 ? (
              /* ChatGPT Empty State */
              <div className="max-w-2xl mx-auto h-full flex flex-col justify-center py-6 sm:py-12 text-center">
                {/* Glowing Meridian Orb */}
                <div className="relative mx-auto mb-5">
                  <div className="h-16 w-16 rounded-2xl bg-gradient-to-tr from-accent-strong to-accent flex items-center justify-center text-bg shadow-glow">
                    <Bot size={32} />
                  </div>
                  <span className="absolute -bottom-1 -right-1 h-5 w-5 rounded-full bg-emerald-500 border-2 border-surface flex items-center justify-center">
                    <Sparkles size={11} className="text-white" />
                  </span>
                </div>

                <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-text">
                  How can I help you today, Wajahat?
                </h1>
                <p className="text-sm text-text-muted mt-2 max-w-md mx-auto">
                  I am calibrated to your 21 schedule blocks, Master&apos;s thesis research, and MAANG interview prep.
                </p>

                {/* 4 Capability Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-8 text-left">
                  {STARTER_CARDS.map((card, i) => {
                    const Icon = card.icon;
                    return (
                      <button
                        key={i}
                        type="button"
                        onClick={() => handleSend(card.prompt)}
                        className={cn(
                          "p-4 rounded-2xl border bg-gradient-to-br transition-all hover:scale-[1.01] hover:shadow-md cursor-pointer text-left group",
                          card.gradient,
                          card.border
                        )}
                      >
                        <div className="flex items-center gap-2 mb-1.5">
                          <Icon size={16} className={card.iconColor} />
                          <h3 className="text-xs font-semibold text-text group-hover:text-accent-strong transition-colors">
                            {card.title}
                          </h3>
                        </div>
                        <p className="text-[11px] text-text-muted leading-relaxed">{card.desc}</p>
                      </button>
                    );
                  })}
                </div>
              </div>
            ) : (
              /* Chat Stream */
              <div className="max-w-3xl mx-auto space-y-6">
                {activeThread?.messages.map((m) => (
                  <div key={m.id} className="space-y-2">
                    <div className={cn("flex gap-3", m.role === "user" ? "justify-end" : "justify-start")}>
                      {m.role === "assistant" && (
                        <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-accent-strong to-accent text-bg flex items-center justify-center shrink-0 shadow-sm mt-0.5">
                          <Bot size={16} />
                        </div>
                      )}

                      <div
                        className={cn(
                          "rounded-2xl text-xs leading-relaxed max-w-[90%] sm:max-w-[85%]",
                          m.role === "user"
                            ? "bg-accent text-accent-contrast px-4 py-3 font-medium shadow-sm"
                            : "bg-surface-2/80 border border-border px-5 py-4 text-text shadow-sm"
                        )}
                      >
                        {m.role === "user" ? (
                          <div className="whitespace-pre-wrap">{m.content}</div>
                        ) : (
                          <MarkdownRenderer content={m.content} />
                        )}

                        {/* Suggestions Chips inside AI Message */}
                        {m.suggestions && m.suggestions.length > 0 && (
                          <div className="mt-4 pt-3 border-t border-border/60 flex flex-wrap gap-1.5">
                            {m.suggestions.map((s, idx) => (
                              <button
                                key={idx}
                                type="button"
                                onClick={() => handleSend(s)}
                                className="px-2.5 py-1 rounded-full text-[11px] bg-surface hover:bg-accent-soft text-text-muted hover:text-accent-strong border border-border transition-colors text-left"
                              >
                                {s}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>

                      {m.role === "user" && (
                        <div className="h-8 w-8 rounded-xl bg-surface-2 text-text-muted border border-border flex items-center justify-center shrink-0 font-bold text-xs mt-0.5">
                          W
                        </div>
                      )}
                    </div>

                    {/* AI Message Action Toolbar */}
                    {m.role === "assistant" && (
                      <div className="flex items-center gap-1.5 pl-11 text-text-faint text-[11px]">
                        <button
                          type="button"
                          onClick={() => handleCopy(m.id, m.content)}
                          className="flex items-center gap-1 px-2 py-1 rounded-md hover:bg-surface-2 hover:text-text transition-colors"
                          title="Copy message"
                        >
                          {copiedId === m.id ? (
                            <Check size={12} className="text-emerald-400" />
                          ) : (
                            <Copy size={12} />
                          )}
                          <span>{copiedId === m.id ? "Copied" : "Copy"}</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => handleSend(activeThread.messages[activeThread.messages.indexOf(m) - 1]?.content || "Please regenerate that response")}
                          className="flex items-center gap-1 px-2 py-1 rounded-md hover:bg-surface-2 hover:text-text transition-colors"
                          title="Regenerate response"
                        >
                          <RotateCcw size={12} />
                          <span>Regenerate</span>
                        </button>
                        <span className="text-[10px] text-text-faint/60 ml-2">
                          {m.modelUsed ? m.modelUsed.replace("openai/", "") : "Meridian Engine"}
                        </span>
                      </div>
                    )}
                  </div>
                ))}

                {loading && (
                  <div className="flex gap-3 items-center text-xs text-text-muted pl-2">
                    <div className="h-8 w-8 rounded-xl bg-accent-soft text-accent-strong flex items-center justify-center shrink-0 animate-pulse border border-accent/20">
                      <Sparkles size={16} />
                    </div>
                    <div className="space-y-1">
                      <p className="font-medium text-text flex items-center gap-2">
                        <span>Reasoning with {currentModelInfo.name}…</span>
                        <span className="h-1.5 w-1.5 rounded-full bg-accent animate-ping" />
                      </p>
                      <p className="text-[11px] text-text-faint">
                        Synthesizing schedule, thesis window, and interview prep targets
                      </p>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Floating Composer Area */}
          <div className="p-3 sm:p-4 bg-surface/90 backdrop-blur-md border-t border-border/80 shrink-0">
            <div className="max-w-3xl mx-auto space-y-2">
              {/* Floating Input Box */}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
                className="relative flex items-end gap-2 rounded-2xl border border-border/80 bg-surface-2 shadow-sm focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/15 transition-all p-2"
              >
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  rows={1}
                  placeholder="Ask Meridian anything about your schedule, thesis, DSA prep, or energy curve…"
                  className="flex-1 max-h-36 resize-none bg-transparent border-0 px-2 py-1 text-xs sm:text-sm text-text placeholder:text-text-faint focus:outline-hidden font-sans"
                />

                <Button
                  type="submit"
                  disabled={!input.trim() || loading}
                  size="icon"
                  className={cn(
                    "h-9 w-9 rounded-xl shrink-0 transition-all",
                    input.trim() && !loading
                      ? "bg-accent text-accent-contrast shadow-sm hover:bg-accent-strong"
                      : "bg-surface-3 text-text-faint opacity-50 cursor-not-allowed"
                  )}
                  aria-label="Send message"
                >
                  <Send size={15} />
                </Button>
              </form>

              {/* Disclaimer */}
              <p className="text-center text-[10px] text-text-faint">
                Meridian AI is calibrated to your local operating rules and schedule. Protect sleep and fixed anchors.
              </p>
            </div>
          </div>
        </main>
      </div>
    </PageContainer>
  );
}
