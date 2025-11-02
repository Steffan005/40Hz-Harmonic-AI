# Test MiniMax Anthropic Integration NOW

## Quick Start (5 minutes)

### Step 1: Restart Backend (REQUIRED)
```bash
# Stop current backend
cd /Users/steffanhaskins/evoagentx_project/sprint_1hour
lsof -ti:8000 | xargs kill -9

# Start with new code
./scripts/start_backend.sh

# Look for this line:
# ⚡ CLOUD LLM ENABLED: minimax (MiniMax-M2)
```

### Step 2: Open Unity GUI
```
http://localhost:1420
```

### Step 3: Quick Test Sequence

#### Test 1: Hello World (No Tools)
**Type:** "Hello, how are you?"

**Expected:** Quick response (<10 sec), no tool calls

**Success:** ✅ If you get conversational response

---

#### Test 2: List Files (Single Tool)
**Type:** "List files in the offices directory"

**Expected:**
- Calls `list_files` tool
- Returns file list with explanation
- ~10-15 seconds

**Success:** ✅ If you see actual files listed

---

#### Test 3: Read File (Multi-Tool)
**Type:** "Read orchestrator.py and tell me what it does"

**Expected:**
- Calls `list_files` + `read_file`
- Returns summary of orchestrator
- ~20-30 seconds

**Success:** ✅ If you get meaningful code explanation

---

## Check Debug Logs

```bash
tail -f /tmp/orchestrator_debug.log
```

**Look for:**
```
🔥 Calling MiniMax-M2 (Anthropic API) with 7 tools
⟨⦿⟩ Anthropic Response:
✅ Converted N Anthropic tool_use blocks to OpenAI format
⟨⦿⟩ Executing tool: list_files
```

---

## If Something Breaks

### Error: "Cloud LLM API error: 401"
**Fix:** Check API key in `configs/system.yaml`

### Error: "Unknown provider: minimax"
**Fix:** Backend not restarted - kill and restart

### Error: Backend won't start
**Fix:** Check syntax:
```bash
python3 -m py_compile offices/orchestrator.py
```

### No tool calls happening
**Fix:** Check logs for errors, verify tools defined

### Empty responses
**Fix:** Convergence system should catch this, check logs

---

## Switch Back to Together.ai

If MiniMax has issues, switch back:

```yaml
# configs/system.yaml
cloud_llm:
  enabled: true
  provider: "together"  # Change this
  api_key: "adda70d8953c..."  # Together.ai key
  model: "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
```

Restart backend and everything should work as before.

---

## Success Metrics

✅ Backend starts without errors
✅ Simple queries respond in <10 sec
✅ Tool calls execute and return results
✅ Multi-turn conversations work
✅ No "maximum iterations" errors
✅ Logs show Anthropic API calls

---

## What You're Testing

**The Implementation:**
- MiniMax using Anthropic API endpoint
- Format conversion (OpenAI ↔ Anthropic)
- Multi-turn tool calling
- Tool result handling
- Response parsing

**The Proof:**
- Direct test already proved endpoint works
- Now testing full integration in orchestrator
- Tool executor unchanged (provider-agnostic)

---

## That's It!

**3 simple tests = complete validation**

If all 3 pass → Implementation successful! 🎉

If any fail → Check logs, report errors

**Time to test: 5 minutes**
**Time to glory: priceless** 🚀

---

*Ready when you are!*
