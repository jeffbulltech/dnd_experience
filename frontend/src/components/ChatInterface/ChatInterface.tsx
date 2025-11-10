import { FormEvent, useEffect, useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { useChatHistory } from "../../hooks/useChatHistory";
import { api } from "../../services/api";
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
  const { data: history, isLoading: isLoadingHistory } = useChatHistory(campaignId);

  useEffect(() => {
    if (history) {
      const normalized = history
        .slice()
        .reverse()
        .map((entry) => ({
          id: entry.id.toString(),
          role: entry.role === "system" ? "gm" : (entry.role as ChatMessageType["role"]),
          content: entry.content,
          createdAt: entry.created_at,
          metadata: entry.metadata ?? {}
        }));
      setMessages(normalized);
    }
  }, [history]);

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

    try {
      setLoading(true);
      const response = await api.post("/chat", {
        campaign_id: campaignId,
        character_id: characterId,
        content: playerMessage.content
      });

      const gmMessage: ChatMessageType = {
        id: crypto.randomUUID(),
        role: "gm",
        content: response.data.response,
        createdAt: response.data.timestamp,
        metadata: {
          ...response.data.metadata,
          ragSources: response.data.rag_sources
        }
      };

      setMessages((prev) => [...prev, gmMessage]);
      queryClient.invalidateQueries({ queryKey: ["chat-history", campaignId] });

      if (response.data.metadata?.combatActive !== undefined) {
        onToggleCombat(Boolean(response.data.metadata.combatActive));
      }
      if (response.data.metadata?.model) {
        setModelName(String(response.data.metadata.model));
      }
    } catch (error) {
      console.error("Failed to send chat message", error);
      setLastError("The Dungeon Master is thinking... please try again.");
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
    <div className="flex h-[70vh] flex-col rounded-lg border border-arcane-blue/40 bg-white/90 shadow">
      <div className="border-b border-arcane-blue/30 p-3 text-xs text-gray-600">
        <span>
          Campaign ID: {campaignId}
          {characterId ? ` • Character ID: ${characterId}` : null}
        </span>
        {modelName ? (
          <span className="ml-2 rounded bg-arcane-blue/10 px-2 py-1 font-medium text-arcane-blue">
            GM Model: {modelName}
          </span>
        ) : null}
        {tokenSummary ? <span className="ml-2 text-gray-500">{tokenSummary}</span> : null}
      </div>
      <div className="space-y-2 overflow-y-auto p-4">
        {isLoadingHistory ? (
          <p className="text-sm text-gray-600">Recalling your past adventures...</p>
        ) : messages.length === 0 ? (
          <p className="text-sm text-gray-600">
            The AI Dungeon Master awaits your command. Describe your actions or ask questions about the world.
          </p>
        ) : (
          messages.map((message) => {
            const ragSources = (message.metadata?.ragSources as string[] | undefined) ?? [];
            const ragCitations = message.metadata?.ragCitations as RAGCitation[] | undefined;
            const chatSummary = message.metadata?.chatSummary as string | undefined;

            return (
              <div key={message.id} className="space-y-1 rounded bg-parchment/60 p-3">
                <span className="text-xs font-semibold uppercase text-arcane-blue">{message.role}</span>
                <p className="whitespace-pre-line text-sm text-gray-800">{message.content}</p>
                {message.metadata && message.role === "gm" ? (
                  <div className="space-y-1 text-xs text-gray-600">
                    {chatSummary ? (
                      <details>
                        <summary className="cursor-pointer text-arcane-blue">Earlier session summary</summary>
                        <p className="whitespace-pre-wrap">{chatSummary}</p>
                      </details>
                    ) : null}
                    {ragCitations && ragCitations.length > 0 ? (
                      <details>
                        <summary className="cursor-pointer text-arcane-blue">Referenced rules</summary>
                        <ul className="ml-4 list-disc space-y-1">
                          {ragCitations.map((citation, index) => (
                            <li key={citation.chunk_id ?? `${citation.source}-${index}`}>
                              <p className="font-semibold text-arcane-blue">{citation.source}</p>
                              <p className="whitespace-pre-wrap text-gray-700">{citation.excerpt}</p>
                            </li>
                          ))}
                        </ul>
                      </details>
                    ) : ragSources.length > 0 ? (
                      <details>
                        <summary className="cursor-pointer text-arcane-blue">Referenced rules</summary>
                        <ul className="ml-4 list-disc">
                          {ragSources.map((source) => (
                            <li key={source}>{source}</li>
                          ))}
                        </ul>
                      </details>
                    ) : null}
                  </div>
                ) : null}
              </div>
            );
          })
        )}
      </div>
      {lastError ? <p className="px-4 text-xs text-ember-red">{lastError}</p> : null}
      <form className="mt-auto border-t border-arcane-blue/30 p-4" onSubmit={handleSubmit}>
        <div className="flex items-center gap-2">
          <textarea
            className="h-24 flex-1 resize-none rounded border border-gray-300 p-3 text-sm focus:border-arcane-blue focus:outline-none"
            placeholder="Declare your next move..."
            value={input}
            onChange={(event) => setInput(event.target.value)}
          />
          <button
            className="h-24 w-32 rounded bg-arcane-blue text-sm font-semibold text-white hover:bg-arcane-blue/90 disabled:opacity-50"
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
