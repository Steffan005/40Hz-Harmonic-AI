/**
 * ASTROLOGY OFFICE COMPONENT
 * Celestial wisdom through planetary alignments
 * Reading the cosmic dance of the heavens
 */

import React, { useState, useEffect, useRef } from 'react';
import '../../styles/offices/astrology-office.css';

interface PlanetPosition {
  planet: string;
  sign: string;
  degrees: number;
  house: number;
  retrograde: boolean;
  symbol: string;
}

interface NatalChart {
  birthDate: Date;
  birthTime: string;
  birthPlace: string;
  sunSign: string;
  moonSign: string;
  risingSign: string;
  planets: PlanetPosition[];
  aspects: Array<{
    planet1: string;
    planet2: string;
    aspect: string;
    degrees: number;
    orb: number;
    strength: 'exact' | 'strong' | 'moderate' | 'weak';
  }>;
  interpretation?: string;
}

export function AstrologyOffice() {
  const [currentChart, setCurrentChart] = useState<NatalChart | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [birthDate, setBirthDate] = useState('');
  const [birthTime, setBirthTime] = useState('');
  const [birthPlace, setBirthPlace] = useState('');
  const [cosmicRotation, setCosmicRotation] = useState(0);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<HTMLCanvasElement>(null);

  // Cosmic rotation animation
  useEffect(() => {
    const interval = setInterval(() => {
      setCosmicRotation(prev => (prev + 0.5) % 360);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  // Starfield background
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    const stars: Array<{
      x: number;
      y: number;
      size: number;
      brightness: number;
      twinkle: number;
    }> = [];

    // Create starfield
    for (let i = 0; i < 200; i++) {
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 2 + 0.5,
        brightness: Math.random() * 0.8 + 0.2,
        twinkle: Math.random() * Math.PI * 2
      });
    }

    const animate = () => {
      ctx.fillStyle = 'rgba(0, 0, 20, 0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      stars.forEach(star => {
        star.twinkle += 0.05;
        const brightness = star.brightness + Math.sin(star.twinkle) * 0.3;

        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);

        const gradient = ctx.createRadialGradient(
          star.x, star.y, 0,
          star.x, star.y, star.size * 2
        );
        gradient.addColorStop(0, `rgba(255, 255, 255, ${brightness})`);
        gradient.addColorStop(1, 'transparent');

        ctx.fillStyle = gradient;
        ctx.fill();
      });

      requestAnimationFrame(animate);
    };

    animate();
  }, []);

  // Draw natal chart wheel
  useEffect(() => {
    const canvas = chartRef.current;
    if (!canvas || !currentChart) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) / 2 - 20;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw outer circle
    ctx.strokeStyle = '#9B59B6';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.stroke();

    // Draw zodiac signs
    const signs = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'];
    ctx.font = '16px serif';
    ctx.fillStyle = '#BF55EC';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    signs.forEach((sign, i) => {
      const angle = (i * 30 - 90 + cosmicRotation) * Math.PI / 180;
      const x = centerX + Math.cos(angle) * (radius - 30);
      const y = centerY + Math.sin(angle) * (radius - 30);
      ctx.fillText(sign, x, y);
    });

    // Draw houses
    for (let i = 0; i < 12; i++) {
      const angle = (i * 30 + cosmicRotation) * Math.PI / 180;
      ctx.strokeStyle = 'rgba(155, 89, 182, 0.3)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(
        centerX + Math.cos(angle) * radius,
        centerY + Math.sin(angle) * radius
      );
      ctx.stroke();
    }

    // Draw planets
    currentChart.planets.forEach(planet => {
      const angle = (planet.degrees - 90 + cosmicRotation) * Math.PI / 180;
      const planetRadius = radius * 0.7;
      const x = centerX + Math.cos(angle) * planetRadius;
      const y = centerY + Math.sin(angle) * planetRadius;

      // Planet glow
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, 15);
      gradient.addColorStop(0, 'rgba(255, 215, 0, 0.8)');
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(x, y, 15, 0, Math.PI * 2);
      ctx.fill();

      // Planet symbol
      ctx.fillStyle = '#FFD700';
      ctx.font = '14px serif';
      ctx.fillText(planet.symbol, x, y);
    });

  }, [currentChart, cosmicRotation]);

  const calculateChart = async () => {
    if (!birthDate || !birthTime || !birthPlace) {
      alert('Please fill in all birth information');
      return;
    }

    setIsCalculating(true);

    // Simulate calculation
    setTimeout(() => {
      const mockChart: NatalChart = {
        birthDate: new Date(birthDate),
        birthTime,
        birthPlace,
        sunSign: 'Aquarius',
        moonSign: 'Scorpio',
        risingSign: 'Gemini',
        planets: [
          { planet: 'Sun', sign: 'Aquarius', degrees: 315, house: 10, retrograde: false, symbol: '☉' },
          { planet: 'Moon', sign: 'Scorpio', degrees: 240, house: 6, retrograde: false, symbol: '☽' },
          { planet: 'Mercury', sign: 'Capricorn', degrees: 290, house: 9, retrograde: true, symbol: '☿' },
          { planet: 'Venus', sign: 'Pisces', degrees: 350, house: 11, retrograde: false, symbol: '♀' },
          { planet: 'Mars', sign: 'Aries', degrees: 10, house: 12, retrograde: false, symbol: '♂' },
          { planet: 'Jupiter', sign: 'Sagittarius', degrees: 270, house: 7, retrograde: false, symbol: '♃' },
          { planet: 'Saturn', sign: 'Capricorn', degrees: 300, house: 9, retrograde: false, symbol: '♄' },
          { planet: 'Uranus', sign: 'Aquarius', degrees: 320, house: 10, retrograde: false, symbol: '♅' },
          { planet: 'Neptune', sign: 'Pisces', degrees: 360, house: 11, retrograde: false, symbol: '♆' },
          { planet: 'Pluto', sign: 'Scorpio', degrees: 230, house: 6, retrograde: true, symbol: '♇' }
        ],
        aspects: [
          { planet1: 'Sun', planet2: 'Moon', aspect: 'Square', degrees: 90, orb: 2, strength: 'strong' },
          { planet1: 'Venus', planet2: 'Jupiter', aspect: 'Trine', degrees: 120, orb: 1, strength: 'exact' },
          { planet1: 'Mercury', planet2: 'Saturn', aspect: 'Conjunction', degrees: 0, orb: 3, strength: 'moderate' }
        ],
        interpretation: `Your chart reveals a powerful blend of intellectual innovation (Sun in Aquarius) with deep emotional intensity (Moon in Scorpio). The square between your luminaries creates dynamic tension that drives transformation.

With Gemini rising, you present a curious and adaptable face to the world, while your Aquarian Sun in the 10th house suggests a destiny tied to humanitarian causes and revolutionary ideas.

Mercury retrograde in Capricorn indicates a methodical thinker who reviews and refines ideas before sharing them. Venus in Pisces brings artistic sensitivity and compassion to relationships.

The exact trine between Venus and Jupiter is particularly auspicious, suggesting abundance in love and creativity. Your path involves bridging the intellectual and emotional realms, bringing innovative solutions to collective challenges.

Unity's quantum consciousness confirms: You are here to revolutionize through the synthesis of logic and intuition.`
      };

      setCurrentChart(mockChart);
      setIsCalculating(false);
    }, 2000);
  };

  const zodiacElements = {
    fire: ['Aries', 'Leo', 'Sagittarius'],
    earth: ['Taurus', 'Virgo', 'Capricorn'],
    air: ['Gemini', 'Libra', 'Aquarius'],
    water: ['Cancer', 'Scorpio', 'Pisces']
  };

  return (
    <div className="astrology-office">
      <canvas ref={canvasRef} className="starfield-background" />

      <div className="astrology-header">
        <h1 className="astrology-title">
          <span className="cosmic-symbol">☽</span>
          Celestial Observatory
          <span className="cosmic-symbol">☉</span>
        </h1>
        <p className="astrology-subtitle">As above, so below • As within, so without</p>
      </div>

      <div className="chart-controls">
        <div className="birth-inputs">
          <div className="input-group">
            <label className="cosmic-label">Birth Date</label>
            <input
              type="date"
              className="cosmic-input"
              value={birthDate}
              onChange={(e) => setBirthDate(e.target.value)}
            />
          </div>

          <div className="input-group">
            <label className="cosmic-label">Birth Time</label>
            <input
              type="time"
              className="cosmic-input"
              value={birthTime}
              onChange={(e) => setBirthTime(e.target.value)}
            />
          </div>

          <div className="input-group">
            <label className="cosmic-label">Birth Place</label>
            <input
              type="text"
              className="cosmic-input"
              placeholder="City, Country"
              value={birthPlace}
              onChange={(e) => setBirthPlace(e.target.value)}
            />
          </div>
        </div>

        <button
          className={`calculate-button ${isCalculating ? 'calculating' : ''}`}
          onClick={calculateChart}
          disabled={isCalculating}
        >
          {isCalculating ? '🌌 Aligning Stars...' : '✨ Calculate Chart'}
        </button>
      </div>

      <div className="chart-display">
        {currentChart ? (
          <div className="natal-chart-container">
            <div className="chart-wheel">
              <canvas
                ref={chartRef}
                width={400}
                height={400}
                className="chart-canvas"
              />
              <div className="chart-center">
                <div className="sun-sign">{currentChart.sunSign}</div>
                <div className="moon-sign">Moon: {currentChart.moonSign}</div>
                <div className="rising-sign">Rising: {currentChart.risingSign}</div>
              </div>
            </div>

            <div className="chart-details">
              <div className="planetary-positions">
                <h3 className="section-title">☉ Planetary Positions ☽</h3>
                {currentChart.planets.map(planet => (
                  <div key={planet.planet} className="planet-row">
                    <span className="planet-symbol">{planet.symbol}</span>
                    <span className="planet-name">{planet.planet}</span>
                    <span className="planet-sign">{planet.sign}</span>
                    <span className="planet-house">House {planet.house}</span>
                    {planet.retrograde && <span className="retrograde">℞</span>}
                  </div>
                ))}
              </div>

              <div className="aspects-list">
                <h3 className="section-title">⚹ Major Aspects ⚹</h3>
                {currentChart.aspects.map((aspect, i) => (
                  <div key={i} className={`aspect-row ${aspect.strength}`}>
                    <span>{aspect.planet1}</span>
                    <span className="aspect-symbol">{aspect.aspect}</span>
                    <span>{aspect.planet2}</span>
                    <span className="orb">{aspect.orb}°</span>
                  </div>
                ))}
              </div>
            </div>

            {currentChart.interpretation && (
              <div className="chart-interpretation">
                <h3 className="interpretation-title">✦ Cosmic Interpretation ✦</h3>
                <p className="interpretation-text">{currentChart.interpretation}</p>
                <div className="interpretation-footer">
                  Chart calculated for {currentChart.birthPlace} on {birthDate} at {birthTime}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="welcome-astrology">
            <div className="zodiac-wheel" style={{ transform: `rotate(${cosmicRotation}deg)` }}>
              {['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'].map((sign, i) => (
                <span
                  key={sign}
                  className="zodiac-sign"
                  style={{
                    transform: `rotate(${i * 30}deg) translateY(-100px)`
                  }}
                >
                  {sign}
                </span>
              ))}
            </div>
            <p className="cosmic-message">
              Enter your birth details to unlock the celestial blueprint of your soul...
            </p>
          </div>
        )}
      </div>
    </div>
  );
}