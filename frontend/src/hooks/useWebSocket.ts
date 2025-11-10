import { useCallback, useEffect, useRef, useState } from "react";

type WebSocketOptions = {
  onMessage?: (event: MessageEvent) => void;
  onOpen?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
};

export function useWebSocket(url: string, options: WebSocketOptions = {}) {
  const socketRef = useRef<WebSocket | null>(null);
  const [isConnected, setConnected] = useState(false);

  const connect = useCallback(() => {
    if (socketRef.current?.readyState === WebSocket.OPEN) return;

    const socket = new WebSocket(url);
    socketRef.current = socket;

    socket.onopen = (event) => {
      setConnected(true);
      options.onOpen?.(event);
    };

    socket.onmessage = (event) => {
      options.onMessage?.(event);
    };

    socket.onclose = (event) => {
      setConnected(false);
      options.onClose?.(event);
      setTimeout(connect, 4000);
    };
  }, [options, url]);

  useEffect(() => {
    connect();
    return () => socketRef.current?.close();
  }, [connect]);

  const send = useCallback((data: unknown) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.warn("WebSocket is not connected");
      return;
    }
    socketRef.current.send(JSON.stringify(data));
  }, []);

  return { isConnected, send };
}
