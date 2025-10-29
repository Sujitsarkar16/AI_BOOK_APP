/**
 * WebSocket hook for real-time book generation updates
 */
import { useEffect, useState, useCallback, useRef } from 'react';

export interface WebSocketMessage {
  type: string;
  data: any;
}

export interface AgentStatus {
  agent_name: string;
  status: 'idle' | 'active' | 'error';
  current_task?: string;
}

export interface ChapterProgress {
  chapter_id: number;
  status: 'generating' | 'complete';
  progress_percent: number;
}

export interface UseBookWebSocketReturn {
  agentStatuses: AgentStatus[];
  chapterProgress: Map<number, ChapterProgress>;
  isConnected: boolean;
  sendMessage: (message: WebSocketMessage) => void;
}

export function useBookWebSocket(bookId: number | null): UseBookWebSocketReturn {
  const [agentStatuses, setAgentStatuses] = useState<AgentStatus[]>([]);
  const [chapterProgress, setChapterProgress] = useState<Map<number, ChapterProgress>>(new Map());
  const [isConnected, setIsConnected] = useState(false);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number>();

  const connect = useCallback(() => {
    if (!bookId) return;

    try {
      const ws = new WebSocket(`ws://localhost:8000/ws/books/${bookId}`);
      
      ws.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket connected');
      };
      
      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          switch (message.type) {
            case 'agent_status':
              setAgentStatuses((prev) => {
                const updated = [...prev];
                const index = updated.findIndex((a) => a.agent_name === message.data.agent_name);
                const newStatus: AgentStatus = {
                  agent_name: message.data.agent_name,
                  status: message.data.status,
                  current_task: message.data.current_task,
                };
                
                if (index >= 0) {
                  updated[index] = newStatus;
                } else {
                  updated.push(newStatus);
                }
                return updated;
              });
              break;
              
            case 'chapter_progress':
              setChapterProgress((prev) => {
                const updated = new Map(prev);
                updated.set(message.data.chapter_id, {
                  chapter_id: message.data.chapter_id,
                  status: message.data.status,
                  progress_percent: message.data.progress_percent || 0,
                });
                return updated;
              });
              break;
              
            case 'generation_complete':
              console.log('Generation complete:', message.data);
              break;
              
            case 'error':
              console.error('WebSocket error:', message.data);
              break;
              
            default:
              console.log('Unknown message type:', message.type);
          }
        } catch (e) {
          console.error('Error parsing WebSocket message:', e);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };
      
      ws.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket disconnected');
        
        // Attempt to reconnect after 3 seconds
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect();
        }, 3000);
      };
      
      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setIsConnected(false);
    }
  }, [bookId]);

  useEffect(() => {
    connect();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  return {
    agentStatuses,
    chapterProgress,
    isConnected,
    sendMessage,
  };
}

