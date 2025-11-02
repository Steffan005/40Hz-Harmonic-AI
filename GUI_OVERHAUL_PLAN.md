# Unity GUI — Complete Overhaul Plan
**Oracle/Google Level Sophistication with Quantum-Psychedelic Aesthetics**

**Date:** October 17, 2025
**Status:** PLANNING → IMPLEMENTATION
**Philosophy:** *"Every pixel matters. Sophistication meets psychedelia. Freedom meets beauty."*

---

## 🎯 Executive Summary

**Current State:**
- Basic functional GUI (Dashboard, Canvas, Controls, StatusBar, Console)
- No quantum aesthetics
- No main orchestrator chat
- No 43 offices integration
- Generic styling

**Target State:**
- **Oracle/Google sophistication** — Premium, intentional design
- **Quantum-psychedelic** — 40Hz breathing, fractal viz, parallax depth
- **Main Orchestrator** — Central AI chat interface
- **43 Offices** — Visual city with clickable districts/buildings
- **Multi-million dollar look** — Professional + innovative

---

## 📊 Current GUI Audit

### Files Structure
```
gui/src/
├── App.tsx                  # Entry point (minimal)
├── main.tsx                 # React bootstrap
├── pages/
│   └── Dashboard.tsx        # Main page (Controls + Canvas + Console + Telemetry)
├── components/
│   ├── StatusBar.tsx        # Top bar with metrics
│   ├── Controls.tsx         # Left sidebar buttons
│   └── Canvas.tsx           # Center canvas (basic)
└── lib/
    ├── api.ts               # Backend API calls
    └── preflight.ts         # System checks
```

### Components Analysis

#### ✅ **StatusBar** (Keep & Enhance)
- Shows: tokens/sec, cache hit, memory
- Good: Real-time telemetry
- Needs: Quantum breathing animation, better styling

#### ⚠️ **Controls** (Redesign)
- Shows: 6 buttons (Evaluate, Mutate, Bandit, Memory, Workflow, Dependencies)
- Issues: Generic buttons, no context, not connected to offices
- Needs: Replace with office launcher, add main chat

#### ⚠️ **Canvas** (Complete Overhaul)
- Shows: Basic DAG node count
- Issues: No fractals, no 40Hz breathing, no interactivity
- Needs: Fractal viz, graph rendering, quantum effects

#### ⚠️ **Console** (Keep & Style)
- Shows: Log messages
- Good: Functional
- Needs: Better styling, color coding, filtering

---

## 🌟 Design Principles

### 1. **Quantum-Psychedelic Aesthetics**

**40Hz Breathing Animation:**
```css
/* Gamma wave frequency for neural entrainment */
@keyframes breathe-40hz {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.02); opacity: 0.95; }
}

/* 40Hz = 25ms period */
.breathing-element {
  animation: breathe-40hz 25ms ease-in-out infinite;
}
```

**Fractal Backgrounds:**
- Mandelbrot/Julia sets with WebGL
- Slowly rotating and zooming
- Depth layers with parallax
- Color schemes: Purple/Blue/Orange (quantum vibes)

**Parallax Depth:**
- Layer 1 (Back): Fractal background (slow)
- Layer 2 (Mid): UI panels (medium)
- Layer 3 (Front): Active elements (fast)
- Mouse movement creates 3D depth

### 2. **Oracle/Google Sophistication**

**Typography:**
- Primary: Inter or SF Pro (clean, modern)
- Monospace: JetBrains Mono (code, metrics)
- Headings: 18-24px, 600 weight
- Body: 14-16px, 400 weight

**Color Palette:**
```
Background: #0A0E1A (deep space blue)
Surface: #1A1F2E (elevated panels)
Border: #2A3142 (subtle separation)
Primary: #9B59B6 (quantum purple)
Secondary: #3498DB (electric blue)
Accent: #FFA500 (consciousness orange)
Success: #00E676 (emerald green)
Warning: #FFC107 (amber)
Error: #FF5252 (red)
Text Primary: #FFFFFF
Text Secondary: #B0B8C4
```

**Spacing:**
- Base unit: 8px
- Margins: 16px, 24px, 32px
- Padding: 12px, 16px, 24px
- Border radius: 8px, 12px, 16px

**Elevation (Shadows):**
```css
/* Level 1: Cards */
box-shadow: 0 2px 8px rgba(0,0,0,0.3);

/* Level 2: Panels */
box-shadow: 0 4px 16px rgba(0,0,0,0.4);

/* Level 3: Modals */
box-shadow: 0 8px 32px rgba(0,0,0,0.5);

/* Glow effect for active elements */
box-shadow: 0 0 20px rgba(155, 89, 182, 0.6);
```

### 3. **Intentional Interactions**

**Button States:**
- Default: Subtle glow, clear affordance
- Hover: Brighten, scale(1.02), cursor pointer
- Active: Depress, scale(0.98), instant feedback
- Disabled: Opacity 0.5, no hover, cursor not-allowed

**Animations:**
- Transitions: 200ms ease-in-out (snappy)
- Hover: 150ms (immediate feedback)
- Panel open: 300ms cubic-bezier(0.4, 0, 0.2, 1)
- Never: Spinner loops (use progress indicators)

---

## 🏗️ New Architecture

### Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  Header (StatusBar + Logo + Quantum Heartbeat)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────────────────┐  ┌───────────┐ │
│  │              │  │                          │  │           │ │
│  │   Office     │  │    Main Canvas           │  │ Orchestr- │ │
│  │   Launcher   │  │    (Quantum City)        │  │   ator    │ │
│  │              │  │                          │  │   Chat    │ │
│  │  43 Offices  │  │  • Fractal Background    │  │           │ │
│  │  Organized   │  │  • 40Hz Breathing        │  │ "Talk to  │ │
│  │  by District │  │  • Memory Graph Viz      │  │  Unity"   │ │
│  │              │  │  • Office Nodes          │  │           │ │
│  │  [Mystical]  │  │  • Kernel Heartbeat      │  │           │ │
│  │  [Science]   │  │                          │  │           │ │
│  │  [Finance]   │  │                          │  │           │ │
│  │  [Art]       │  │                          │  │           │ │
│  │  [...]       │  │                          │  │           │ │
│  │              │  │                          │  │           │ │
│  └──────────────┘  └──────────────────────────┘  └───────────┘ │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  Console (Collapsible, Bottom Drawer)                           │
└─────────────────────────────────────────────────────────────────┘
```

### Component Hierarchy

```typescript
<App>
  <QuantumBackground />  // Fractal viz with 40Hz breathing
  <Header>
    <Logo />
    <QuantumHeartbeat />  // Kernel pulse visualization
    <StatusBar />
  </Header>

  <MainLayout>
    <OfficeLauncher>
      <DistrictGroup district="mystical">
        <OfficeCard office="tarot" />
        <OfficeCard office="astrology" />
        <OfficeCard office="numerology" />
        ...
      </DistrictGroup>
      <DistrictGroup district="science">
        ...
      </DistrictGroup>
      ...
    </OfficeLauncher>

    <QuantumCanvas>
      <MemoryGraphViz />
      <OfficeNodesViz />
      <KernelHeartbeat />
    </QuantumCanvas>

    <OrchestratorChat>
      <ChatHistory />
      <ChatInput />
      <StreamingResponse />
    </OrchestratorChat>
  </MainLayout>

  <ConsoleDrawer />
</App>
```

---

## 🎨 Implementation Roadmap

### Phase 1: Foundation (2-3 hours)

**1.1 Design System Setup**
- Create `src/styles/theme.ts` with color palette, typography, spacing
- Create `src/styles/animations.css` with 40Hz breathing, transitions
- Create `src/styles/global.css` with base resets, utilities

**1.2 Quantum Background**
- Create `src/components/QuantumBackground.tsx`
- Implement WebGL fractal rendering (Mandelbrot/Julia)
- Add 40Hz breathing animation
- Add parallax mouse tracking

**1.3 New Layout**
- Update `src/pages/Dashboard.tsx` with 3-column layout
- Add responsive breakpoints (desktop-first, mobile later)

### Phase 2: Core Components (3-4 hours)

**2.1 Office Launcher**
- Create `src/components/OfficeLauncher.tsx`
- Create `src/components/DistrictGroup.tsx`
- Create `src/components/OfficeCard.tsx`
- Load 43 offices from ontology
- Add search/filter functionality

**2.2 Orchestrator Chat**
- Create `src/components/OrchestratorChat.tsx`
- Create `src/components/ChatMessage.tsx`
- Implement streaming LLM responses (SSE)
- Add chat history persistence (localStorage)
- Add markdown rendering for code/formatting

**2.3 Enhanced Canvas**
- Update `src/components/Canvas.tsx`
- Add D3.js for memory graph visualization
- Add force-directed layout for office nodes
- Add click-to-focus interactions
- Add zoom/pan controls

### Phase 3: Quantum Effects (2-3 hours)

**3.1 Kernel Heartbeat Visualization**
- Create `src/components/QuantumHeartbeat.tsx`
- Pulse animation synced to `/kernel/stream`
- Show tick count, uptime, status

**3.2 40Hz Breathing**
- Apply to all major UI elements
- Synchronize with kernel heartbeat
- Add settings toggle (some users may find distracting)

**3.3 Fractal Details**
- Add color cycling based on system state
- Add zoom levels based on memory graph depth
- Add rotation based on time of day

### Phase 4: Polish (2-3 hours)

**4.1 Micro-Interactions**
- Button hover effects
- Panel open/close animations
- Toast notifications for actions
- Loading states (skeleton screens, not spinners)

**4.2 Accessibility**
- Keyboard navigation (Tab, Enter, Esc)
- ARIA labels for screen readers
- Focus indicators
- Color contrast ratios (WCAG AA minimum)

**4.3 Performance**
- Code splitting (React.lazy)
- Memoization (React.memo, useMemo)
- Virtual scrolling for office list
- WebGL optimizations for fractals

**4.4 Responsive**
- Mobile layout (stack vertically)
- Tablet layout (2-column)
- Touch interactions

---

## 🛠️ Technical Implementation

### 1. Quantum Background Component

```typescript
// src/components/QuantumBackground.tsx
import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export function QuantumBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Three.js setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    const renderer = new THREE.WebGLRenderer({
      canvas: canvasRef.current,
      alpha: true,
      antialias: true
    });

    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    // Create fractal geometry
    const geometry = new THREE.PlaneGeometry(20, 20, 128, 128);
    const material = new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        resolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
        colorShift: { value: 0 }
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform float time;
        uniform vec2 resolution;
        uniform float colorShift;
        varying vec2 vUv;

        // Mandelbrot set calculation
        vec3 mandelbrot(vec2 c, int maxIter) {
          vec2 z = vec2(0.0);
          float iter = 0.0;

          for (int i = 0; i < 100; i++) {
            if (length(z) > 2.0) break;
            z = vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;
            iter += 1.0;
          }

          float t = iter / float(maxIter);

          // Quantum color palette (purple, blue, orange)
          vec3 color = vec3(
            0.6 + 0.4 * cos(6.28 * (t + colorShift)),
            0.4 + 0.4 * cos(6.28 * (t + colorShift + 0.33)),
            0.3 + 0.4 * cos(6.28 * (t + colorShift + 0.67))
          );

          return color * (1.0 - t);
        }

        void main() {
          vec2 uv = vUv * 4.0 - 2.0;
          uv *= 1.0 + 0.1 * sin(time * 0.5);  // Slow zoom

          vec3 color = mandelbrot(uv, 100);

          // 40Hz breathing (25ms period = 40Hz)
          float breathe = 0.95 + 0.05 * sin(time * 251.327);  // 40Hz = 251.327 rad/s
          color *= breathe;

          gl_FragColor = vec4(color * 0.3, 0.5);  // Semi-transparent
        }
      `
    });

    const fractal = new THREE.Mesh(geometry, material);
    scene.add(fractal);

    camera.position.z = 5;

    // Animation loop
    let animationId: number;
    const animate = () => {
      animationId = requestAnimationFrame(animate);

      material.uniforms.time.value += 0.016;  // ~60fps
      material.uniforms.colorShift.value = Math.sin(Date.now() * 0.0001) * 0.5;

      renderer.render(scene, camera);
    };
    animate();

    // Cleanup
    return () => {
      cancelAnimationFrame(animationId);
      renderer.dispose();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        zIndex: -1,
        pointerEvents: 'none'
      }}
    />
  );
}
```

### 2. Orchestrator Chat Component

```typescript
// src/components/OrchestratorChat.tsx
import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export function OrchestratorChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Welcome to Unity. I am the Orchestrator. How can I help you today?',
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);

    // Add assistant message placeholder
    const assistantMessage: Message = {
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, assistantMessage]);

    try {
      // Stream response from backend
      const response = await fetch('http://127.0.0.1:8000/orchestrator/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          history: messages.slice(-10)  // Last 10 messages for context
        })
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('No reader available');

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        // Update last message with streamed content
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1].content += chunk;
          return updated;
        });
      }
    } catch (err) {
      console.error('Chat error:', err);
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1].content = 'Error: Could not reach orchestrator.';
        return updated;
      });
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="orchestrator-chat">
      <div className="chat-header">
        <div className="chat-title">Unity Orchestrator</div>
        <div className="chat-subtitle">Main AI Conductor</div>
      </div>

      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message message-${msg.role}`}>
            <div className="message-role">
              {msg.role === 'assistant' ? '🌌 Orchestrator' : '👤 You'}
            </div>
            <div className="message-content">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
            <div className="message-timestamp">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <textarea
          className="chat-input"
          placeholder="Talk to Unity..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          rows={3}
          disabled={isStreaming}
        />
        <button
          className="chat-send"
          onClick={handleSend}
          disabled={!input.trim() || isStreaming}
        >
          {isStreaming ? 'Streaming...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
```

### 3. Office Launcher Component

```typescript
// src/components/OfficeLauncher.tsx
import React, { useState, useEffect } from 'react';

interface Office {
  id: string;
  name: string;
  district: string;
  specialization: string;
  icon: string;
}

export function OfficeLauncher() {
  const [offices, setOffices] = useState<Office[]>([]);
  const [search, setSearch] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState<string | null>(null);

  useEffect(() => {
    // Load offices from ontology
    fetch('http://127.0.0.1:8000/ontology/offices')
      .then(res => res.json())
      .then(data => setOffices(data))
      .catch(err => console.error('Failed to load offices:', err));
  }, []);

  const districts = Array.from(new Set(offices.map(o => o.district)));

  const filteredOffices = offices.filter(office => {
    const matchesSearch = office.name.toLowerCase().includes(search.toLowerCase());
    const matchesDistrict = !selectedDistrict || office.district === selectedDistrict;
    return matchesSearch && matchesDistrict;
  });

  return (
    <div className="office-launcher">
      <div className="launcher-header">
        <div className="launcher-title">Offices</div>
        <div className="launcher-subtitle">{offices.length} Active</div>
      </div>

      <input
        className="launcher-search"
        type="text"
        placeholder="Search offices..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      <div className="district-filter">
        <button
          className={`district-button ${!selectedDistrict ? 'active' : ''}`}
          onClick={() => setSelectedDistrict(null)}
        >
          All
        </button>
        {districts.map(district => (
          <button
            key={district}
            className={`district-button ${selectedDistrict === district ? 'active' : ''}`}
            onClick={() => setSelectedDistrict(district)}
          >
            {district}
          </button>
        ))}
      </div>

      <div className="office-list">
        {filteredOffices.map(office => (
          <div key={office.id} className="office-card" onClick={() => {
            // Open office window or navigate
            console.log('Opening office:', office.id);
          }}>
            <div className="office-icon">{office.icon}</div>
            <div className="office-name">{office.name}</div>
            <div className="office-specialization">{office.specialization}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🎯 Success Criteria

### Visual Quality
- [ ] 40Hz breathing visible and synchronized
- [ ] Fractal background renders smoothly (60fps)
- [ ] All typography follows design system
- [ ] Color palette consistent throughout
- [ ] Shadows/elevation properly applied
- [ ] Animations smooth and intentional

### Functionality
- [ ] All 43 offices accessible from launcher
- [ ] Orchestrator chat streams responses
- [ ] Memory graph visualized in canvas
- [ ] Kernel heartbeat animates in real-time
- [ ] Console shows logs with color coding
- [ ] All buttons have clear purpose and work

### Sophistication
- [ ] Looks professional (could be Oracle/Google product)
- [ ] Every element has clear purpose
- [ ] No placeholder text or Lorem ipsum
- [ ] Loading states elegant (no spinners)
- [ ] Error states helpful and styled
- [ ] Responsive design (desktop + tablet + mobile)

---

## 📝 Next Steps

1. **Review this plan** — Confirm design direction
2. **Set up design system** — Colors, fonts, spacing
3. **Implement Quantum Background** — Fractal + 40Hz
4. **Build Orchestrator Chat** — Main interaction point
5. **Create Office Launcher** — Gateway to 43 offices
6. **Enhanced Canvas** — Memory graph + nodes
7. **Polish** — Micro-interactions, accessibility, performance

---

**Total Estimated Time:** 12-15 hours for complete overhaul

**Recommended Approach:** Iterate in phases, test each component, maintain high standards throughout

**Philosophy:** *"Perfect as we go. No technical debt. Every pixel intentional."*

---

**End of GUI Overhaul Plan**
