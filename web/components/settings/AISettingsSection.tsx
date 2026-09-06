"use client";

import { useState } from "react";
import { Check, KeyRound } from "lucide-react";
import { useAISettings, useUpdateAISettings } from "@/hooks/useAISettings";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/cn";

export function AISettingsSection() {
  const { data, isLoading } = useAISettings();
  const update = useUpdateAISettings();
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [savedMessage, setSavedMessage] = useState<string | null>(null);

  if (isLoading || !data) {
    return <Skeleton className="h-64" />;
  }

  const saveApiKey = () => {
    setSavedMessage(null);
    update.mutate(
      { api_key: apiKeyInput },
      {
        onSuccess: () => {
          setApiKeyInput("");
          setSavedMessage(apiKeyInput ? "API key saved." : "API key cleared.");
        },
      }
    );
  };

  const toggleModel = (modelId: string) => {
    const currentlyEnabled = data.models.filter((m) => m.enabled).map((m) => m.id);
    const nextEnabled = currentlyEnabled.includes(modelId)
      ? currentlyEnabled.filter((id) => id !== modelId)
      : [...currentlyEnabled, modelId];
    if (nextEnabled.length === 0) return; // at least one must stay enabled
    update.mutate({ enabled_model_ids: nextEnabled });
  };

  const setActive = (modelId: string) => {
    update.mutate({ active_model: modelId });
  };

  return (
    <Card className="p-5">
      <h2 className="text-sm font-semibold text-text mb-1">AI / Groq</h2>
      <p className="text-xs text-text-muted mb-4 leading-relaxed">
        Bring your own Groq API key, and choose which models are available for AI features.
        The key is never shown again once saved — only whether one is set.
      </p>

      <div className="mb-5">
        <label className="text-xs text-text-faint mb-1.5 block">
          Groq API key {data.api_key_set && <span className="text-status-done">· currently set</span>}
        </label>
        <div className="flex gap-2">
          <div className="relative flex-1">
            <KeyRound size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-faint" />
            <input
              type="password"
              value={apiKeyInput}
              onChange={(e) => setApiKeyInput(e.target.value)}
              placeholder={data.api_key_set ? "•••••••••••••••• (replace)" : "gsk_..."}
              className="h-10 w-full rounded-lg border border-border bg-surface-2 pl-9 pr-3 text-sm text-text"
            />
          </div>
          <Button variant="secondary" size="md" onClick={saveApiKey} disabled={update.isPending}>
            Save
          </Button>
          {data.api_key_set && (
            <Button
              variant="ghost"
              size="md"
              onClick={() => {
                setApiKeyInput("");
                update.mutate({ api_key: "" });
              }}
              disabled={update.isPending}
            >
              Clear
            </Button>
          )}
        </div>
        {savedMessage && <p className="text-xs text-status-done mt-1.5">{savedMessage}</p>}
      </div>

      <div>
        <p className="text-xs text-text-faint uppercase tracking-wide mb-2">
          Available models — toggle which ones you want, pick the active one
        </p>
        <ul className="space-y-1.5">
          {data.models.map((m) => (
            <li
              key={m.id}
              className={cn(
                "flex items-center gap-3 rounded-lg border px-3 py-2.5",
                m.enabled ? "border-border" : "border-border opacity-50"
              )}
            >
              <button
                type="button"
                onClick={() => toggleModel(m.id)}
                aria-label={`${m.enabled ? "Disable" : "Enable"} ${m.label}`}
                className={cn(
                  "h-5 w-9 rounded-full shrink-0 relative transition-colors",
                  m.enabled ? "bg-accent" : "bg-surface-2 border border-border-strong"
                )}
              >
                <span
                  className={cn(
                    "absolute top-0.5 h-4 w-4 rounded-full bg-bg transition-transform",
                    m.enabled ? "translate-x-4" : "translate-x-0.5"
                  )}
                />
              </button>

              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-text">{m.label}</p>
                <p className="text-xs text-text-faint truncate">{m.description}</p>
              </div>

              {m.enabled &&
                (data.active_model === m.id ? (
                  <span className="shrink-0 inline-flex items-center gap-1 text-xs text-accent-strong font-medium">
                    <Check size={13} /> Active
                  </span>
                ) : (
                  <Button variant="ghost" size="sm" onClick={() => setActive(m.id)} disabled={update.isPending}>
                    Use this
                  </Button>
                ))}
            </li>
          ))}
        </ul>
      </div>
    </Card>
  );
}
