"use client";
import { CopilotKit } from "@copilotkit/react-core/v2";
import { createContext, useState } from "react";

export const ModelContext = createContext<{
  model: string | undefined;
  set_model: (m: string | undefined) => void;
}>({ model: undefined, set_model: () => {} });

export const ThreadContext = createContext<{
  thread_id: string | undefined;
  set_thread_id: (m: string | undefined) => void;
}>({
  thread_id: crypto.randomUUID(),
  set_thread_id: () => {},
});

export function CopilotProvider({ children }: { children: React.ReactNode }) {
  const [model, set_model] = useState<string | undefined>(undefined);
  const [thread_id, set_thread_id] = useState<string | undefined>(() =>
    crypto.randomUUID(),
  );
  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      agent="simple"
      properties={{ model }}
      threadId={thread_id}
    >
      <ModelContext.Provider value={{ model, set_model: set_model }}>
        <ThreadContext.Provider
          value={{ thread_id, set_thread_id: set_thread_id }}
        >
          {children}
        </ThreadContext.Provider>
      </ModelContext.Provider>
    </CopilotKit>
  );
}
