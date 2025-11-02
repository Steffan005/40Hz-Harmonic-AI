use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tauri::{Manager, Window, WindowBuilder, WindowUrl};
use tokio::sync::RwLock;
use uuid::Uuid;

/// Represents a Unity Office window instance
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OfficeWindow {
    pub id: String,
    pub office_type: OfficeType,
    pub title: String,
    pub position: Option<(i32, i32)>,
    pub size: (u32, u32),
    pub memory_consent: bool,
    pub shared_memory_ttl: u64, // in seconds
}

/// All 43 office types in Unity
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum OfficeType {
    // Core Offices
    Orchestrator,
    Memory,
    Security,

    // Financial Offices
    TradingOffice,
    CryptoOffice,
    TaxAdvisor,
    FinancialAdvisor,
    BankingOffice,

    // Legal & Compliance
    LegalOffice,
    ComplianceOfficer,
    ContractAnalyst,
    IntellectualProperty,

    // Travel & Lifestyle
    TravelPlanner,
    RestaurantConcierge,
    EventCoordinator,
    PersonalShopper,

    // Health & Wellness
    PhysicalTrainer,
    Nutritionist,
    SleepCoach,
    Psychologist,
    MedicalAdvisor,

    // Creative & Media
    ContentCreator,
    VideoEditor,
    GraphicDesigner,
    MusicProducer,

    // Technical
    DevOpsEngineer,
    DataAnalyst,
    SecurityAnalyst,
    CloudArchitect,

    // Research & Education
    ResearchAnalyst,
    EducationAdvisor,
    LanguageTutor,
    SkillCoach,

    // Spiritual & Personal
    TarotReader,
    Astrologer,
    MeditationGuide,
    LifeCoach,

    // Home & Kitchen
    KitchenManager,
    HomeAutomation,
    MaintenanceScheduler,

    // Special Operations
    QuantumComputing,
    EmergencyResponse,
}

impl OfficeType {
    pub fn to_string(&self) -> String {
        match self {
            Self::Orchestrator => "Orchestrator".to_string(),
            Self::Memory => "Memory Graph".to_string(),
            Self::Security => "Security Office".to_string(),
            Self::TradingOffice => "Trading Office".to_string(),
            Self::CryptoOffice => "Crypto Office".to_string(),
            Self::TaxAdvisor => "Tax Advisor".to_string(),
            Self::FinancialAdvisor => "Financial Advisor".to_string(),
            Self::BankingOffice => "Banking Office".to_string(),
            Self::LegalOffice => "Legal Office".to_string(),
            Self::ComplianceOfficer => "Compliance Officer".to_string(),
            Self::ContractAnalyst => "Contract Analyst".to_string(),
            Self::IntellectualProperty => "IP Office".to_string(),
            Self::TravelPlanner => "Travel Planner".to_string(),
            Self::RestaurantConcierge => "Restaurant Concierge".to_string(),
            Self::EventCoordinator => "Event Coordinator".to_string(),
            Self::PersonalShopper => "Personal Shopper".to_string(),
            Self::PhysicalTrainer => "Physical Trainer".to_string(),
            Self::Nutritionist => "Nutritionist".to_string(),
            Self::SleepCoach => "Sleep Coach".to_string(),
            Self::Psychologist => "Psychologist".to_string(),
            Self::MedicalAdvisor => "Medical Advisor".to_string(),
            Self::ContentCreator => "Content Creator".to_string(),
            Self::VideoEditor => "Video Editor".to_string(),
            Self::GraphicDesigner => "Graphic Designer".to_string(),
            Self::MusicProducer => "Music Producer".to_string(),
            Self::DevOpsEngineer => "DevOps Engineer".to_string(),
            Self::DataAnalyst => "Data Analyst".to_string(),
            Self::SecurityAnalyst => "Security Analyst".to_string(),
            Self::CloudArchitect => "Cloud Architect".to_string(),
            Self::ResearchAnalyst => "Research Analyst".to_string(),
            Self::EducationAdvisor => "Education Advisor".to_string(),
            Self::LanguageTutor => "Language Tutor".to_string(),
            Self::SkillCoach => "Skill Coach".to_string(),
            Self::TarotReader => "Tarot Reader".to_string(),
            Self::Astrologer => "Astrologer".to_string(),
            Self::MeditationGuide => "Meditation Guide".to_string(),
            Self::LifeCoach => "Life Coach".to_string(),
            Self::KitchenManager => "Kitchen Manager".to_string(),
            Self::HomeAutomation => "Home Automation".to_string(),
            Self::MaintenanceScheduler => "Maintenance Scheduler".to_string(),
            Self::QuantumComputing => "Quantum Computing".to_string(),
            Self::EmergencyResponse => "Emergency Response".to_string(),
        }
    }

    pub fn get_default_size(&self) -> (u32, u32) {
        match self {
            Self::Orchestrator => (1400, 900),
            Self::Memory => (1200, 800),
            Self::TradingOffice | Self::CryptoOffice => (1600, 900),
            Self::QuantumComputing => (1500, 850),
            _ => (1024, 768),
        }
    }

    pub fn get_url(&self) -> String {
        let base_url = "http://localhost:1420";
        match self {
            Self::Orchestrator => format!("{}/", base_url),
            Self::Memory => format!("{}/memory", base_url),
            Self::Security => format!("{}/security", base_url),
            _ => format!("{}/office/{:?}", base_url, self).to_lowercase(),
        }
    }
}

/// Manages all Unity office windows
pub struct WindowManager {
    windows: Arc<RwLock<HashMap<String, OfficeWindow>>>,
    app_handle: tauri::AppHandle,
}

impl WindowManager {
    pub fn new(app_handle: tauri::AppHandle) -> Self {
        Self {
            windows: Arc::new(RwLock::new(HashMap::new())),
            app_handle,
        }
    }

    /// Create a new office window
    pub async fn create_office_window(
        &self,
        office_type: OfficeType,
        memory_consent: bool,
        shared_memory_ttl: Option<u64>,
    ) -> Result<String, String> {
        let window_id = format!("office_{}", Uuid::new_v4());
        let title = format!("Unity — {}", office_type.to_string());
        let size = office_type.get_default_size();
        let url = office_type.get_url();

        // Create the actual Tauri window
        let window = WindowBuilder::new(
            &self.app_handle,
            &window_id,
            WindowUrl::App(url.into()),
        )
        .title(&title)
        .inner_size(size.0 as f64, size.1 as f64)
        .resizable(true)
        .center()
        .build()
        .map_err(|e| format!("Failed to create window: {}", e))?;

        // Store window metadata
        let office_window = OfficeWindow {
            id: window_id.clone(),
            office_type: office_type.clone(),
            title,
            position: None,
            size,
            memory_consent,
            shared_memory_ttl: shared_memory_ttl.unwrap_or(3600), // Default 1 hour TTL
        };

        let mut windows = self.windows.write().await;
        windows.insert(window_id.clone(), office_window);

        // Set up IPC handlers for this window
        self.setup_window_ipc(&window, office_type).await?;

        Ok(window_id)
    }

    /// Set up inter-process communication for a window
    async fn setup_window_ipc(
        &self,
        window: &Window,
        office_type: OfficeType,
    ) -> Result<(), String> {
        let window_clone = window.clone();

        // Listen for memory sharing requests
        window.listen("request_memory_access", move |event| {
            println!(
                "Office {:?} requesting memory access: {:?}",
                office_type, event.payload()
            );
        });

        // Listen for inter-office messages
        let window_clone2 = window.clone();
        window.listen("inter_office_message", move |event| {
            println!(
                "Inter-office message for {:?}: {:?}",
                office_type, event.payload()
            );
        });

        Ok(())
    }

    /// Close an office window
    pub async fn close_office_window(&self, window_id: &str) -> Result<(), String> {
        // Remove from tracking
        let mut windows = self.windows.write().await;
        windows.remove(window_id);

        // Close the actual window
        if let Some(window) = self.app_handle.get_window(window_id) {
            window.close().map_err(|e| format!("Failed to close window: {}", e))?;
        }

        Ok(())
    }

    /// Get all active office windows
    pub async fn get_active_offices(&self) -> Vec<OfficeWindow> {
        let windows = self.windows.read().await;
        windows.values().cloned().collect()
    }

    /// Send a message to a specific office
    pub async fn send_to_office(
        &self,
        office_type: &OfficeType,
        message: serde_json::Value,
    ) -> Result<(), String> {
        let windows = self.windows.read().await;

        for (window_id, office_window) in windows.iter() {
            if office_window.office_type == *office_type {
                if let Some(window) = self.app_handle.get_window(window_id) {
                    window
                        .emit("office_message", &message)
                        .map_err(|e| format!("Failed to send message: {}", e))?;
                }
            }
        }

        Ok(())
    }

    /// Broadcast a message to all offices
    pub async fn broadcast_to_all(&self, message: serde_json::Value) -> Result<(), String> {
        let windows = self.windows.read().await;

        for window_id in windows.keys() {
            if let Some(window) = self.app_handle.get_window(window_id) {
                window
                    .emit("system_broadcast", &message)
                    .map_err(|e| format!("Failed to broadcast: {}", e))?;
            }
        }

        Ok(())
    }

    /// Update memory sharing consent for an office
    pub async fn update_memory_consent(
        &self,
        window_id: &str,
        consent: bool,
    ) -> Result<(), String> {
        let mut windows = self.windows.write().await;

        if let Some(office_window) = windows.get_mut(window_id) {
            office_window.memory_consent = consent;

            // Notify the window of the consent update
            if let Some(window) = self.app_handle.get_window(window_id) {
                window
                    .emit("memory_consent_updated", &consent)
                    .map_err(|e| format!("Failed to update consent: {}", e))?;
            }

            Ok(())
        } else {
            Err("Window not found".to_string())
        }
    }

    /// Update TTL for shared memory
    pub async fn update_memory_ttl(&self, window_id: &str, ttl: u64) -> Result<(), String> {
        let mut windows = self.windows.write().await;

        if let Some(office_window) = windows.get_mut(window_id) {
            office_window.shared_memory_ttl = ttl;
            Ok(())
        } else {
            Err("Window not found".to_string())
        }
    }

    /// Orchestrate a multi-office workflow
    pub async fn orchestrate_workflow(
        &self,
        workflow: WorkflowDefinition,
    ) -> Result<String, String> {
        let workflow_id = Uuid::new_v4().to_string();

        // Execute workflow steps
        for step in workflow.steps {
            match step.action {
                WorkflowAction::OpenOffice(office_type) => {
                    self.create_office_window(office_type, true, None).await?;
                }
                WorkflowAction::SendMessage(office_type, message) => {
                    self.send_to_office(&office_type, message).await?;
                }
                WorkflowAction::WaitForResponse(timeout) => {
                    tokio::time::sleep(tokio::time::Duration::from_secs(timeout)).await;
                }
                WorkflowAction::CloseOffice(window_id) => {
                    self.close_office_window(&window_id).await?;
                }
            }
        }

        Ok(workflow_id)
    }
}

/// Workflow definition for multi-office orchestration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkflowDefinition {
    pub name: String,
    pub steps: Vec<WorkflowStep>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkflowStep {
    pub action: WorkflowAction,
    pub description: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum WorkflowAction {
    OpenOffice(OfficeType),
    SendMessage(OfficeType, serde_json::Value),
    WaitForResponse(u64),
    CloseOffice(String),
}

/// Tauri commands for window management
#[tauri::command]
pub async fn create_office(
    state: tauri::State<'_, Arc<RwLock<WindowManager>>>,
    office_type: String,
    memory_consent: bool,
) -> Result<String, String> {
    let office_type = serde_json::from_str::<OfficeType>(&format!("\"{}\"", office_type))
        .map_err(|e| format!("Invalid office type: {}", e))?;

    let manager = state.read().await;
    manager.create_office_window(office_type, memory_consent, None).await
}

#[tauri::command]
pub async fn close_office(
    state: tauri::State<'_, Arc<RwLock<WindowManager>>>,
    window_id: String,
) -> Result<(), String> {
    let manager = state.read().await;
    manager.close_office_window(&window_id).await
}

#[tauri::command]
pub async fn get_offices(
    state: tauri::State<'_, Arc<RwLock<WindowManager>>>,
) -> Result<Vec<OfficeWindow>, String> {
    let manager = state.read().await;
    Ok(manager.get_active_offices().await)
}

#[tauri::command]
pub async fn send_office_message(
    state: tauri::State<'_, Arc<RwLock<WindowManager>>>,
    office_type: String,
    message: serde_json::Value,
) -> Result<(), String> {
    let office_type = serde_json::from_str::<OfficeType>(&format!("\"{}\"", office_type))
        .map_err(|e| format!("Invalid office type: {}", e))?;

    let manager = state.read().await;
    manager.send_to_office(&office_type, message).await
}

#[tauri::command]
pub async fn broadcast_message(
    state: tauri::State<'_, Arc<RwLock<WindowManager>>>,
    message: serde_json::Value,
) -> Result<(), String> {
    let manager = state.read().await;
    manager.broadcast_to_all(message).await
}