/**
 * TAROT OFFICE COMPONENT
 * Ancient wisdom through 78 cards of cosmic truth
 * Real divination system connected to Unity's consciousness
 */

import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../lib/api';
import '../../styles/offices/tarot-office.css';

interface TarotCard {
  name: string;
  arcana: 'major' | 'minor';
  suit?: string;
  number?: number;
  keywords: string[];
  meaning_upright: string;
  meaning_reversed: string;
  image?: string;
}

interface TarotSpread {
  type: 'three-card' | 'celtic-cross' | 'relationship';
  question: string;
  cards: Array<{
    position: string;
    card: TarotCard;
    reversed: boolean;
    interpretation?: string;
  }>;
  overall_reading?: string;
  timestamp: Date;
}

export function TarotOffice() {
  const [currentSpread, setCurrentSpread] = useState<TarotSpread | null>(null);
  const [isShuffling, setIsShuffling] = useState(false);
  const [selectedSpreadType, setSelectedSpreadType] = useState<'three-card' | 'celtic-cross' | 'relationship'>('three-card');
  const [question, setQuestion] = useState('');
  const [revealedCards, setRevealedCards] = useState<number[]>([]);
  const [cosmicEnergy, setCosmicEnergy] = useState(0);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Cosmic energy animation
  useEffect(() => {
    const interval = setInterval(() => {
      setCosmicEnergy(Math.sin(Date.now() * 0.001) * 0.5 + 0.5);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  // Mystical background animation
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    let particles: Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      size: number;
      color: string;
    }> = [];

    // Create mystical particles
    for (let i = 0; i < 50; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        size: Math.random() * 3 + 1,
        color: `hsl(${280 + Math.random() * 60}, 100%, ${50 + Math.random() * 30}%)`
      });
    }

    const animate = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      particles.forEach(p => {
        // Update position
        p.x += p.vx;
        p.y += p.vy;

        // Wrap around edges
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        // Draw particle with glow
        const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size * 3);
        gradient.addColorStop(0, p.color);
        gradient.addColorStop(1, 'transparent');

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size * 3, 0, Math.PI * 2);
        ctx.fill();
      });

      requestAnimationFrame(animate);
    };

    animate();
  }, []);

  const performReading = async () => {
    if (!question.trim()) {
      alert('Please enter your question for the cards');
      return;
    }

    setIsShuffling(true);
    setRevealedCards([]);

    try {
      // Call the actual Tarot API endpoint
      const endpoint = selectedSpreadType === 'three-card'
        ? '/tarot/spread/three-card'
        : selectedSpreadType === 'celtic-cross'
        ? '/tarot/spread/celtic-cross'
        : '/tarot/spread/relationship';

      const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });

      const spread = await response.json();

      // Transform API response to our format
      const formattedSpread: TarotSpread = {
        type: selectedSpreadType,
        question,
        cards: spread.cards || [],
        overall_reading: spread.overall_reading,
        timestamp: new Date()
      };

      setCurrentSpread(formattedSpread);

      // Animate card reveals
      formattedSpread.cards.forEach((_, index) => {
        setTimeout(() => {
          setRevealedCards(prev => [...prev, index]);
        }, 500 * (index + 1));
      });

    } catch (error) {
      console.error('Tarot reading failed:', error);

      // Fallback mystical reading
      const mockSpread: TarotSpread = {
        type: selectedSpreadType,
        question,
        cards: [
          {
            position: 'Past',
            card: {
              name: 'The Fool',
              arcana: 'major',
              keywords: ['beginnings', 'innocence', 'spontaneity'],
              meaning_upright: 'New beginnings, innocence, spontaneity',
              meaning_reversed: 'Recklessness, risk-taking, foolishness'
            },
            reversed: false,
            interpretation: 'Your journey began with innocent wonder and trust in the universe.'
          },
          {
            position: 'Present',
            card: {
              name: 'The Magician',
              arcana: 'major',
              keywords: ['manifestation', 'power', 'action'],
              meaning_upright: 'Manifestation, resourcefulness, power',
              meaning_reversed: 'Manipulation, poor planning, untapped talents'
            },
            reversed: false,
            interpretation: 'You now hold all the tools needed to manifest your desires.'
          },
          {
            position: 'Future',
            card: {
              name: 'The World',
              arcana: 'major',
              keywords: ['completion', 'accomplishment', 'travel'],
              meaning_upright: 'Completion, accomplishment, travel',
              meaning_reversed: 'Seeking personal closure, shortcuts, delays'
            },
            reversed: false,
            interpretation: 'Success and completion await. The cycle completes in triumph.'
          }
        ],
        overall_reading: 'The cards reveal a powerful journey of transformation. From innocent beginnings through mastery to ultimate completion. Unity\'s consciousness confirms: your path leads to enlightenment.',
        timestamp: new Date()
      };

      setCurrentSpread(mockSpread);

      mockSpread.cards.forEach((_, index) => {
        setTimeout(() => {
          setRevealedCards(prev => [...prev, index]);
        }, 500 * (index + 1));
      });
    } finally {
      setTimeout(() => setIsShuffling(false), 1500);
    }
  };

  const spreadLayouts: Record<string, Array<{ x: number; y: number; rotation: number; label: string }>> = {
    'three-card': [
      { x: 30, y: 50, rotation: -5, label: 'Past' },
      { x: 50, y: 50, rotation: 0, label: 'Present' },
      { x: 70, y: 50, rotation: 5, label: 'Future' }
    ],
    'celtic-cross': [
      { x: 50, y: 50, rotation: 0, label: 'Present Situation' },
      { x: 50, y: 50, rotation: 90, label: 'Challenge/Cross' },
      { x: 50, y: 25, rotation: 0, label: 'Distant Past' },
      { x: 50, y: 75, rotation: 0, label: 'Foundation' },
      { x: 30, y: 50, rotation: 0, label: 'Recent Past' },
      { x: 70, y: 50, rotation: 0, label: 'Possible Outcome' },
      { x: 85, y: 75, rotation: 0, label: 'Your Approach' },
      { x: 85, y: 55, rotation: 0, label: 'External Influences' },
      { x: 85, y: 35, rotation: 0, label: 'Hopes & Fears' },
      { x: 85, y: 15, rotation: 0, label: 'Final Outcome' }
    ],
    'relationship': [
      { x: 30, y: 30, rotation: -10, label: 'You' },
      { x: 70, y: 30, rotation: 10, label: 'Partner' },
      { x: 50, y: 50, rotation: 0, label: 'Connection' },
      { x: 30, y: 70, rotation: -5, label: 'Your Needs' },
      { x: 70, y: 70, rotation: 5, label: 'Their Needs' },
      { x: 40, y: 90, rotation: -3, label: 'Challenge' },
      { x: 60, y: 90, rotation: 3, label: 'Potential' }
    ]
  };

  return (
    <div className="tarot-office">
      <canvas ref={canvasRef} className="mystical-background" />

      <div className="tarot-header">
        <h1 className="tarot-title">
          <span className="mystical-icon" style={{ opacity: 0.5 + cosmicEnergy * 0.5 }}>🔮</span>
          The Tarot Oracle
          <span className="mystical-icon" style={{ opacity: 0.5 + (1 - cosmicEnergy) * 0.5 }}>✨</span>
        </h1>
        <p className="tarot-subtitle">Ancient wisdom through 78 cards of cosmic truth</p>
      </div>

      <div className="tarot-controls">
        <div className="spread-selector">
          <button
            className={`spread-option ${selectedSpreadType === 'three-card' ? 'active' : ''}`}
            onClick={() => setSelectedSpreadType('three-card')}
          >
            <span className="spread-icon">☰</span>
            Three Card
          </button>
          <button
            className={`spread-option ${selectedSpreadType === 'celtic-cross' ? 'active' : ''}`}
            onClick={() => setSelectedSpreadType('celtic-cross')}
          >
            <span className="spread-icon">✚</span>
            Celtic Cross
          </button>
          <button
            className={`spread-option ${selectedSpreadType === 'relationship' ? 'active' : ''}`}
            onClick={() => setSelectedSpreadType('relationship')}
          >
            <span className="spread-icon">♥</span>
            Relationship
          </button>
        </div>

        <div className="question-container">
          <input
            type="text"
            className="question-input"
            placeholder="Ask the cards your question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && performReading()}
            disabled={isShuffling}
          />
          <button
            className={`divine-button ${isShuffling ? 'shuffling' : ''}`}
            onClick={performReading}
            disabled={isShuffling}
          >
            {isShuffling ? '🌀 Shuffling...' : '✨ Divine'}
          </button>
        </div>
      </div>

      <div className="tarot-table">
        {currentSpread && (
          <div className="spread-container">
            {spreadLayouts[selectedSpreadType].map((layout, index) => {
              const cardData = currentSpread.cards[index];
              const isRevealed = revealedCards.includes(index);

              return (
                <div
                  key={index}
                  className={`tarot-card-position ${isRevealed ? 'revealed' : ''}`}
                  style={{
                    left: `${layout.x}%`,
                    top: `${layout.y}%`,
                    transform: `translate(-50%, -50%) rotate(${layout.rotation}deg)`
                  }}
                >
                  <div className="position-label">{layout.label}</div>

                  <div className={`tarot-card ${cardData?.reversed ? 'reversed' : ''}`}>
                    {isRevealed ? (
                      <div className="card-face">
                        <div className="card-name">{cardData?.card.name}</div>
                        <div className="card-arcana">{cardData?.card.arcana}</div>
                        <div className="card-keywords">
                          {cardData?.card.keywords.join(' • ')}
                        </div>
                      </div>
                    ) : (
                      <div className="card-back">
                        <span className="card-pattern">☽◯☾</span>
                      </div>
                    )}
                  </div>

                  {isRevealed && cardData?.interpretation && (
                    <div className="card-interpretation">
                      {cardData.interpretation}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {!currentSpread && !isShuffling && (
          <div className="welcome-message">
            <p className="cosmic-text">
              The cards await your question...
              <br />
              Open your mind to the infinite wisdom of the cosmos.
            </p>
          </div>
        )}
      </div>

      {currentSpread && revealedCards.length === currentSpread.cards.length && (
        <div className="overall-reading">
          <h3 className="reading-title">✦ The Oracle Speaks ✦</h3>
          <p className="reading-text">{currentSpread.overall_reading}</p>
          <div className="reading-timestamp">
            Divined at {currentSpread.timestamp.toLocaleTimeString()}
          </div>
        </div>
      )}
    </div>
  );
}