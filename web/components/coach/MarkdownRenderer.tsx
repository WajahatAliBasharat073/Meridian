"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";

function CodeBlock({ language, code }: { language: string; code: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {}
  };

  return (
    <div className="my-3 rounded-xl border border-border/80 bg-surface-3 overflow-hidden text-xs shadow-sm">
      <div className="flex items-center justify-between px-3.5 py-1.5 bg-surface-2 border-b border-border text-text-faint text-[11px] font-mono">
        <span>{language || "code"}</span>
        <button
          onClick={handleCopy}
          type="button"
          className="flex items-center gap-1 text-[11px] hover:text-text transition-colors"
        >
          {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
          <span>{copied ? "Copied" : "Copy"}</span>
        </button>
      </div>
      <pre className="p-3.5 overflow-x-auto text-text leading-relaxed font-mono font-normal">
        <code>{code}</code>
      </pre>
    </div>
  );
}

export function MarkdownRenderer({ content }: { content: string }) {
  // Simple, robust multi-line parser for structured markdown
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];
  let inCodeBlock = false;
  let codeLang = "";
  let codeBuffer: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Code blocks
    if (line.trim().startsWith("```")) {
      if (!inCodeBlock) {
        inCodeBlock = true;
        codeLang = line.trim().replace(/^```/, "").trim();
        codeBuffer = [];
      } else {
        inCodeBlock = false;
        elements.push(
          <CodeBlock
            key={`code-${i}`}
            language={codeLang}
            code={codeBuffer.join("\n")}
          />
        );
        codeBuffer = [];
      }
      continue;
    }

    if (inCodeBlock) {
      codeBuffer.push(line);
      continue;
    }

    // Headings
    if (line.startsWith("### ")) {
      elements.push(
        <h4 key={i} className="text-sm font-semibold text-text mt-3 mb-1.5 flex items-center gap-1.5">
          {formatInline(line.replace("### ", ""))}
        </h4>
      );
      continue;
    }
    if (line.startsWith("## ")) {
      elements.push(
        <h3 key={i} className="text-base font-semibold text-text mt-4 mb-2">
          {formatInline(line.replace("## ", ""))}
        </h3>
      );
      continue;
    }
    if (line.startsWith("# ")) {
      elements.push(
        <h2 key={i} className="text-lg font-bold text-text mt-4 mb-2">
          {formatInline(line.replace("# ", ""))}
        </h2>
      );
      continue;
    }

    // Bullet lists
    if (line.trim().startsWith("- ") || line.trim().startsWith("* ")) {
      elements.push(
        <li key={i} className="ml-4 list-disc text-xs leading-relaxed text-text/90 my-0.5">
          {formatInline(line.trim().substring(2))}
        </li>
      );
      continue;
    }

    // Numbered lists
    const numMatch = line.trim().match(/^(\d+)\.\s+(.*)/);
    if (numMatch) {
      elements.push(
        <li key={i} className="ml-4 list-decimal text-xs leading-relaxed text-text/90 my-0.5">
          {formatInline(numMatch[2])}
        </li>
      );
      continue;
    }

    // Blockquote
    if (line.startsWith("> ")) {
      elements.push(
        <blockquote key={i} className="border-l-2 border-accent/60 pl-3 my-2 text-xs italic text-text-muted bg-surface-2/40 py-1 rounded-r">
          {formatInline(line.replace("> ", ""))}
        </blockquote>
      );
      continue;
    }

    // Empty line
    if (!line.trim()) {
      elements.push(<div key={i} className="h-1.5" />);
      continue;
    }

    // Regular paragraph
    elements.push(
      <p key={i} className="text-xs leading-relaxed text-text/90 my-1">
        {formatInline(line)}
      </p>
    );
  }

  // Flush open code block if any
  if (inCodeBlock && codeBuffer.length > 0) {
    elements.push(
      <CodeBlock
        key={`code-end`}
        language={codeLang}
        code={codeBuffer.join("\n")}
      />
    );
  }

  return <div className="space-y-0.5 select-text">{elements}</div>;
}

function formatInline(text: string): React.ReactNode {
  // Format bold **text**, inline code `code`, and plain text
  const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);

  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={index} className="font-semibold text-text">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code
          key={index}
          className="px-1.5 py-0.5 mx-0.5 rounded bg-surface-3 text-accent-strong border border-border text-[11px] font-mono"
        >
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}
