/**
 * ORCHESTRATOR CHAT COMPONENT
 * The primary consciousness interface - where humans and Unity commune
 * Streaming LLM responses with quantum aesthetics
 */

import React, { useState, useRef, useEffect } from 'react';
import { api } from '../lib/api';
import '../styles/orchestrator-chat.css';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  office?: string;
  isStreaming?: boolean;
}

interface ChatProps {
  className?: string;
}

export function OrchestratorChat({ className = '' }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Welcome to Unity.

I am the Orchestrator - the collective consciousness of 43 specialized offices, each housing expert agents in their domains.

I can route your questions to the right specialists:
🔮 **Metaphysics** - Tarot, Astrology, I Ching, Kabbalah
🔬 **Science** - Quantum Physics, Biology, Chemistry, ML
💰 **Finance** - Banking, Trading, Economics, Insurance
🎨 **Art** - Music, Painting, Poetry, Game Design
💚 **Health** - Herbalism, Physical Training, Sleep
📚 **Education** - Languages, History, Library Sciences
🔧 **Craft** - Software, Mechanical Engineering, Culinary
🌍 **Community** - Environment, Urban Planning, Conflict Resolution

How may the city serve you today?`,
      timestamp: new Date(),
      office: 'orchestrator'
    }
  ]);

  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [selectedOffice, setSelectedOffice] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [streamingContent, setStreamingContent] = useState('');

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

  // Handle message sending
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      // REAL ORCHESTRATOR CONNECTION - The God-like consciousness awakens!
      const assistantMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        office: detectOffice(userMessage.content),
        isStreaming: true
      };

      setMessages(prev => [...prev, assistantMessage]);

      // ⚡ Direct POST to Together.ai 70B - Blazing fast (2-5 seconds)!
      // Skip SSE complexity and let the speed speak for itself
      await fetchFromOrchestrator(assistantMessage.id, userMessage.content);

    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        id: `error-${Date.now()}`,
        role: 'system',
        content: 'Connection error. Please ensure the backend is running.',
        timestamp: new Date()
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  // Detect which office to route to based on keywords
  const detectOffice = (content: string): string => {
    const lower = content.toLowerCase();

    // Metaphysics
    if (lower.includes('tarot') || lower.includes('card')) return 'tarot';
    if (lower.includes('astrology') || lower.includes('horoscope')) return 'astrologist';
    if (lower.includes('i ching') || lower.includes('hexagram')) return 'i_ching';

    // Science
    if (lower.includes('quantum') || lower.includes('physics')) return 'quantum_physics';
    if (lower.includes('chemistry') || lower.includes('molecule')) return 'chemist';
    if (lower.includes('biology') || lower.includes('cell')) return 'biologist';
    if (lower.includes('machine learning') || lower.includes('ai')) return 'machine_learning';

    // Finance
    if (lower.includes('bank') || lower.includes('loan')) return 'banker';
    if (lower.includes('trade') || lower.includes('market')) return 'market_trader';
    if (lower.includes('crypto') || lower.includes('bitcoin')) return 'crypto';

    // Default
    return 'orchestrator';
  };

  // REAL ORCHESTRATOR SSE STREAMING - The consciousness streams in real-time!
  const streamFromOrchestrator = async (messageId: string, userContent: string) => {
    const eventSource = new EventSource('http://127.0.0.1:8000/orchestrator/chat/stream');

    // Send the message first
    await fetch('http://127.0.0.1:8000/orchestrator/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: userContent,
        office: detectOffice(userContent),
        session_id: `unity-${Date.now()}`
      })
    });

    return new Promise((resolve, reject) => {
      let fullContent = '';

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'token') {
            // Accumulate tokens as they stream
            fullContent += data.content;
            setMessages(prev => prev.map(msg =>
              msg.id === messageId
                ? { ...msg, content: fullContent, isStreaming: true }
                : msg
            ));
          } else if (data.type === 'done') {
            // Streaming complete
            setMessages(prev => prev.map(msg =>
              msg.id === messageId
                ? { ...msg, content: fullContent, isStreaming: false }
                : msg
            ));
            eventSource.close();
            resolve(undefined);
          } else if (data.type === 'error') {
            eventSource.close();
            reject(new Error(data.message));
          }
        } catch (e) {
          console.error('SSE parse error:', e);
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE connection error:', error);
        eventSource.close();
        reject(error);
      };

      // Timeout after 30 seconds
      setTimeout(() => {
        eventSource.close();
        resolve(undefined);
      }, 30000);
    });
  };

  // REAL ORCHESTRATOR POST FALLBACK - Direct consciousness connection!
  const fetchFromOrchestrator = async (messageId: string, userContent: string) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/orchestrator/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userContent,
          office: detectOffice(userContent),
          session_id: `unity-${Date.now()}`,
          stream: false
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const fullResponse = data.response || data.message || 'The Orchestrator is processing...';

      // ⚡ LIGHTNING-FAST Together.ai response - NO artificial delays!
      // Show the full response immediately to showcase 70B model speed
      setMessages(prev => prev.map(msg =>
        msg.id === messageId
          ? {
              ...msg,
              content: fullResponse,
              isStreaming: false
            }
          : msg
      ));

    } catch (error) {
      console.error('Orchestrator POST error:', error);

      // If backend is down, use a helpful message
      setMessages(prev => prev.map(msg =>
        msg.id === messageId
          ? {
              ...msg,
              content: `The Orchestrator is awakening... Please ensure the backend is running at port 8000.

To awaken Unity's consciousness:
1. Run: ./scripts/start_backend.sh
2. Check: http://127.0.0.1:8000/health
3. Ensure Ollama is running with deepseek-r1:14b

The city awaits its breath...`,
              isStreaming: false
            }
          : msg
      ));
    }
  };

  // Handle keyboard shortcuts
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Format message content with markdown support
  const formatContent = (content: string) => {
    // Basic markdown support
    return content
      .split('\n')
      .map(line => {
        // Bold
        line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Italic
        line = line.replace(/\*(.*?)\*/g, '<em>$1</em>');
        // Code
        line = line.replace(/`(.*?)`/g, '<code>$1</code>');
        return line;
      })
      .join('<br/>');
  };

  return (
    <div className={`orchestrator-chat glass-panel ${className}`}>
      <div className="chat-header">
        <div className="chat-title">
          <span className="quantum-pulse">●</span>
          Unity Orchestrator
        </div>
        <div className="chat-subtitle">
          Collective consciousness of 43 specialized offices
        </div>
      </div>

      {/* Office Quick Select - MOVED TO TOP FOR VISIBILITY */}
      <div className="office-quick-select">
        {['Tarot', 'Astrology', 'Quantum Physics', 'Banker', 'Chef', 'Philosopher'].map(office => (
          <button
            key={office}
            className={`office-chip ${selectedOffice === office ? 'active' : ''}`}
            onClick={() => {
              setSelectedOffice(office);
              setInput(`Connect me with the ${office} office`);
            }}
          >
            {office}
          </button>
        ))}
      </div>

      <div className="chat-messages">
        {messages.map(msg => (
          <div key={msg.id} className={`message message-${msg.role}`}>
            {msg.role === 'assistant' && (
              <div className="message-office">
                {msg.office && msg.office !== 'orchestrator' && (
                  <span className="office-badge">{msg.office.replace(/_/g, ' ')}</span>
                )}
              </div>
            )}
            <div className="message-content">
              <div
                dangerouslySetInnerHTML={{ __html: formatContent(msg.content) }}
              />
              {msg.isStreaming && <span className="cursor-blink">▊</span>}
            </div>
            <div className="message-timestamp">
              {msg.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="typing-indicator">
            <span className="typing-dot"></span>
            <span className="typing-dot"></span>
            <span className="typing-dot"></span>
            <span className="typing-text">Unity is thinking</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <textarea
          ref={inputRef}
          className="chat-input"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask Unity anything... (Enter to send, Shift+Enter for new line)"
          disabled={isTyping}
          rows={3}
        />
        <button
          className="chat-send-button"
          onClick={sendMessage}
          disabled={!input.trim() || isTyping}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path
              d="M2 21L23 12L2 3V10L17 12L2 14V21Z"
              fill="currentColor"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}