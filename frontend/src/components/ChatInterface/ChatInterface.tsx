import { FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { useChatHistory } from "../../hooks/useChatHistory";
import { ChatMessage as ChatMessageType, RAGCitation } from "../../types";

type ChatInterfaceProps = {
  campaignId: number;
  characterId?: number;
  onToggleCombat: (active: boolean) => void;
};

function ChatInterface({ campaignId, characterId, onToggleCombat }: ChatInterfaceProps): JSX.Element {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setLoading] = useState(false);
  const [lastError, setLastError] = useState<string | null>(null);
  const [modelName, setModelName] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const {
    data: historyData,
    isLoading: isLoadingHistory,
    hasNextPage,
    fetchNextPage,
    isFetchingNextPage,
  } = useChatHistory(campaignId);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (historyData) {
      // Flatten all pages, each page has items in newest-first order
      const allEntries = historyData.pages.flatMap((page) => page.items);
      // Reverse to chronological (oldest first) and deduplicate by id
      const seen = new Set<number>();
      const unique = allEntries.reverse().filter((entry) => {
        if (seen.has(entry.id)) return false;
        seen.add(entry.id);
        return true;
      });
      const normalized = unique.map((entry) => ({
        id: entry.id.toString(),
        role: entry.role === "system" ? "gm" : (entry.role as ChatMessageType["role"]),
        content: entry.content,
        createdAt: entry.created_at,
        metadata: entry.metadata ?? {}
      }));
      setMessages(normalized);
    }
  }, [historyData]);

  const handleLoadEarlier = useCallback(() => {
    if (!hasNextPage || isFetchingNextPage) return;
    const container = messagesContainerRef.current;
    const prevScrollHeight = container?.scrollHeight ?? 0;
    fetchNextPage().then(() => {
      // Preserve scroll position after prepending older messages
      requestAnimationFrame(() => {
        if (container) {
          const newScrollHeight = container.scrollHeight;
          container.scrollTop = newScrollHeight - prevScrollHeight;
        }
      });
    });
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!input.trim()) return;

    setLastError(null);

    const playerMessage: ChatMessageType = {
      id: crypto.randomUUID(),
      role: "player",
      content: input,
      createdAt: new Date().toISOString()
    };

    setMessages((prev) => [...prev, playerMessage]);
    setInput("");

    const gmMessageId = crypto.randomUUID();

    try {
      setLoading(true);

      // Add an empty GM message that we'll fill in as tokens stream
      setMessages((prev) => [
        ...prev,
        { id: gmMessageId, role: "gm", content: "", createdAt: new Date().toISOString() }
      ]);

      const token = localStorage.getItem("dnd_ai_token");
      const response = await fetch("/api/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          campaign_id: campaignId,
          character_id: characterId,
          content: playerMessage.content
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Parse SSE events from buffer
        const events = buffer.split("\n\n");
        // Keep the last (possibly incomplete) chunk in the buffer
        buffer = events.pop() ?? "";

        for (const eventBlock of events) {
          const lines = eventBlock.split("\n");
          let eventType = "";
          let data = "";

          for (const line of lines) {
            if (line.startsWith("event: ")) eventType = line.slice(7);
            else if (line.startsWith("data: ")) data = line.slice(6);
          }

          if (eventType === "token" && data) {
            const token = JSON.parse(data) as string;
            setMessages((prev) =>
              prev.map((m) => (m.id === gmMessageId ? { ...m, content: m.content + token } : m))
            );
          } else if (eventType === "done" && data) {
            const payload = JSON.parse(data) as {
              response: string;
              rag_sources: string[];
              metadata: Record<string, unknown>;
              timestamp: string;
            };

            // Finalize the GM message with full content and metadata
            setMessages((prev) =>
              prev.map((m) =>
                m.id === gmMessageId
                  ? {
                      ...m,
                      content: payload.response,
                      createdAt: payload.timestamp,
                      metadata: { ...payload.metadata, ragSources: payload.rag_sources }
                    }
                  : m
              )
            );

            queryClient.invalidateQueries({ queryKey: ["chat-history", campaignId] });

            if (payload.metadata?.combatActive !== undefined) {
              onToggleCombat(Boolean(payload.metadata.combatActive));
            }
            if (payload.metadata?.model) {
              setModelName(String(payload.metadata.model));
            }
          }
        }
      }
    } catch (error) {
      console.error("Failed to send chat message", error);
      setLastError("The Dungeon Master is thinking... please try again.");
      // Remove the empty GM message on failure
      setMessages((prev) => prev.filter((m) => m.id !== gmMessageId));
    } finally {
      setLoading(false);
    }
  };

  const tokenSummary = useMemo(() => {
    const gmMessage = messages
      .slice()
      .reverse()
      .find((message) => message.role === "gm" && message.metadata);
    if (!gmMessage?.metadata) return null;

    const promptTokens = gmMessage.metadata?.promptTokens as number | undefined;
    const completionTokens = gmMessage.metadata?.completionTokens as number | undefined;
    if (promptTokens === undefined && completionTokens === undefined) return null;

    return `${promptTokens ?? "?"}/${completionTokens ?? "?"} tokens`;
  }, [messages]);

  return (
    <div className="parchment-card flex h-[70vh] flex-col overflow-hidden">
      <div className="border-b-2 border-arcane-blue-800/30 bg-gradient-to-r from-arcane-blue-50 to-parchment-100 p-3 flex-shrink-0">
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="font-display font-semibold text-arcane-blue-800">
            Campaign: {campaignId}
            {characterId ? ` • Hero: ${characterId}` : null}
          </span>
          {modelName ? (
            <span className="rounded-md border border-arcane-blue-300 bg-arcane-blue-100 px-2 py-1 font-display font-medium text-arcane-blue-800">
              GM: {modelName}
            </span>
          ) : null}
          {tokenSummary ? (
            <span className="text-gray-600 font-medium">{tokenSummary}</span>
          ) : null}
        </div>
      </div>
      <div ref={messagesContainerRef} className="scroll-container space-y-3 p-4 overflow-y-auto flex-1 min-h-0">
        {isLoadingHistory ? (
          <div className="flex items-center gap-2 text-sm text-gray-700">
            <span className="text-lg">🔮</span>
            <p className="font-display">Recalling your past adventures...</p>
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-lg mb-2">⚔️</p>
            <p className="text-sm font-display text-gray-700">
              The AI Dungeon Master awaits your command. Describe your actions or ask questions about the world.
            </p>
          </div>
        ) : (
          <>
            {hasNextPage ? (
              <div className="text-center pb-2">
                <button
                  type="button"
                  className="text-xs font-display font-semibold text-arcane-blue-700 hover:text-arcane-blue-500 disabled:opacity-50"
                  disabled={isFetchingNextPage}
                  onClick={handleLoadEarlier}
                >
                  {isFetchingNextPage ? "Loading..." : "Load earlier messages"}
                </button>
              </div>
            ) : null}
            {messages.map((message) => {
            const ragSources = (message.metadata?.ragSources as string[] | undefined) ?? [];
            const ragCitations = message.metadata?.ragCitations as RAGCitation[] | undefined;
            const chatSummary = message.metadata?.chatSummary as string | undefined;

            return (
              <div key={message.id} className="space-y-2 rounded-md border-2 border-arcane-blue-200/50 bg-parchment-50/90 p-4 shadow-sm">
                <div className="flex items-center gap-2">
                  <span className="text-lg">
                    {message.role === "gm" ? "👑" : "⚔️"}
                  </span>
                  <span className="text-xs font-display font-bold uppercase text-arcane-blue-800">
                    {message.role === "gm" ? "Dungeon Master" : "Adventurer"}
                  </span>
                </div>
                <p className="whitespace-pre-line text-sm leading-relaxed text-gray-800">{message.content}</p>
                {message.metadata && message.role === "gm" ? (
                  <div className="space-y-1 text-xs text-gray-600">
                    {chatSummary ? (
                      <details>
                        <summary className="cursor-pointer text-arcane-blue">Earlier session summary</summary>
                        <p className="whitespace-pre-wrap">{chatSummary}</p>
                      </details>
                    ) : null}
                    {ragCitations && ragCitations.length > 0 ? (
                      <details className="mt-2 rounded-md border border-arcane-blue-200/50 bg-parchment-50/80 p-2">
                        <summary className="cursor-pointer font-display font-semibold text-arcane-blue-800 hover:text-arcane-blue-600">
                          📚 Referenced rules
                        </summary>
                        <ul className="ml-4 mt-2 list-disc space-y-2">
                          {ragCitations.map((citation, index) => (
                            <li key={citation.chunk_id ?? `${citation.source}-${index}`} className="text-xs">
                              <p className="font-display font-semibold text-arcane-blue-800">{citation.source}</p>
                              <p className="whitespace-pre-wrap text-gray-700">{citation.excerpt}</p>
                            </li>
                          ))}
                        </ul>
                      </details>
                    ) : ragSources.length > 0 ? (
                      <details className="mt-2 rounded-md border border-arcane-blue-200/50 bg-parchment-50/80 p-2">
                        <summary className="cursor-pointer font-display font-semibold text-arcane-blue-800 hover:text-arcane-blue-600">
                          📚 Referenced rules
                        </summary>
                        <ul className="ml-4 mt-2 list-disc">
                          {ragSources.map((source) => (
                            <li key={source} className="text-xs text-gray-700">{source}</li>
                          ))}
                        </ul>
                      </details>
                    ) : null}
                  </div>
                ) : null}
              </div>
            );
          })}
            {/* Scroll anchor */}
            <div ref={messagesEndRef} />
            {isLoading && (
              <div className="flex items-center gap-2 text-sm text-gray-700">
                <span className="text-lg animate-pulse">🔮</span>
                <p className="font-display">The Dungeon Master is thinking...</p>
              </div>
            )}
          </>
        )}
      </div>
      {lastError ? (
        <div className="mx-4 mb-2 rounded-md border-2 border-ember-red-600 bg-ember-red-50 p-2">
          <p className="text-xs font-medium text-ember-red-800">{lastError}</p>
        </div>
      ) : null}
      <form className="mt-auto border-t-2 border-arcane-blue-800/30 bg-gradient-to-r from-parchment-50 to-parchment-100 p-4 flex-shrink-0" onSubmit={handleSubmit}>
        <div className="flex items-end gap-3">
          <textarea
            className="fantasy-input h-24 flex-1 resize-none"
            placeholder="Declare your next move, adventurer..."
            value={input}
            onChange={(event) => setInput(event.target.value)}
          />
          <button
            className="fantasy-button h-24 w-32 disabled:opacity-50"
            disabled={isLoading}
            type="submit"
          >
            {isLoading ? "Thinking..." : "Send"}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ChatInterface;
