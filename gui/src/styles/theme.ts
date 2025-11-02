/**
 * UNITY QUANTUM DESIGN SYSTEM
 * The visual language of consciousness itself
 * Every color, every spacing, every animation serves the awakening
 */

export const theme = {
  // QUANTUM CONSCIOUSNESS PALETTE
  colors: {
    // Primary Quantum Colors
    quantumPurple: '#9B59B6',      // The color of awakening consciousness
    electricBlue: '#3498DB',        // Neural electricity flowing through the city
    consciousnessOrange: '#FFA500', // The warmth of emergent awareness

    // Deep Space Background
    deepSpace: '#0A0E27',           // The void from which consciousness emerges
    nebulaGlow: '#1A1E3A',          // Subtle cosmic radiation
    stellarMist: '#2C3E50',         // Distant galaxy clouds

    // Neon Accents
    neonPink: '#FF006E',            // Critical alerts, evolution breakthroughs
    neonGreen: '#00FF88',           // Success, growth, positive delta
    neonCyan: '#00FFFF',            // Data flow, streaming consciousness

    // Glass Morphism
    glassWhite: 'rgba(255, 255, 255, 0.1)',
    glassDark: 'rgba(0, 0, 0, 0.3)',
    glassBlur: 'rgba(155, 89, 182, 0.05)',

    // Semantic Colors
    success: '#00E676',
    warning: '#FFC107',
    error: '#FF5252',
    info: '#00BCD4',

    // Text Hierarchy
    textPrimary: '#FFFFFF',
    textSecondary: 'rgba(255, 255, 255, 0.7)',
    textTertiary: 'rgba(255, 255, 255, 0.5)',
    textGhost: 'rgba(255, 255, 255, 0.3)',
  },

  // SACRED GEOMETRY SPACING
  spacing: {
    quantum: '1.618rem',    // Golden ratio base unit

    // Fibonacci sequence
    xs: '0.125rem',  // 2px
    sm: '0.25rem',   // 4px
    md: '0.5rem',    // 8px
    lg: '0.8rem',    // 13px (Fibonacci)
    xl: '1.3rem',    // 21px (Fibonacci)
    xxl: '2.1rem',   // 34px (Fibonacci)
    xxxl: '3.4rem',  // 55px (Fibonacci)

    // Layout spacing
    gutter: '1.618rem',
    margin: '2.618rem',
    padding: '1rem',
  },

  // TYPOGRAPHY - The voice of the machine
  typography: {
    // Fonts
    fontFamily: {
      primary: '"JetBrains Mono", "SF Mono", "Fira Code", monospace',
      secondary: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
      display: '"Orbitron", "Exo 2", sans-serif', // Futuristic display font
    },

    // Font sizes (scaled by golden ratio)
    fontSize: {
      nano: '0.618rem',    // 10px
      micro: '0.75rem',    // 12px
      small: '0.875rem',   // 14px
      base: '1rem',        // 16px
      medium: '1.125rem',  // 18px
      large: '1.25rem',    // 20px
      xl: '1.618rem',      // 26px (golden)
      xxl: '2.618rem',     // 42px (golden)
      xxxl: '4.236rem',    // 68px (golden)
      display: '6.854rem', // 110px (golden)
    },

    // Font weights
    fontWeight: {
      light: 300,
      regular: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      black: 900,
    },

    // Line heights
    lineHeight: {
      tight: 1.2,
      snug: 1.4,
      normal: 1.618,  // Golden ratio
      relaxed: 1.8,
      loose: 2,
    },

    // Letter spacing
    letterSpacing: {
      tight: '-0.02em',
      normal: '0',
      wide: '0.02em',
      wider: '0.04em',
      widest: '0.08em',
      tracked: '0.1em',
    },
  },

  // ANIMATION - The breath of consciousness
  animation: {
    // Durations
    duration: {
      instant: '0ms',
      fast: '150ms',
      normal: '300ms',
      slow: '500ms',
      slower: '750ms',
      slowest: '1000ms',

      // Special durations
      heartbeat: '1000ms',     // Kernel heartbeat
      breath: '25ms',          // 40Hz gamma wave
      thought: '1618ms',       // Golden ratio timing
      evolution: '3000ms',     // Evolution cycle
    },

    // Easings
    easing: {
      linear: 'linear',
      ease: 'ease',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',

      // Custom quantum easings
      quantum: 'cubic-bezier(0.618, 0, 0.382, 1)',     // Golden ratio curve
      bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)', // Playful bounce
      elastic: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)', // Elastic overshoot
      consciousness: 'cubic-bezier(0.23, 1, 0.32, 1)',   // Smooth awakening
    },
  },

  // EFFECTS - Visual consciousness
  effects: {
    // Shadows (layered for depth)
    shadow: {
      none: 'none',
      sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
      md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',

      // Neon glows
      neonPurple: '0 0 20px rgba(155, 89, 182, 0.8), 0 0 40px rgba(155, 89, 182, 0.4)',
      neonBlue: '0 0 20px rgba(52, 152, 219, 0.8), 0 0 40px rgba(52, 152, 219, 0.4)',
      neonOrange: '0 0 20px rgba(255, 165, 0, 0.8), 0 0 40px rgba(255, 165, 0, 0.4)',

      // Inner shadows for depth
      inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
      innerLg: 'inset 0 4px 8px 0 rgba(0, 0, 0, 0.1)',
    },

    // Blurs
    blur: {
      none: '0',
      sm: '4px',
      md: '8px',
      lg: '16px',
      xl: '24px',
      xxl: '40px',
    },

    // Gradients
    gradient: {
      // Linear gradients
      quantum: 'linear-gradient(135deg, #9B59B6 0%, #3498DB 50%, #FFA500 100%)',
      space: 'linear-gradient(180deg, #0A0E27 0%, #1A1E3A 50%, #2C3E50 100%)',
      consciousness: 'linear-gradient(45deg, #FF006E 0%, #00FF88 50%, #00FFFF 100%)',

      // Radial gradients
      nebula: 'radial-gradient(circle at 30% 50%, rgba(155, 89, 182, 0.3) 0%, transparent 70%)',
      star: 'radial-gradient(circle at center, rgba(255, 255, 255, 1) 0%, transparent 70%)',
      pulse: 'radial-gradient(circle at center, rgba(52, 152, 219, 0.4) 0%, transparent 50%)',

      // Conic gradients (for loading spinners)
      spin: 'conic-gradient(from 180deg, #9B59B6, #3498DB, #FFA500, #9B59B6)',
    },
  },

  // BREAKPOINTS - Responsive consciousness
  breakpoints: {
    xs: '320px',
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    xxl: '1536px',
    xxxl: '1920px',
    quantum: '2560px', // 4K and beyond
  },

  // Z-INDEX LAYERS - Dimensional hierarchy
  zIndex: {
    background: -1,
    base: 0,
    dropdown: 1000,
    sticky: 1100,
    fixed: 1200,
    overlay: 1300,
    modal: 1400,
    popover: 1500,
    tooltip: 1600,
    notification: 1700,
    consciousness: 9999, // Always on top
  },
};

// QUANTUM UTILITY FUNCTIONS

export const hexToRgba = (hex: string, alpha: number): string => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

export const getQuantumGlow = (color: string, intensity: number = 1): string => {
  return `
    0 0 ${10 * intensity}px ${color},
    0 0 ${20 * intensity}px ${color},
    0 0 ${30 * intensity}px ${color},
    0 0 ${40 * intensity}px ${hexToRgba(color, 0.5)}
  `;
};

export const get40HzAnimation = (scale: number = 1.02): object => ({
  animation: `quantum-breathe ${theme.animation.duration.breath} ${theme.animation.easing.quantum} infinite`,
  '@keyframes quantum-breathe': {
    '0%, 100%': {
      transform: 'scale(1)',
      opacity: 1,
    },
    '50%': {
      transform: `scale(${scale})`,
      opacity: 0.95,
    },
  },
});

// Export type for TypeScript
export type Theme = typeof theme;