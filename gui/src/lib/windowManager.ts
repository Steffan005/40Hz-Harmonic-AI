/**
 * WINDOW MANAGER
 * Manages multiple Tauri windows for office instances
 * Part of Phase 13: Multi-Window Office Support
 */

import { invoke } from '@tauri-apps/api/tauri';

interface OfficeWindow {
  label: string;
  officeName: string;
  isOpen: boolean;
}

class WindowManager {
  private windows: Map<string, OfficeWindow> = new Map();

  /**
   * Open an office in a new Tauri window
   * If window already exists, focuses it instead of creating new one
   */
  async openOffice(officeName: string): Promise<void> {
    const label = `office-${officeName}`;

    // If window already open, focus it
    if (this.windows.has(label)) {
      console.log(`[WindowManager] Window already open for ${officeName}, focusing...`);
      try {
        await invoke('focus_window', { label });
        return;
      } catch (error) {
        console.error(`[WindowManager] Failed to focus window:`, error);
        // Window might have been closed - remove from tracking and try to open new one
        this.windows.delete(label);
      }
    }

    // Open new window
    console.log(`[WindowManager] Opening new window for ${officeName}...`);
    try {
      await invoke('open_office_window', { officeName });

      // Track the window
      this.windows.set(label, {
        label,
        officeName,
        isOpen: true
      });

      console.log(`[WindowManager] Successfully opened window for ${officeName}`);
    } catch (error) {
      console.error(`[WindowManager] Failed to open window:`, error);
      throw error;
    }
  }

  /**
   * Close an office window
   */
  closeOffice(officeName: string): void {
    const label = `office-${officeName}`;
    this.windows.delete(label);
    console.log(`[WindowManager] Closed window tracking for ${officeName}`);
  }

  /**
   * Check if an office window is currently open
   */
  isOpen(officeName: string): boolean {
    const label = `office-${officeName}`;
    return this.windows.has(label);
  }

  /**
   * Get all currently tracked windows
   */
  getOpenWindows(): OfficeWindow[] {
    return Array.from(this.windows.values());
  }

  /**
   * Close all office windows
   */
  closeAll(): void {
    console.log(`[WindowManager] Closing all ${this.windows.size} tracked windows`);
    this.windows.clear();
  }
}

// Singleton instance
export const windowManager = new WindowManager();

// Listen for window close events (if Tauri provides them)
// This would allow us to clean up our tracking when windows are closed manually
if (typeof window !== 'undefined' && 'addEventListener' in window) {
  window.addEventListener('beforeunload', () => {
    windowManager.closeAll();
  });
}
