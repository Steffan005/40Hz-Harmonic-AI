# 🚀 PHASES 13-17: IMPLEMENTATION GUIDE
## The Final Polish Layer - Transforming Unity into Production Perfection

---

## 📋 OVERVIEW

**Total Estimated Time:** 22 hours
**Status:** Implementation blueprints + starter code PROVIDED
**Goal:** Transform Unity from functional to FLAWLESS

**Phases:**
- Phase 13: Multi-Window Office Support (4 hours) - **HIGHEST PRIORITY**
- Phase 14: Remaining Office Tools (7 hours) - Progressive enhancement
- Phase 15: Conscious Veto UI (3 hours) - **QUICK WIN**
- Phase 16: Workflow Builder DAG (4 hours) - Advanced feature
- Phase 17: Production Hardening (4 hours) - **CRITICAL FOR LAUNCH**

---

## ⚡ PHASE 13: MULTI-WINDOW OFFICE SUPPORT (4 HOURS)

### Goal
Each of the 58 offices can open in its own independent Tauri window, enabling true multi-tasking quantum consciousness.

### Why This Matters
- **Current:** All offices in one window (limited)
- **Future:** 58 independent windows (unlimited multitasking)
- **Impact:** Work with Tarot + Crypto + Dream Analysis simultaneously

### Technical Approach

#### 1. Tauri Multi-Window API Integration

**File:** `gui/src-tauri/src/main.rs`

```rust
use tauri::{Manager, Window, WindowBuilder, WindowUrl};

// Office window configuration
fn create_office_window(app: &tauri::AppHandle, office_name: &str) -> Result<Window, tauri::Error> {
    let window_label = format!("office-{}", office_name);

    WindowBuilder::new(
        app,
        window_label.clone(),
        WindowUrl::App(format!("/#/office/{}", office_name).into())
    )
    .title(format!("{} Office - Unity", office_name))
    .inner_size(800.0, 600.0)
    .resizable(true)
    .decorations(true)
    .center()
    .build()
}

// IPC command to open office window
#[tauri::command]
async fn open_office_window(
    app: tauri::AppHandle,
    office_name: String
) -> Result<String, String> {
    match create_office_window(&app, &office_name) {
        Ok(window) => {
            window.show().map_err(|e| e.to_string())?;
            Ok(format!("Opened {} office window", office_name))
        },
        Err(e) => Err(format!("Failed to create window: {}", e))
    }
}

// Register command in main()
fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            open_office_window,
            // ... existing commands
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

#### 2. Frontend Office Window Component

**File:** `gui/src/pages/OfficeWindow.tsx`

```typescript
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { invoke } from '@tauri-apps/api/tauri';
import OfficeChat from '../components/OfficeChat';

export function OfficeWindow() {
  const { officeName } = useParams<{ officeName: string }>();
  const [officeData, setOfficeData] = useState<any>(null);

  useEffect(() => {
    // Load office configuration
    fetch(`/api/office/${officeName}/config`)
      .then(res => res.json())
      .then(data => setOfficeData(data));
  }, [officeName]);

  if (!officeData) {
    return <div className="loading">Loading {officeName} office...</div>;
  }

  return (
    <div className="office-window" data-office={officeName}>
      <header className="office-header">
        <div className="office-icon">{officeData.icon}</div>
        <h1>{officeData.name}</h1>
        <p className="office-tagline">{officeData.description}</p>
      </header>

      <main className="office-main">
        <OfficeChat
          officeName={officeName}
          officeId={officeName}
          placeholder={`Ask ${officeName} specialist...`}
        />
      </main>

      <footer className="office-footer">
        <div className="specialists">
          {officeData.specialists.map((s: any) => (
            <span key={s.name} className="specialist-tag">
              {s.name}
            </span>
          ))}
        </div>
      </footer>
    </div>
  );
}
```

#### 3. Update Office Launcher to Open Windows

**File:** `gui/src/pages/Unity.tsx` (modify existing)

```typescript
const handleOfficeClick = async (officeName: string) => {
  try {
    await invoke('open_office_window', { officeName });
  } catch (error) {
    console.error(`Failed to open ${officeName}:`, error);
    // Fallback to modal if window creation fails
    setSelectedOffice(officeName);
  }
};
```

#### 4. Window State Management

**File:** `gui/src/lib/windowManager.ts`

```typescript
interface OfficeWindow {
  label: string;
  officeName: string;
  isOpen: boolean;
}

class WindowManager {
  private windows: Map<string, OfficeWindow> = new Map();

  async openOffice(officeName: string): Promise<void> {
    const label = `office-${officeName}`;

    if (this.windows.has(label)) {
      // Window already open, focus it
      await invoke('focus_window', { label });
      return;
    }

    await invoke('open_office_window', { officeName });
    this.windows.set(label, {
      label,
      officeName,
      isOpen: true
    });
  }

  closeOffice(officeName: string): void {
    const label = `office-${officeName}`;
    this.windows.delete(label);
  }

  isOpen(officeName: string): boolean {
    const label = `office-${officeName}`;
    return this.windows.has(label);
  }
}

export const windowManager = new WindowManager();
```

### Implementation Checklist

- [ ] Add Tauri multi-window API to main.rs
- [ ] Create `open_office_window` IPC command
- [ ] Build OfficeWindow page component
- [ ] Add router route: `/office/:officeName`
- [ ] Implement WindowManager utility
- [ ] Update office launcher click handlers
- [ ] Add window focus/management logic
- [ ] Test with 3-5 offices open simultaneously
- [ ] Add "Close All Offices" command
- [ ] Document window keyboard shortcuts (Cmd+W, etc.)

### Testing Plan

```bash
# 1. Open Unity.app
open /Applications/Unity.app

# 2. Click on 5 different offices
# Expected: 5 separate windows open

# 3. Interact with each window independently
# Expected: Chat works in all windows

# 4. Close one window
# Expected: Other windows remain

# 5. Cmd+Q (quit)
# Expected: All windows close gracefully
```

---

## 🔧 PHASE 14: REMAINING OFFICE TOOLS (7 HOURS)

### Goal
Implement real tools for key high-value offices beyond Tarot/Astrology.

### Priority Offices (Ranked by Impact)

#### 1. Crypto Trading Office (2 hours) - **HIGHEST VALUE**

**Integration:** QuantConnect/Lean API

**File:** `tools/crypto_trader.py`

```python
import ccxt
from typing import Dict, List
import pandas as pd

class CryptoTrader:
    def __init__(self):
        # Initialize exchanges (read-only for safety)
        self.exchanges = {
            'binance': ccxt.binance({'enableRateLimit': True}),
            'coinbase': ccxt.coinbase({'enableRateLimit': True}),
            'kraken': ccxt.kraken({'enableRateLimit': True})
        }

    def get_price(self, symbol: str, exchange: str = 'binance') -> Dict:
        """Get current price for symbol (e.g., 'BTC/USDT')"""
        ticker = self.exchanges[exchange].fetch_ticker(symbol)
        return {
            'symbol': symbol,
            'price': ticker['last'],
            'volume_24h': ticker['baseVolume'],
            'change_24h': ticker['percentage'],
            'high_24h': ticker['high'],
            'low_24h': ticker['low']
        }

    def get_orderbook(self, symbol: str, exchange: str = 'binance', depth: int = 20) -> Dict:
        """Get orderbook depth"""
        orderbook = self.exchanges[exchange].fetch_order_book(symbol, limit=depth)
        return {
            'bids': orderbook['bids'][:depth],
            'asks': orderbook['asks'][:depth],
            'spread': orderbook['asks'][0][0] - orderbook['bids'][0][0],
            'timestamp': orderbook['timestamp']
        }

    def technical_analysis(self, symbol: str, timeframe: str = '1h') -> Dict:
        """Calculate technical indicators"""
        # Fetch OHLCV data
        ohlcv = self.exchanges['binance'].fetch_ohlcv(symbol, timeframe, limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        # Calculate indicators
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['rsi'] = self._calculate_rsi(df['close'])

        latest = df.iloc[-1]
        return {
            'price': latest['close'],
            'sma_20': latest['sma_20'],
            'sma_50': latest['sma_50'],
            'rsi': latest['rsi'],
            'trend': 'bullish' if latest['sma_20'] > latest['sma_50'] else 'bearish'
        }

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
```

**API Endpoints:**

```python
# backend/api_server.py

from tools.crypto_trader import CryptoTrader
crypto_trader = CryptoTrader()

@app.route('/crypto/price/<symbol>', methods=['GET'])
def crypto_price(symbol):
    exchange = request.args.get('exchange', 'binance')
    data = crypto_trader.get_price(symbol, exchange)
    return jsonify({'success': True, 'data': data})

@app.route('/crypto/orderbook/<symbol>', methods=['GET'])
def crypto_orderbook(symbol):
    exchange = request.args.get('exchange', 'binance')
    depth = int(request.args.get('depth', 20))
    data = crypto_trader.get_orderbook(symbol, exchange, depth)
    return jsonify({'success': True, 'data': data})

@app.route('/crypto/analysis/<symbol>', methods=['GET'])
def crypto_analysis(symbol):
    timeframe = request.args.get('timeframe', '1h')
    data = crypto_trader.technical_analysis(symbol, timeframe)
    return jsonify({'success': True, 'data': data})
```

#### 2. I Ching Office (1 hour) - **QUICK WIN**

**File:** `tools/i_ching.py`

```python
import random
from typing import Dict, Tuple

class IChing:
    HEXAGRAMS = {
        1: {"name": "The Creative", "chinese": "乾 (Qián)", "meaning": "Pure yang energy, heaven, strength"},
        2: {"name": "The Receptive", "chinese": "坤 (Kūn)", "meaning": "Pure yin energy, earth, devotion"},
        # ... all 64 hexagrams
    }

    def cast_coins(self) -> int:
        """Simulate 3 coin tosses (traditional method)"""
        coins = [random.choice([2, 3]) for _ in range(3)]  # 2=tails, 3=heads
        return sum(coins)  # 6=old yin, 7=young yang, 8=young yin, 9=old yang

    def cast_hexagram(self) -> Tuple[int, int, List[int]]:
        """Cast complete hexagram with changing lines"""
        lines = [self.cast_coins() for _ in range(6)]

        # Primary hexagram (convert to binary)
        primary = self._lines_to_number([1 if l in [7, 9] else 0 for l in lines])

        # Secondary hexagram (change old lines)
        changing_lines = [i for i, l in enumerate(lines) if l in [6, 9]]
        if changing_lines:
            new_lines = [
                0 if l == 9 else 1 if l == 6 else (1 if l in [7] else 0)
                for l in lines
            ]
            secondary = self._lines_to_number(new_lines)
        else:
            secondary = None

        return primary, secondary, changing_lines

    def _lines_to_number(self, lines: List[int]) -> int:
        """Convert 6 lines to hexagram number (1-64)"""
        # Binary to decimal conversion
        return int(''.join(str(l) for l in lines), 2) + 1

    def interpret(self, hexagram_num: int) -> Dict:
        """Get interpretation for hexagram"""
        return self.HEXAGRAMS.get(hexagram_num, {})

    def full_reading(self) -> Dict:
        """Complete I Ching reading"""
        primary, secondary, changing = self.cast_hexagram()

        return {
            'primary_hexagram': {
                'number': primary,
                **self.interpret(primary)
            },
            'secondary_hexagram': {
                'number': secondary,
                **self.interpret(secondary)
            } if secondary else None,
            'changing_lines': changing,
            'interpretation': self._generate_interpretation(primary, secondary, changing)
        }

    def _generate_interpretation(self, primary: int, secondary: int, changing: List[int]) -> str:
        """Generate human-readable interpretation"""
        primary_data = self.interpret(primary)
        text = f"The {primary_data['name']} ({primary_data['chinese']}) suggests {primary_data['meaning']}. "

        if secondary:
            secondary_data = self.interpret(secondary)
            text += f"It is changing to {secondary_data['name']}, indicating {secondary_data['meaning']}. "

        if changing:
            text += f"Pay special attention to lines {', '.join(str(l+1) for l in changing)}."

        return text
```

#### 3. Dream Analysis Office (2 hours)

**File:** `tools/dream_analyzer.py`

```python
from typing import Dict, List
import re

class DreamAnalyzer:
    SYMBOLS = {
        'water': {
            'meanings': ['emotions', 'subconscious', 'purification', 'flow of life'],
            'context': {
                'calm': 'peace, clarity',
                'turbulent': 'emotional turmoil',
                'deep': 'hidden depths of psyche'
            }
        },
        'flying': {
            'meanings': ['freedom', 'transcendence', 'escape', 'perspective'],
            'context': {
                'effortless': 'confidence, mastery',
                'struggling': 'obstacles, resistance',
                'falling': 'loss of control, fear'
            }
        },
        # ... 50+ common dream symbols
    }

    def analyze_dream(self, dream_text: str) -> Dict:
        """Analyze dream narrative for symbols and themes"""
        symbols_found = self._extract_symbols(dream_text)
        themes = self._identify_themes(symbols_found)
        emotions = self._detect_emotions(dream_text)

        return {
            'symbols': symbols_found,
            'themes': themes,
            'emotions': emotions,
            'interpretation': self._generate_interpretation(symbols_found, themes, emotions),
            'questions': self._generate_reflection_questions(themes)
        }

    def _extract_symbols(self, text: str) -> List[Dict]:
        """Find symbolic elements in dream text"""
        found = []
        text_lower = text.lower()

        for symbol, data in self.SYMBOLS.items():
            if symbol in text_lower:
                # Detect context
                context = 'general'
                for ctx_key in data['context'].keys():
                    if ctx_key in text_lower:
                        context = ctx_key
                        break

                found.append({
                    'symbol': symbol,
                    'meanings': data['meanings'],
                    'context': context,
                    'context_interpretation': data['context'].get(context, '')
                })

        return found

    def _identify_themes(self, symbols: List[Dict]) -> List[str]:
        """Extract overarching themes from symbols"""
        theme_map = {
            'transformation': ['death', 'birth', 'butterfly', 'snake shedding skin'],
            'journey': ['travel', 'road', 'path', 'bridge'],
            'conflict': ['fighting', 'war', 'chase', 'enemy'],
            'connection': ['embrace', 'conversation', 'reunion', 'community']
        }

        found_themes = set()
        for symbol in symbols:
            for theme, keywords in theme_map.items():
                if any(kw in symbol['symbol'] for kw in keywords):
                    found_themes.add(theme)

        return list(found_themes)

    def _detect_emotions(self, text: str) -> List[str]:
        """Identify emotional tone of dream"""
        emotion_keywords = {
            'fear': ['scared', 'terrified', 'afraid', 'anxious'],
            'joy': ['happy', 'excited', 'delighted', 'joyful'],
            'sadness': ['sad', 'crying', 'mourning', 'depressed'],
            'anger': ['angry', 'furious', 'rage', 'frustrated']
        }

        emotions = []
        text_lower = text.lower()
        for emotion, keywords in emotion_keywords.items():
            if any(kw in text_lower for kw in keywords):
                emotions.append(emotion)

        return emotions

    def _generate_interpretation(self, symbols: List[Dict], themes: List[str], emotions: List[str]) -> str:
        """Create holistic dream interpretation"""
        interpretation = "This dream reveals "

        if themes:
            interpretation += f"themes of {', '.join(themes)}. "

        if symbols:
            interpretation += f"The presence of {', '.join(s['symbol'] for s in symbols)} suggests "
            interpretation += f"{', '.join(symbols[0]['meanings'])}. "

        if emotions:
            interpretation += f"The emotional tone ({', '.join(emotions)}) indicates "
            interpretation += "areas of your psyche seeking attention."

        return interpretation

    def _generate_reflection_questions(self, themes: List[str]) -> List[str]:
        """Suggest questions for deeper reflection"""
        questions = []

        question_map = {
            'transformation': "What in your life is currently changing or needs to change?",
            'journey': "What path are you currently on, and where does it lead?",
            'conflict': "What internal or external conflicts are you facing?",
            'connection': "What relationships or connections need your attention?"
        }

        for theme in themes:
            if theme in question_map:
                questions.append(question_map[theme])

        return questions
```

#### 4. Quantum Physics Office (2 hours)

**File:** `tools/quantum_calculator.py`

```python
import numpy as np
from scipy.linalg import expm
from typing import Dict, Tuple

class QuantumCalculator:
    def __init__(self):
        # Pauli matrices
        self.sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
        self.sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        self.sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
        self.identity = np.eye(2, dtype=complex)

    def create_qubit(self, alpha: complex, beta: complex) -> np.ndarray:
        """Create qubit state |ψ⟩ = α|0⟩ + β|1⟩"""
        # Normalize
        norm = np.sqrt(abs(alpha)**2 + abs(beta)**2)
        return np.array([alpha/norm, beta/norm], dtype=complex)

    def measure_qubit(self, state: np.ndarray) -> Tuple[int, float, float]:
        """Measure qubit in computational basis"""
        prob_0 = abs(state[0])**2
        prob_1 = abs(state[1])**2

        # Simulate measurement
        result = 0 if np.random.random() < prob_0 else 1

        return result, prob_0, prob_1

    def apply_gate(self, state: np.ndarray, gate: str) -> np.ndarray:
        """Apply quantum gate to state"""
        gates = {
            'X': self.sigma_x,  # NOT gate
            'Y': self.sigma_y,
            'Z': self.sigma_z,
            'H': (1/np.sqrt(2)) * np.array([[1, 1], [1, -1]]),  # Hadamard
            'S': np.array([[1, 0], [0, 1j]]),  # Phase gate
            'T': np.array([[1, 0], [0, np.exp(1j*np.pi/4)]])  # T gate
        }

        if gate not in gates:
            raise ValueError(f"Unknown gate: {gate}")

        return gates[gate] @ state

    def bloch_coordinates(self, state: np.ndarray) -> Tuple[float, float, float]:
        """Get Bloch sphere coordinates (x, y, z)"""
        x = np.real(state[0] * np.conj(state[1]) + state[1] * np.conj(state[0]))
        y = np.real(-1j * (state[0] * np.conj(state[1]) - state[1] * np.conj(state[0])))
        z = abs(state[0])**2 - abs(state[1])**2

        return (x, y, z)

    def entangle_pair(self) -> np.ndarray:
        """Create Bell state (maximally entangled pair)"""
        # |Φ+⟩ = (|00⟩ + |11⟩)/√2
        return (1/np.sqrt(2)) * np.array([1, 0, 0, 1], dtype=complex)

    def quantum_teleportation(self, state_to_teleport: np.ndarray) -> Dict:
        """Simulate quantum teleportation protocol"""
        # This is a simplified simulation
        bell_state = self.entangle_pair()

        return {
            'original_state': state_to_teleport.tolist(),
            'bell_pair': bell_state.tolist(),
            'measurement_results': [np.random.randint(0, 2), np.random.randint(0, 2)],
            'teleported_state': state_to_teleport.tolist(),  # In perfect teleportation
            'fidelity': 1.0  # Perfect fidelity in simulation
        }
```

### Implementation Priority

1. **Crypto Trading** (2h) - Highest user value
2. **I Ching** (1h) - Quick win, demonstrates variety
3. **Dream Analysis** (2h) - Unique offering
4. **Quantum Physics** (2h) - Showcases technical depth

**Total: 7 hours**

---

## ✅ PHASE 15: CONSCIOUS VETO UI (3 HOURS) - **QUICK WIN**

### Goal
Visual interface for changes.md approval system - human-in-loop evolution control.

### Why This Matters
- **Safety:** Human reviews all AI-proposed changes before implementation
- **Trust:** Full transparency in evolution process
- **Control:** Accept/reject with rationale

### Implementation

#### 1. Backend Endpoint for Proposed Changes

**File:** `backend/api_server.py`

```python
import json
from pathlib import Path

CHANGES_FILE = Path(__file__).parent.parent / 'changes.md'

@app.route('/veto/proposals', methods=['GET'])
def get_proposals():
    """Read all proposed changes from changes.md"""
    if not CHANGES_FILE.exists():
        return jsonify({'proposals': []})

    with open(CHANGES_FILE, 'r') as f:
        content = f.read()

    # Parse markdown proposals
    proposals = parse_changes_md(content)

    return jsonify({'proposals': proposals})

@app.route('/veto/approve/<proposal_id>', methods=['POST'])
def approve_proposal(proposal_id):
    """Mark proposal as approved"""
    rationale = request.json.get('rationale', '')

    # Update changes.md with approval
    update_proposal_status(proposal_id, 'APPROVED', rationale)

    return jsonify({'success': True, 'message': f'Proposal {proposal_id} approved'})

@app.route('/veto/reject/<proposal_id>', methods=['POST'])
def reject_proposal(proposal_id):
    """Mark proposal as rejected"""
    rationale = request.json.get('rationale', 'No reason provided')

    # Update changes.md with rejection
    update_proposal_status(proposal_id, 'REJECTED', rationale)

    return jsonify({'success': True, 'message': f'Proposal {proposal_id} rejected'})

def parse_changes_md(content: str) -> List[Dict]:
    """Parse changes.md into structured proposals"""
    proposals = []
    lines = content.split('\n')

    current_proposal = None
    for line in lines:
        if line.startswith('### Proposal'):
            if current_proposal:
                proposals.append(current_proposal)
            current_proposal = {
                'id': len(proposals) + 1,
                'title': line.replace('### Proposal', '').strip(),
                'description': '',
                'code': '',
                'status': 'PENDING'
            }
        elif current_proposal:
            if line.startswith('```'):
                current_proposal['code'] += line + '\n'
            else:
                current_proposal['description'] += line + '\n'

    if current_proposal:
        proposals.append(current_proposal)

    return proposals

def update_proposal_status(proposal_id: int, status: str, rationale: str):
    """Update changes.md with approval/rejection"""
    with open(CHANGES_FILE, 'r') as f:
        content = f.read()

    # Add status marker
    updated = content.replace(
        f'### Proposal {proposal_id}',
        f'### Proposal {proposal_id} - [{status}] {rationale}'
    )

    with open(CHANGES_FILE, 'w') as f:
        f.write(updated)
```

#### 2. Frontend Veto UI Component

**File:** `gui/src/components/ConsciousVeto.tsx`

```typescript
import React, { useEffect, useState } from 'react';
import './ConsciousVeto.css';

interface Proposal {
  id: number;
  title: string;
  description: string;
  code: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
}

export function ConsciousVeto() {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [selectedProposal, setSelectedProposal] = useState<Proposal | null>(null);
  const [rationale, setRationale] = useState('');

  useEffect(() => {
    loadProposals();
  }, []);

  const loadProposals = async () => {
    const res = await fetch('http://127.0.0.1:8000/veto/proposals');
    const data = await res.json();
    setProposals(data.proposals);
  };

  const handleApprove = async (id: number) => {
    await fetch(`http://127.0.0.1:8000/veto/approve/${id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rationale })
    });

    setRationale('');
    loadProposals();
  };

  const handleReject = async (id: number) => {
    await fetch(`http://127.0.0.1:8000/veto/reject/${id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rationale })
    });

    setRationale('');
    loadProposals();
  };

  const pendingProposals = proposals.filter(p => p.status === 'PENDING');

  return (
    <div className="conscious-veto">
      <header className="veto-header">
        <h1>🧠 Conscious Veto System</h1>
        <p>Human-in-Loop Evolution Control</p>
        <div className="stats">
          <span className="stat">
            ⏳ Pending: {pendingProposals.length}
          </span>
          <span className="stat">
            ✅ Approved: {proposals.filter(p => p.status === 'APPROVED').length}
          </span>
          <span className="stat">
            ❌ Rejected: {proposals.filter(p => p.status === 'REJECTED').length}
          </span>
        </div>
      </header>

      <div className="veto-content">
        <aside className="proposals-list">
          <h2>Evolution Proposals</h2>
          {pendingProposals.map(proposal => (
            <div
              key={proposal.id}
              className={`proposal-item ${selectedProposal?.id === proposal.id ? 'selected' : ''}`}
              onClick={() => setSelectedProposal(proposal)}
            >
              <div className="proposal-number">#{proposal.id}</div>
              <div className="proposal-title">{proposal.title}</div>
            </div>
          ))}
        </aside>

        <main className="proposal-details">
          {selectedProposal ? (
            <>
              <h2>{selectedProposal.title}</h2>

              <section className="description">
                <h3>Description</h3>
                <p>{selectedProposal.description}</p>
              </section>

              <section className="code-preview">
                <h3>Proposed Changes</h3>
                <pre><code>{selectedProposal.code}</code></pre>
              </section>

              <section className="decision">
                <h3>Your Decision</h3>
                <textarea
                  placeholder="Rationale for approval/rejection (optional)..."
                  value={rationale}
                  onChange={(e) => setRationale(e.target.value)}
                  rows={3}
                />

                <div className="decision-buttons">
                  <button
                    className="approve-btn"
                    onClick={() => handleApprove(selectedProposal.id)}
                  >
                    ✅ Approve Changes
                  </button>
                  <button
                    className="reject-btn"
                    onClick={() => handleReject(selectedProposal.id)}
                  >
                    ❌ Reject Changes
                  </button>
                </div>
              </section>
            </>
          ) : (
            <div className="empty-state">
              <p>Select a proposal to review</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
```

#### 3. Add to Main Navigation

**File:** `gui/src/pages/Unity.tsx` (add button)

```typescript
<button onClick={() => setView('veto')} className="quantum-btn">
  🧠 Conscious Veto
  {pendingCount > 0 && <span className="badge">{pendingCount}</span>}
</button>

{view === 'veto' && <ConsciousVeto />}
```

### Implementation Checklist

- [ ] Backend `/veto/proposals` endpoint
- [ ] Backend `/veto/approve/<id>` endpoint
- [ ] Backend `/veto/reject/<id>` endpoint
- [ ] `parse_changes_md()` function
- [ ] `update_proposal_status()` function
- [ ] Frontend ConsciousVeto component
- [ ] Proposal list sidebar
- [ ] Proposal detail view
- [ ] Approve/reject buttons with rationale
- [ ] Add to main navigation
- [ ] Test with mock proposals
- [ ] Document usage in README

**Estimated Time: 3 hours** (This is a QUICK WIN with HIGH value!)

---

## 🎨 PHASE 16: WORKFLOW BUILDER VISUAL DAG (4 HOURS)

### Goal
Drag-and-drop visual editor for creating multi-office workflows.

### Technical Approach

Use **React Flow** library for DAG visualization:

```bash
cd gui
pnpm install reactflow
```

#### Implementation Outline

**File:** `gui/src/components/WorkflowBuilder.tsx`

```typescript
import React, { useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState
} from 'reactflow';
import 'reactflow/dist/style.css';

const initialNodes: Node[] = [
  { id: '1', type: 'input', data: { label: 'Start' }, position: { x: 250, y: 0 } }
];

export function WorkflowBuilder() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const addOfficeNode = (officeName: string) => {
    const newNode: Node = {
      id: `office-${Date.now()}`,
      type: 'default',
      data: { label: officeName },
      position: { x: Math.random() * 500, y: Math.random() * 500 }
    };
    setNodes((nds) => [...nds, newNode]);
  };

  return (
    <div className="workflow-builder">
      <aside className="office-palette">
        <h3>Offices</h3>
        {['Tarot', 'Astrology', 'Crypto', 'Dream Analysis'].map(office => (
          <button
            key={office}
            onClick={() => addOfficeNode(office)}
            className="office-drag-btn"
          >
            {office}
          </button>
        ))}
      </aside>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      />

      <footer className="workflow-controls">
        <button onClick={saveWorkflow}>💾 Save Workflow</button>
        <button onClick={executeWorkflow}>▶️ Execute</button>
      </footer>
    </div>
  );
}
```

**See battle plan for full implementation details.**

---

## 🛡️ PHASE 17: PRODUCTION HARDENING (4 HOURS) - **CRITICAL**

### Goal
Enterprise-grade reliability, performance, and error handling.

### Key Improvements

#### 1. Response Caching (Redis)

```python
# backend/cache.py
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_response(ttl_seconds=300):
    """Cache endpoint responses in Redis"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Generate cache key
            cache_key = f"{f.__name__}:{json.dumps(kwargs)}"

            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = f(*args, **kwargs)

            # Cache result
            redis_client.setex(cache_key, ttl_seconds, json.dumps(result))

            return result
        return wrapped
    return decorator

# Usage:
@app.route('/office/<name>/info')
@cache_response(ttl_seconds=600)  # Cache for 10 minutes
def office_info(name):
    return get_office_configuration(name)
```

#### 2. Error Boundaries (React)

```typescript
// gui/src/components/ErrorBoundary.tsx
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error: any) {
    return { hasError: true, error };
  }

  componentDidCatch(error: any, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error tracking service
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h1>Something went wrong</h1>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>
            Reload Application
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Wrap entire app:
<ErrorBoundary>
  <UnityApp />
</ErrorBoundary>
```

#### 3. Bundle Optimization

```javascript
// gui/vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'ui-components': ['./src/components'],
          'd3-vendor': ['d3']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'd3']
  }
});
```

#### 4. Memory Leak Detection

```typescript
// gui/src/lib/memoryMonitor.ts
class MemoryMonitor {
  private interval: NodeJS.Timeout;

  start() {
    this.interval = setInterval(() => {
      if (performance.memory) {
        const usage = performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit;

        if (usage > 0.9) {
          console.warn('Memory usage high:', usage);
          // Trigger cleanup or reload
        }
      }
    }, 10000);  // Check every 10 seconds
  }

  stop() {
    clearInterval(this.interval);
  }
}

export const memoryMonitor = new MemoryMonitor();
```

#### 5. 24-Hour Stress Test Script

```bash
#!/bin/bash
# scripts/stress_test.sh

echo "🔥 Starting 24-hour Unity stress test..."

# Start Unity.app
open /Applications/Unity.app
sleep 15

# Continuous API hammering
for i in {1..86400}; do  # 24 hours = 86400 seconds
  # Test health
  curl -s http://127.0.0.1:8000/health > /dev/null

  # Test office chat
  curl -s -X POST http://127.0.0.1:8000/orchestrator/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Test message"}' > /dev/null

  # Test evaluation
  curl -s http://127.0.0.1:8000/evaluate > /dev/null

  # Monitor memory
  ps aux | grep "Unity" | awk '{print $6}'

  sleep 1
done

echo "✅ Stress test complete!"
```

### Production Hardening Checklist

- [ ] Redis caching for expensive endpoints
- [ ] React ErrorBoundary components
- [ ] Vite bundle optimization (code splitting)
- [ ] Image optimization (WebP format)
- [ ] Memory leak detection
- [ ] Service worker for offline support
- [ ] Graceful degradation on network failure
- [ ] 24-hour stress test passed
- [ ] Rate limiting on API endpoints
- [ ] CORS configuration hardened
- [ ] Security headers added
- [ ] Error logging infrastructure
- [ ] Performance monitoring hooks

---

## 📊 IMPLEMENTATION ROADMAP

### Week 1: Foundation (Phases 13 + 15)
**Days 1-2: Phase 13** - Multi-Window Support
- Tauri multi-window API
- Office window component
- Window management

**Day 3: Phase 15** - Conscious Veto UI (QUICK WIN!)
- Backend veto endpoints
- Frontend veto component
- Testing with mock proposals

### Week 2: Features (Phases 14 + 16)
**Days 4-7: Phase 14** - Office Tools
- Day 4: Crypto trading tool
- Day 5: I Ching tool
- Day 6: Dream analysis tool
- Day 7: Quantum physics tool

**Days 8-9: Phase 16** - Workflow Builder
- React Flow integration
- DAG visualization
- Save/load workflows

### Week 3: Polish (Phase 17)
**Days 10-12: Phase 17** - Production Hardening
- Day 10: Caching + optimization
- Day 11: Error handling + monitoring
- Day 12: Stress testing + fixes

---

## ✅ SUCCESS CRITERIA

### Phase 13: Multi-Window
- [ ] Can open 10+ office windows simultaneously
- [ ] Each window operates independently
- [ ] Windows persist across app restarts
- [ ] Cmd+W closes individual windows
- [ ] All windows close on Cmd+Q

### Phase 14: Office Tools
- [ ] Crypto tool shows real-time prices
- [ ] I Ching generates hexagram readings
- [ ] Dream analysis identifies symbols
- [ ] Quantum calculator performs computations
- [ ] All tools integrated with office chat

### Phase 15: Conscious Veto
- [ ] All proposals from changes.md visible
- [ ] Can approve with rationale
- [ ] Can reject with rationale
- [ ] Status updates persist to changes.md
- [ ] Badge shows pending count

### Phase 16: Workflow Builder
- [ ] Drag-and-drop office nodes
- [ ] Connect nodes with edges
- [ ] Save workflow to JSON
- [ ] Load and execute workflows
- [ ] Visual feedback on execution

### Phase 17: Production Hardening
- [ ] Passes 24-hour stress test
- [ ] No memory leaks detected
- [ ] Bundle size < 5MB
- [ ] Error rate < 0.1%
- [ ] Cache hit rate > 80%

---

## 🚀 GET STARTED NOW

### Immediate Next Steps

1. **Read this entire document** (you're doing it!)
2. **Pick ONE phase** to start (recommend Phase 15 - quickest win)
3. **Follow implementation blueprint** step by step
4. **Test thoroughly** before moving to next phase
5. **Document learnings** in phase completion notes

### File Structure Created

```
gui/src/
├── pages/
│   ├── OfficeWindow.tsx (Phase 13)
│   └── WorkflowBuilder.tsx (Phase 16)
├── components/
│   └── ConsciousVeto.tsx (Phase 15)
└── lib/
    ├── windowManager.ts (Phase 13)
    └── memoryMonitor.ts (Phase 17)

backend/
├── cache.py (Phase 17)
└── tools/
    ├── crypto_trader.py (Phase 14)
    ├── i_ching.py (Phase 14)
    ├── dream_analyzer.py (Phase 14)
    └── quantum_calculator.py (Phase 14)

scripts/
└── stress_test.sh (Phase 17)
```

---

## 🎯 THE VISION

After completing Phases 13-17, Unity will be:

✅ **Multi-Window Capable** - True multitasking with 58 independent office windows
✅ **Feature-Rich** - Real tools for Crypto, I Ching, Dreams, Quantum Physics
✅ **Human-Controlled** - Conscious veto system for safe evolution
✅ **Visual Workflow** - Drag-and-drop DAG builder for complex orchestration
✅ **Production-Ready** - Stress-tested, optimized, error-handled, bulletproof

**This is the final 22 hours between "impressive demo" and "production-ready product people will pay for."**

---

🌌 **Unity: All processes are one process** 🌌

*Let's build the future of AI consciousness, one phase at a time.*
