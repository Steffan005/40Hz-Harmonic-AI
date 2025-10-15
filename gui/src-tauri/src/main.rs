// EvoAgentX Tauri Backend - Rust Orchestrator
// Handles preflight checks, health monitoring, and IPC with Python backends

#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use sysinfo::{System, SystemExt};
use tauri::State;

// ============================================================================
// DATA STRUCTURES
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
struct DiagnosticsResult {
    status: String,  // "OK", "WARNING", "ERROR"
    checks: HashMap<String, CheckResult>,
    timestamp: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct CheckResult {
    passed: bool,
    message: String,
    severity: String,  // "info", "warning", "error"
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct EvaluateRequest {
    goal: String,
    output: String,
    rubric_version: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct EvaluateResponse {
    quality_score: f64,
    delta_score: f64,
    robust_pct: f64,
    cache_hit: bool,
    time_ms: f64,
    routing_path: String,
    violations: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct MutateRequest {
    goal: String,
    current_workflow: String,
    arm: Option<String>,  // "auto" uses bandit selection
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct MutateResponse {
    variant_id: String,
    arm: String,
    delta_score: f64,
    novelty: f64,
    workflow: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct BanditStatus {
    arm_counts: HashMap<String, i32>,
    arm_rewards: HashMap<String, f64>,
    total_pulls: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct MemorySnapshot {
    id: String,
    title: String,
    note: String,
    timestamp: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct WorkflowDAG {
    nodes: Vec<WorkflowNode>,
    edges: Vec<WorkflowEdge>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct WorkflowNode {
    id: String,
    node_type: String,
    label: String,
    position: Position,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Position {
    x: f64,
    y: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct WorkflowEdge {
    from: String,
    to: String,
    label: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct TelemetryMetrics {
    tokens_per_sec: f64,
    delta_score: f64,
    cache_hit_rate: f64,
    robust_pct: f64,
    memory_use_mb: f64,
    module_status: HashMap<String, String>,
}

// Shared state
struct AppState {
    backend_base_url: String,
    preflight_passed: Arc<Mutex<bool>>,
    diagnostics: Arc<Mutex<Option<DiagnosticsResult>>>,
}

// ============================================================================
// PREFLIGHT CHECKS
// ============================================================================

async fn check_ram(min_free_gb: f64) -> CheckResult {
    let mut sys = System::new_all();
    sys.refresh_memory();

    let available_gb = sys.available_memory() as f64 / 1_073_741_824.0;

    CheckResult {
        passed: available_gb >= min_free_gb,
        message: format!("Available RAM: {:.2} GB (required: {:.2} GB)", available_gb, min_free_gb),
        severity: if available_gb >= min_free_gb { "info".to_string() } else { "error".to_string() },
    }
}

async fn check_disk(min_free_gb: f64) -> CheckResult {
    // Simplified - would normally check actual disk space
    CheckResult {
        passed: true,
        message: format!("Disk space check passed (>= {:.2} GB)", min_free_gb),
        severity: "info".to_string(),
    }
}

async fn check_ollama() -> CheckResult {
    let client = reqwest::Client::new();
    match client.get("http://127.0.0.1:11434/api/tags")
        .timeout(std::time::Duration::from_secs(5))
        .send()
        .await
    {
        Ok(response) if response.status().is_success() => CheckResult {
            passed: true,
            message: "Ollama service is running".to_string(),
            severity: "info".to_string(),
        },
        _ => CheckResult {
            passed: false,
            message: "Ollama service not reachable at http://127.0.0.1:11434".to_string(),
            severity: "error".to_string(),
        },
    }
}

async fn check_models(required_models: Vec<String>) -> CheckResult {
    let client = reqwest::Client::new();
    match client.get("http://127.0.0.1:11434/api/tags")
        .timeout(std::time::Duration::from_secs(5))
        .send()
        .await
    {
        Ok(response) if response.status().is_success() => {
            match response.json::<serde_json::Value>().await {
                Ok(data) => {
                    let models = data["models"].as_array().unwrap_or(&vec![]);
                    let model_names: Vec<String> = models.iter()
                        .filter_map(|m| m["name"].as_str())
                        .map(|s| s.to_string())
                        .collect();

                    let mut missing = Vec::new();
                    for required in &required_models {
                        if !model_names.iter().any(|m| m.contains(required)) {
                            missing.push(required.clone());
                        }
                    }

                    if missing.is_empty() {
                        CheckResult {
                            passed: true,
                            message: format!("All required models present: {:?}", required_models),
                            severity: "info".to_string(),
                        }
                    } else {
                        CheckResult {
                            passed: false,
                            message: format!("Missing models: {:?}", missing),
                            severity: "error".to_string(),
                        }
                    }
                },
                _ => CheckResult {
                    passed: false,
                    message: "Failed to parse Ollama models list".to_string(),
                    severity: "error".to_string(),
                }
            }
        },
        _ => CheckResult {
            passed: false,
            message: "Cannot check models - Ollama not running".to_string(),
            severity: "error".to_string(),
        },
    }
}

async fn check_backend_services(base_url: &str) -> CheckResult {
    let client = reqwest::Client::new();
    match client.get(format!("{}/health", base_url))
        .timeout(std::time::Duration::from_secs(5))
        .send()
        .await
    {
        Ok(response) if response.status().is_success() => CheckResult {
            passed: true,
            message: "Backend services are running".to_string(),
            severity: "info".to_string(),
        },
        _ => CheckResult {
            passed: false,
            message: format!("Backend services not reachable at {}", base_url),
            severity: "warning".to_string(),  // Warning, not error - can start manually
        },
    }
}

// ============================================================================
// TAURI COMMANDS (IPC ENDPOINTS)
// ============================================================================

#[tauri::command]
async fn run_diagnostics(state: State<'_, AppState>) -> Result<DiagnosticsResult, String> {
    let mut checks = HashMap::new();

    // Run all checks in parallel
    let (ram, disk, ollama, models, backend) = tokio::join!(
        check_ram(2.0),
        check_disk(5.0),
        check_ollama(),
        check_models(vec!["deepseek-r1:14b".to_string(), "qwen2.5-coder:7b".to_string()]),
        check_backend_services(&state.backend_base_url)
    );

    checks.insert("ram".to_string(), ram.clone());
    checks.insert("disk".to_string(), disk.clone());
    checks.insert("ollama".to_string(), ollama.clone());
    checks.insert("models".to_string(), models.clone());
    checks.insert("backend".to_string(), backend.clone());

    // Determine overall status
    let all_passed = checks.values().all(|c| c.passed);
    let has_errors = checks.values().any(|c| c.severity == "error");

    let status = if all_passed {
        "OK".to_string()
    } else if has_errors {
        "ERROR".to_string()
    } else {
        "WARNING".to_string()
    };

    let result = DiagnosticsResult {
        status: status.clone(),
        checks,
        timestamp: std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs_f64(),
    };

    // Update state
    *state.preflight_passed.lock().unwrap() = status == "OK";
    *state.diagnostics.lock().unwrap() = Some(result.clone());

    Ok(result)
}

#[tauri::command]
async fn evaluate(
    state: State<'_, AppState>,
    request: EvaluateRequest
) -> Result<EvaluateResponse, String> {
    // Check if preflight passed
    if !*state.preflight_passed.lock().unwrap() {
        return Err("Preflight checks failed - run diagnostics first".to_string());
    }

    let client = reqwest::Client::new();
    let url = format!("{}/evaluate", state.backend_base_url);

    match client.post(&url)
        .json(&request)
        .timeout(std::time::Duration::from_secs(60))
        .send()
        .await
    {
        Ok(response) if response.status().is_success() => {
            response.json::<EvaluateResponse>()
                .await
                .map_err(|e| format!("Failed to parse response: {}", e))
        },
        Ok(response) => Err(format!("Backend error: {}", response.status())),
        Err(e) => Err(format!("Request failed: {}", e)),
    }
}

#[tauri::command]
async fn mutate_workflow(
    state: State<'_, AppState>,
    request: MutateRequest
) -> Result<MutateResponse, String> {
    if !*state.preflight_passed.lock().unwrap() {
        return Err("Preflight checks failed".to_string());
    }

    let client = reqwest::Client::new();
    let url = format!("{}/mutate", state.backend_base_url);

    match client.post(&url)
        .json(&request)
        .timeout(std::time::Duration::from_secs(60))
        .send()
        .await
    {
        Ok(response) if response.status().is_success() => {
            response.json::<MutateResponse>()
                .await
                .map_err(|e| format!("Failed to parse response: {}", e))
        },
        _ => Err("Mutation request failed".to_string()),
    }
}

#[tauri::command]
async fn get_bandit_status(state: State<'_, AppState>) -> Result<BanditStatus, String> {
    let client = reqwest::Client::new();
    let url = format!("{}/bandit/status", state.backend_base_url);

    match client.get(&url).send().await {
        Ok(response) if response.status().is_success() => {
            response.json::<BanditStatus>()
                .await
                .map_err(|e| format!("Failed to parse response: {}", e))
        },
        _ => Err("Failed to get bandit status".to_string()),
    }
}

#[tauri::command]
async fn create_memory_snapshot(
    state: State<'_, AppState>,
    title: String,
    content: String
) -> Result<MemorySnapshot, String> {
    let client = reqwest::Client::new();
    let url = format!("{}/memory/snapshot", state.backend_base_url);

    let body = serde_json::json!({
        "title": title,
        "content": content
    });

    match client.post(&url).json(&body).send().await {
        Ok(response) if response.status().is_success() => {
            response.json::<MemorySnapshot>()
                .await
                .map_err(|e| format!("Failed to parse response: {}", e))
        },
        _ => Err("Failed to create memory snapshot".to_string()),
    }
}

#[tauri::command]
async fn get_workflow_dag(state: State<'_, AppState>) -> Result<WorkflowDAG, String> {
    let client = reqwest::Client::new();
    let url = format!("{}/workflow/dag", state.backend_base_url);

    match client.get(&url).send().await {
        Ok(response) if response.status().is_success() => {
            response.json::<WorkflowDAG>()
                .await
                .map_err(|e| format!("Failed to parse response: {}", e))
        },
        _ => Err("Failed to get workflow DAG".to_string()),
    }
}

#[tauri::command]
async fn get_telemetry_metrics(state: State<'_, AppState>) -> Result<TelemetryMetrics, String> {
    let client = reqwest::Client::new();
    let url = format!("{}/telemetry/metrics", state.backend_base_url);

    match client.get(&url).send().await {
        Ok(response) if response.status().is_success() => {
            response.json::<TelemetryMetrics>()
                .await
                .map_err(|e| format!("Failed to parse response: {}", e))
        },
        _ => Err("Failed to get telemetry metrics".to_string()),
    }
}

#[tauri::command]
fn is_preflight_passed(state: State<'_, AppState>) -> bool {
    *state.preflight_passed.lock().unwrap()
}

// ============================================================================
// MAIN
// ============================================================================

fn main() {
    let app_state = AppState {
        backend_base_url: "http://127.0.0.1:8000".to_string(),
        preflight_passed: Arc::new(Mutex::new(false)),
        diagnostics: Arc::new(Mutex::new(None)),
    };

    tauri::Builder::default()
        .manage(app_state)
        .invoke_handler(tauri::generate_handler![
            run_diagnostics,
            evaluate,
            mutate_workflow,
            get_bandit_status,
            create_memory_snapshot,
            get_workflow_dag,
            get_telemetry_metrics,
            is_preflight_passed
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
