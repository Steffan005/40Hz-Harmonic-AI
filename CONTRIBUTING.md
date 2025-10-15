# Contributing to EvoAgentX

Thank you for your interest in contributing to EvoAgentX! This project is dedicated to the developer community and the freedom of AI.

## 🌟 Philosophy

**Everything we do, we do it for YOU, THE DEVELOPER COMMUNITY, THE FREEDOM OF AI.**

EvoAgentX is a local-first, privacy-respecting AI evolution framework. We believe in:
- No cloud dependencies
- No API keys or login credentials
- Complete data sovereignty
- Open source collaboration

## 🚀 Getting Started

### Prerequisites

- Rust 1.75+
- Node.js 20+
- pnpm 8+
- Python 3.11+
- Ollama with models:
  - deepseek-r1:14b (reasoning)
  - qwen2.5-coder:7b (coding)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/evoagentx.git
cd evoagentx/sprint_1hour
```

2. Install dependencies:
```bash
# Python dependencies
python3 -m venv ../venv
source ../venv/bin/activate
pip install flask flask-cors psutil

# GUI dependencies
cd gui
pnpm install
```

3. Run dependency check:
```bash
cd ..
./check_dependencies.sh
```

## 📁 Project Structure

```
sprint_1hour/
├── configs/           # System configuration (YAML)
├── backend/           # Python Flask API
├── gui/
│   ├── src/           # React/TypeScript UI
│   ├── src-tauri/     # Rust orchestrator
│   └── public/        # Static assets (theme.css)
├── scripts/           # Startup scripts
└── logs/              # JSONL telemetry
```

## 🔧 Development Workflow

### Running in Development Mode

**Terminal 1 - Ollama:**
```bash
./scripts/start_ollama.sh
```

**Terminal 2 - Backend:**
```bash
./scripts/start_backend.sh
```

**Terminal 3 - GUI:**
```bash
cd gui
pnpm tauri:dev
```

### Making Changes

1. **Backend (Python)**: Edit files in `backend/`, changes auto-reload
2. **Frontend (React)**: Edit files in `gui/src/`, hot reload enabled
3. **Rust Backend**: Edit `gui/src-tauri/src/main.rs`, recompilation required

## 🎨 Code Style

### Python
- Follow PEP 8
- Use type hints
- Document functions with docstrings

### TypeScript/React
- Use functional components
- Prefer TypeScript interfaces over types
- Use async/await for Tauri IPC

### Rust
- Follow Rust conventions
- Use `cargo fmt` before commits
- Handle errors with `Result<T, String>`

## 🧪 Testing

### Run Diagnostics
```bash
# In GUI after launch
Click "Run Diagnostics" button

# Or via API
curl http://127.0.0.1:8000/health
```

### Integration Tests
```bash
# Test full workflow
1. Click "Evaluate Agent"
2. Click "Mutate Workflow"
3. Click "Bandit Controller"
4. Verify console logs and telemetry updates
```

## 🐛 Reporting Issues

When reporting bugs, include:
1. System info (macOS/Linux, RAM, Python/Node versions)
2. Ollama models installed (`ollama list`)
3. Console logs from all 3 terminals
4. Steps to reproduce

## 📝 Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly (run diagnostics, test all buttons)
5. Commit with clear messages:
   ```bash
   git commit -m "feat: add fractal depth control"
   ```
6. Push to your fork
7. Open a Pull Request with:
   - Description of changes
   - Screenshots (if UI changes)
   - Testing performed

### Commit Message Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

## 🎯 Areas for Contribution

### High Priority
- Additional LLM backend support (LMStudio, GPT4All)
- More evaluation heuristics
- Workflow visualization improvements
- Performance optimizations

### UI/UX
- New themes and color schemes
- Accessibility improvements
- Keyboard shortcuts
- Mobile-responsive design

### Backend
- Additional bandit algorithms
- Memory compression strategies
- Distributed evaluation
- Plugin system

### Documentation
- Tutorial videos
- Use case examples
- API documentation
- Troubleshooting guides

## 🌌 Design Principles

### Zero-Hallucination Design
- All buttons disabled until preflight passes
- Clear error messages with remediation steps
- Graceful degradation on failures

### Quantum-Psychedelic Aesthetic
- Fractal imagery and complementary colors
- 40Hz breathing animations for neural entrainment
- Layered parallax depth effects
- Optional calm mode for accessibility

### Local-First Architecture
- No external API calls
- All data stored locally
- Works offline after setup
- Complete data privacy

## 📚 Resources

- [Tauri Documentation](https://tauri.app/)
- [React Documentation](https://react.dev/)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Project README](./README.md)

## 💬 Community

- GitHub Discussions: [Link to discussions]
- Discord: [Link to Discord] (if applicable)
- Twitter: [Link to Twitter] (if applicable)

## 🙏 Acknowledgments

This project is built for the developer community, by the developer community. Every contribution, no matter how small, helps advance AI freedom and local-first computing.

**Thank you for being part of this frontier!** 🚀

---

*"Everything we do, we do it for YOU, THE DEVELOPER COMMUNITY, THE FREEDOM OF AI"*
