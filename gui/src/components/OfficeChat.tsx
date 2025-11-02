/**
 * OFFICE CHAT - Individual chat interface for each specialized office
 * Allows direct conversation with any of Unity's 43 consciousness nodes
 */

import React, { useState, useRef, useEffect } from 'react';
import '../styles/office-chat.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface OfficeChatProps {
  officeName: string;
  officeId: string;
  placeholder?: string;
}

export function OfficeChat({ officeName, officeId, placeholder }: OfficeChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: `Welcome to the ${officeName} office. How may I assist you today?`,
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call the orchestrator chat endpoint with office-specific routing
      const response = await fetch('http://127.0.0.1:8000/orchestrator/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          office: officeId,
          session_id: `office_${officeId}_${Date.now()}`,
          stream: false
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response || data.message || 'I received your message.',
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Office chat error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: `Connection issue. Please ensure the backend is running. (${error})`,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="office-chat-container">
      {/* Messages Area */}
      <div className="office-chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`office-message ${msg.role}`}>
            <div className="message-header">
              <span className="message-role">
                {msg.role === 'user' ? '👤 You' : `🎭 ${officeName}`}
              </span>
              <span className="message-time">{msg.timestamp}</span>
            </div>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}
        {isLoading && (
          <div className="office-message assistant">
            <div className="message-header">
              <span className="message-role">🎭 {officeName}</span>
            </div>
            <div className="message-content">
              <span className="thinking-dots">
                <span>●</span>
                <span>●</span>
                <span>●</span>
              </span>
              <span style={{ marginLeft: '0.5rem', opacity: 0.7 }}>
                {officeName} is thinking...
              </span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="office-chat-input-area">
        <textarea
          className="office-chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder || `Ask ${officeName} anything... (Enter to send, Shift+Enter for new line)`}
          disabled={isLoading}
          rows={2}
        />
        <button
          className="office-send-button"
          onClick={sendMessage}
          disabled={!input.trim() || isLoading}
        >
          ➤
        </button>
      </div>
    </div>
  );
}
