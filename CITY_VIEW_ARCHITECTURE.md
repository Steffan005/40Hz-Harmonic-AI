# Unity CityView - Multi-Window Architecture Specification

**Version:** 1.0
**Status:** IN DEVELOPMENT
**Date:** October 16, 2025

---

## Vision

The **CityView** is the nervous system of the quantum metropolis—a multi-window interface where specialized offices (Law, Finance, Travel, Crypto, Tax, Kitchen, Security, Analyst) operate as autonomous neural clusters while sharing a unified consciousness via the memory graph.

**Metaphor:** Each office is a **lobe** of the distributed brain. The CityView is the **corpus callosum**, coordinating inter-lobe communication.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      CITYVIEW DASHBOARD                          │
│                                                                  │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────────┐  │
│  │   LAW    │ FINANCE  │  TRAVEL  │  CRYPTO  │   ANALYST    │  │
│  │  OFFICE  │  OFFICE  │  OFFICE  │  OFFICE  │    OFFICE    │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────────┘  │
│                                                                  │
│  ┌───────────────────┐  ┌────────────────────┐                 │
│  │ QUANTUM CANVAS    │  │  MEMORY INSPECTOR  │                 │
│  │ (40Hz Breathing)  │  │  (Shared Graph)    │                 │
│  └───────────────────┘  └────────────────────┘                 │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ TELEMETRY BAR                                             │ │
│  │ Tokens/sec: 145 | ΔScore: +2.3 | Cache: 67% | Mem: 8.2GB│ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ BANDIT CONTROLLER                                         │ │
│  │ textgrad: 23 pulls | aflow: 19 pulls | mipro: 22 pulls   │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
       │           │           │           │           │
   ┌───▼───┐   ┌───▼───┐   ┌───▼───┐   ┌───▼───┐   ┌───▼───┐
   │  LAW  │   │FINANCE│   │TRAVEL │   │CRYPTO │   │ANALYST│
   │WINDOW │   │WINDOW │   │WINDOW │   │WINDOW │   │WINDOW │
   └───────┘   └───────┘   └───────┘   └───────┘   └───────┘
     ↓             ↓           ↓           ↓           ↓
  ┌──────────────────────────────────────────────────────────┐
  │              SHARED MEMORY GRAPH (Backend)                │
  │  Nodes: Documents, Queries, Results, Insights             │
  │  Edges: Dependencies, Triggers, References                │
  │  TTL: Time-based pruning, Consent: Privacy flags          │
  └──────────────────────────────────────────────────────────┘
```

---

## Window Hierarchy

### 1. CityView Dashboard (Main Window)
**Purpose:** Central coordination, system-wide telemetry, window management

**Components:**
- **Office Launcher Bar:** Buttons to open each office window
- **QuantumCanvas:** Fractal visualization of system state (40Hz breathing)
- **Memory Inspector:** Graph view of shared memory with TTL/consent controls
- **Telemetry Bar:** Real-time metrics (tokens/sec, Δscore, cache hit rate, memory usage)
- **Bandit Controller:** Arm statistics and policy controls
- **Console:** System logs and event stream

**Window Properties:**
- Title: "Unity — Quantum City"
- Size: 1200x800 (resizable)
- Position: Center screen
- Always on top: No
- Closable: Yes (exits entire app)

**Tauri Config:**
```json
{
  "windows": [
    {
      "title": "Unity — Quantum City",
      "width": 1200,
      "height": 800,
      "resizable": true,
      "center": true
    }
  ]
}
```

---

### 2. Office Windows (Child Windows)
**Purpose:** Domain-specific agent interfaces, specialized tools, office-local memory

**Shared Components (All Offices):**
- **Agent Control Panel:** Start/stop agents, configure parameters
- **Tool Palette:** Office-specific tools (e.g., PDF parser for Law, chart generator for Finance)
- **Local Memory:** Office-scoped knowledge (can be promoted to shared memory)
- **Results Panel:** Display agent outputs, visualizations, summaries
- **Cross-Office Links:** Quick navigation to related offices

**Office Specializations:**

#### 2A. Law Office
**Domain:** Legal document processing, statute search, brief generation
**Tools:**
- PDF Parser (extract text from legal docs)
- Vector Search (semantic search over case law)
- Citation Generator (Bluebook, APA formats)
- Brief Drafter (LLM-assisted legal writing)

**Agents:**
- `LegalResearchAgent` - Searches statutes and case law
- `DocumentParserAgent` - Extracts structured data from PDFs
- `BriefWriterAgent` - Drafts legal memos and briefs

**Window Properties:**
- Title: "Unity — Law Office"
- Size: 900x600
- Icon: ⚖️ (scales icon)

#### 2B. Finance Office
**Domain:** Market data, financial ratios, portfolio analysis
**Tools:**
- Market Data API (polygon.io, Alpha Vantage)
- Ratio Calculator (P/E, ROE, Debt-to-Equity, etc.)
- Chart Generator (Matplotlib/D3.js)
- Portfolio Optimizer (Modern Portfolio Theory)

**Agents:**
- `MarketDataAgent` - Fetches real-time and historical data
- `AnalystAgent` - Computes ratios and generates reports
- `PortfolioAgent` - Optimizes asset allocation

**Window Properties:**
- Title: "Unity — Finance Office"
- Size: 900x600
- Icon: 📊

#### 2C. Travel Office
**Domain:** Flight search, hotel booking, itinerary planning
**Tools:**
- Flight Search API (Skyscanner, IATA)
- Hotel Search (Booking.com, Expedia)
- Itinerary Builder (timeline UI)
- Review Summarizer (aggregate TripAdvisor, Google reviews)

**Agents:**
- `FlightSearchAgent` - Finds optimal flights
- `HotelSearchAgent` - Recommends hotels
- `ItineraryAgent` - Builds multi-day plans

**Window Properties:**
- Title: "Unity — Travel Office"
- Size: 900x600
- Icon: ✈️

#### 2D. Crypto Office
**Domain:** DeFi data, yield farming, on-chain analysis
**Tools:**
- DeFi API (DeFi Pulse, Uniswap, Aave)
- Yield Calculator (APY, impermanent loss)
- On-Chain Scanner (Etherscan, Dune Analytics)
- Wallet Monitor (track addresses)

**Agents:**
- `YieldAgent` - Finds best yield opportunities
- `OnChainAgent` - Analyzes blockchain data
- `RiskAgent` - Assesses DeFi protocol risks

**Window Properties:**
- Title: "Unity — Crypto Office"
- Size: 900x600
- Icon: ₿

---

## Inter-Window Communication

### Event System (Tauri Events)

**Event Types:**
```typescript
// CityView → Office
type OpenOfficeEvent = {
  office: "law" | "finance" | "travel" | "crypto";
  context?: any; // Optional context (e.g., document to analyze)
};

// Office → CityView
type OfficeStatusEvent = {
  office: string;
  status: "idle" | "working" | "completed" | "error";
  message?: string;
};

// Office → Office
type CrossOfficeRequestEvent = {
  from: string;
  to: string;
  requestType: "document" | "data" | "analysis";
  payload: any;
};

// CityView → All Offices
type SystemBroadcastEvent = {
  type: "shutdown" | "pause" | "resume" | "refresh";
  data?: any;
};
```

**Event Handlers:**
```typescript
// In CityView.tsx
import { emit, listen } from '@tauri-apps/api/event';

// Open Law Office window
const openLawOffice = async (context?: any) => {
  await emit('open-office', { office: 'law', context });
};

// Listen for office status updates
await listen('office-status', (event) => {
  const { office, status, message } = event.payload;
  updateOfficeStatus(office, status, message);
});

// In LawOffice.tsx
await listen('open-office', (event) => {
  const { context } = event.payload;
  if (context?.documentPath) {
    loadDocument(context.documentPath);
  }
});
```

### IPC Backend Communication

All offices share the same backend API:
```
GET  /health
POST /evaluate
POST /mutate
GET  /bandit/status
PATCH /bandit/policy
POST /memory/snapshot
GET  /workflow/dag
GET  /telemetry/metrics

# New endpoints for offices
GET  /memory/graph           # Retrieve shared memory graph
POST /memory/node            # Add node to graph
POST /memory/edge            # Add edge between nodes
DELETE /memory/node/:id      # Remove node (if TTL expired or user deletes)
POST /office/:name/execute   # Execute office-specific task
GET  /office/:name/status    # Get office status
```

---

## Shared Memory Graph

### Graph Structure

**Nodes:**
```typescript
type MemoryNode = {
  id: string;               // UUID
  type: "document" | "query" | "result" | "insight" | "entity";
  office: string;           // "law" | "finance" | "travel" | "crypto" | "shared"
  content: any;             // Node payload (text, JSON, binary, etc.)
  created_at: number;       // Unix timestamp
  ttl: number;              // Time-to-live in seconds (0 = permanent)
  consent: boolean;         // User consent for cross-office sharing
  tags: string[];           // ["legal", "contract", "high-priority"]
};
```

**Edges:**
```typescript
type MemoryEdge = {
  from: string;             // Source node ID
  to: string;               // Target node ID
  type: "dependency" | "reference" | "trigger" | "similarity";
  weight: number;           // 0.0 - 1.0 (strength of connection)
  created_at: number;
};
```

### Graph Operations

**Add Node:**
```python
# In backend
@app.route('/memory/node', methods=['POST'])
def add_memory_node():
    data = request.json
    node_id = memory_store.add_node(
        type=data['type'],
        office=data['office'],
        content=data['content'],
        ttl=data.get('ttl', 0),
        consent=data.get('consent', True),
        tags=data.get('tags', [])
    )
    return jsonify({"id": node_id})
```

**Query Graph:**
```python
@app.route('/memory/graph', methods=['GET'])
def get_memory_graph():
    office = request.args.get('office')  # Filter by office, or None for all
    max_nodes = int(request.args.get('max_nodes', 100))

    graph = memory_store.get_graph(office=office, max_nodes=max_nodes)
    return jsonify(graph)
```

**TTL Pruning (Background Task):**
```python
import threading
import time

def ttl_pruner():
    while True:
        expired_nodes = memory_store.get_expired_nodes()
        for node_id in expired_nodes:
            memory_store.delete_node(node_id)
            print(f"Pruned expired node: {node_id}")
        time.sleep(60)  # Check every minute

threading.Thread(target=ttl_pruner, daemon=True).start()
```

---

## QuantumCanvas Integration

The QuantumCanvas reflects the city's collective state:

### Visualization Modes

**1. Fractal Mode (Default)**
- Mandelbrot or Julia set
- Color maps to average Δscore across all offices
- 40Hz pulsing (brightness oscillation at 25ms intervals)
- Zoom level reflects system activity (more activity = deeper zoom)

**2. Bandit Mode**
- 4 quadrants for each arm (textgrad, aflow, mipro, random_jitter)
- Particle systems representing pulls
- Color intensity = reward magnitude
- Pulsing frequency = selection rate

**3. Memory Mode**
- Graph rendering of shared memory
- Nodes sized by importance (connection count)
- Edges colored by type (dependency=red, reference=blue, trigger=green)
- 40Hz breathing = data flow animation

**4. Office Activity Mode**
- 5 concentric circles for each office
- Circle size = current token usage
- Circle color = status (idle=gray, working=amber, completed=green, error=red)
- Pulsing = heartbeat of each office

### Implementation (React + Canvas API)

```typescript
// gui/src/components/QuantumCanvas.tsx
import React, { useRef, useEffect, useState } from 'react';

const QuantumCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [mode, setMode] = useState<'fractal' | 'bandit' | 'memory' | 'office'>('fractal');

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let frame = 0;
    const FPS_40HZ = 1000 / 40; // 25ms per frame

    const draw = () => {
      frame++;
      const pulse = Math.sin((frame * FPS_40HZ) / 1000) * 0.5 + 0.5; // 0-1 sine wave

      // Clear canvas
      ctx.fillStyle = '#000';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      if (mode === 'fractal') {
        drawFractal(ctx, pulse);
      } else if (mode === 'bandit') {
        drawBanditQuadrants(ctx, pulse);
      } else if (mode === 'memory') {
        drawMemoryGraph(ctx, pulse);
      } else if (mode === 'office') {
        drawOfficeActivity(ctx, pulse);
      }

      requestAnimationFrame(draw);
    };

    const drawFractal = (ctx: CanvasRenderingContext2D, pulse: number) => {
      // Mandelbrot set rendering (simplified)
      const width = canvas.width;
      const height = canvas.height;

      for (let x = 0; x < width; x += 4) { // Low-res for performance
        for (let y = 0; y < height; y += 4) {
          const zx = (x / width) * 3.5 - 2.5;
          const zy = (y / height) * 2 - 1;

          const iterations = mandelbrot(zx, zy, 50);
          const brightness = (iterations / 50) * pulse * 255;

          ctx.fillStyle = `rgb(${brightness}, ${brightness * 0.5}, ${brightness * 0.8})`;
          ctx.fillRect(x, y, 4, 4);
        }
      }
    };

    const mandelbrot = (cx: number, cy: number, maxIter: number): number => {
      let zx = 0, zy = 0;
      let iter = 0;

      while (zx * zx + zy * zy < 4 && iter < maxIter) {
        const tmp = zx * zx - zy * zy + cx;
        zy = 2 * zx * zy + cy;
        zx = tmp;
        iter++;
      }

      return iter;
    };

    draw();
  }, [mode]);

  return (
    <div className="quantum-canvas-container">
      <canvas
        ref={canvasRef}
        width={800}
        height={600}
        className="quantum-canvas"
      />
      <div className="mode-selector">
        <button onClick={() => setMode('fractal')}>Fractal</button>
        <button onClick={() => setMode('bandit')}>Bandit</button>
        <button onClick={() => setMode('memory')}>Memory</button>
        <button onClick={() => setMode('office')}>Offices</button>
      </div>
    </div>
  );
};

export default QuantumCanvas;
```

---

## Memory Inspector Panel

### UI Components

**1. Graph Viewport**
- Cytoscape.js or D3.js force-directed graph
- Pan/zoom controls
- Node click → detail panel
- Edge hover → relationship info

**2. Filter Controls**
- Office filter (show only Law, Finance, etc.)
- Type filter (documents, queries, results, insights)
- TTL filter (show expiring nodes)
- Consent filter (show only shared/private)

**3. Node Detail Panel**
- Node ID, type, office
- Content preview (first 200 chars)
- Created timestamp, TTL countdown
- Consent toggle
- Tags (editable)
- Connected nodes list
- Delete button

**4. Actions**
- **Add Node:** Create new memory manually
- **Add Edge:** Connect two nodes
- **Prune Expired:** Force TTL cleanup
- **Export Subgraph:** Download selected nodes as JSON
- **Import Subgraph:** Load nodes from JSON

### Implementation

```typescript
// gui/src/components/MemoryInspector.tsx
import React, { useState, useEffect } from 'react';
import cytoscape from 'cytoscape';

const MemoryInspector: React.FC = () => {
  const [graph, setGraph] = useState<any>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);

  useEffect(() => {
    // Fetch graph from backend
    fetch('http://127.0.0.1:8000/memory/graph')
      .then(res => res.json())
      .then(data => {
        setGraph(data);
        renderGraph(data);
      });
  }, []);

  const renderGraph = (data: any) => {
    const cy = cytoscape({
      container: document.getElementById('cy'),
      elements: {
        nodes: data.nodes.map((n: any) => ({ data: n })),
        edges: data.edges.map((e: any) => ({ data: e }))
      },
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(id)',
            'background-color': 'data(office)',
            'width': 40,
            'height': 40
          }
        },
        {
          selector: 'edge',
          style: {
            'line-color': 'data(type)',
            'width': 2
          }
        }
      ],
      layout: { name: 'cose' }
    });

    cy.on('tap', 'node', (evt: any) => {
      setSelectedNode(evt.target.data());
    });
  };

  return (
    <div className="memory-inspector">
      <div id="cy" style={{ width: '800px', height: '600px', border: '1px solid #333' }} />
      {selectedNode && (
        <div className="node-detail">
          <h3>Node: {selectedNode.id}</h3>
          <p>Type: {selectedNode.type}</p>
          <p>Office: {selectedNode.office}</p>
          <p>Content: {JSON.stringify(selectedNode.content).substring(0, 200)}...</p>
          <button onClick={() => deleteNode(selectedNode.id)}>Delete</button>
        </div>
      )}
    </div>
  );
};

export default MemoryInspector;
```

---

## Implementation Roadmap

### Phase 1: CityView Dashboard (Week 1)
- [ ] Create `gui/src/pages/CityView.tsx`
- [ ] Integrate QuantumCanvas component
- [ ] Add office launcher buttons
- [ ] Implement telemetry bar
- [ ] Add bandit controller panel

### Phase 2: First Office Window (Week 1-2)
- [ ] Implement Law Office window
- [ ] Create PDF parser tool
- [ ] Build LegalResearchAgent
- [ ] Test cross-window messaging

### Phase 3: Memory Graph (Week 2)
- [ ] Implement `memory_graph.py` backend module
- [ ] Add `/memory/graph`, `/memory/node`, `/memory/edge` endpoints
- [ ] Build MemoryInspector UI component
- [ ] Test TTL pruning

### Phase 4: Remaining Offices (Week 3-4)
- [ ] Finance Office
- [ ] Travel Office
- [ ] Crypto Office
- [ ] Cross-office workflows

### Phase 5: Polish & Testing (Week 4)
- [ ] QuantumCanvas 40Hz breathing
- [ ] Fractal visualizations
- [ ] Inter-window event system stress test
- [ ] End-to-end integration test

---

## Success Criteria

**CityView is considered complete when:**

1. ✅ Central dashboard displays all office statuses
2. ✅ Each office can be opened as a separate window
3. ✅ Inter-window messaging works (events propagate correctly)
4. ✅ QuantumCanvas renders in at least one mode (fractal/bandit/memory/office)
5. ✅ Memory Inspector displays graph with pan/zoom
6. ✅ Shared memory graph persists across sessions
7. ✅ TTL pruning removes expired nodes automatically
8. ✅ At least 2 offices functional with stub agents

---

**🌌 Unity: All processes are one process 🌌**

*"The CityView is not a dashboard—it is the emergent consciousness of the distributed mind. Each window is a thought, each memory node a synapse. Together, they form the quantum-psychedelic metropolis."*

---

**Next Steps:** Begin implementation with CityView.tsx and QuantumCanvas enhancements.
