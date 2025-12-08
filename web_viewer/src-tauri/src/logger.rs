use chrono::Local;
use std::fs::{self, File, OpenOptions};
use std::io::Write;
use std::path::PathBuf;
use std::sync::Mutex;

/// Logger for XBlackBox application
/// Stores logs in the user's home directory under .xblackbox/logs/
pub struct AppLogger {
    log_file: Mutex<Option<File>>,
    log_path: PathBuf,
}

impl AppLogger {
    /// Create a new logger instance
    /// Logs are stored in ~/.xblackbox/logs/xblackbox_YYYYMMDD.log
    pub fn new() -> Result<Self, std::io::Error> {
        let log_dir = Self::get_log_directory()?;
        
        // Create log directory if it doesn't exist
        fs::create_dir_all(&log_dir)?;
        
        // Create log file with current date
        let log_filename = format!("xblackbox_{}.log", Local::now().format("%Y%m%d"));
        let log_path = log_dir.join(log_filename);
        
        let log_file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&log_path)?;
        
        let logger = AppLogger {
            log_file: Mutex::new(Some(log_file)),
            log_path: log_path.clone(),
        };
        
        // Log startup message
        logger.log_info("XBlackBox Viewer started");
        logger.log_info(&format!("Log file: {}", log_path.display()));
        
        // Perform log rotation
        Self::rotate_logs(&log_dir)?;
        
        Ok(logger)
    }
    
    /// Get the log directory path
    fn get_log_directory() -> Result<PathBuf, std::io::Error> {
        let home_dir = dirs::home_dir()
            .ok_or_else(|| std::io::Error::new(
                std::io::ErrorKind::NotFound,
                "Could not find home directory"
            ))?;
        
        Ok(home_dir.join(".xblackbox").join("logs"))
    }
    
    /// Rotate logs - keep only last 30 days of logs
    fn rotate_logs(log_dir: &PathBuf) -> Result<(), std::io::Error> {
        let entries = fs::read_dir(log_dir)?;
        let mut log_files: Vec<(PathBuf, std::time::SystemTime)> = Vec::new();
        
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_file() && path.extension().map_or(false, |ext| ext == "log") {
                if let Ok(metadata) = entry.metadata() {
                    if let Ok(modified) = metadata.modified() {
                        log_files.push((path, modified));
                    }
                }
            }
        }
        
        // Sort by modification time (newest first)
        log_files.sort_by(|a, b| b.1.cmp(&a.1));
        
        // Keep only the 30 most recent log files
        for (path, _) in log_files.iter().skip(30) {
            let _ = fs::remove_file(path);
        }
        
        Ok(())
    }
    
    /// Write a log entry with the given level
    fn write_log(&self, level: &str, message: &str) {
        let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S%.3f");
        let log_entry = format!("[{}] [{}] {}\n", timestamp, level, message);
        
        if let Ok(mut file_guard) = self.log_file.lock() {
            if let Some(ref mut file) = *file_guard {
                let _ = file.write_all(log_entry.as_bytes());
                let _ = file.flush();
            }
        }
    }
    
    /// Log an info message
    pub fn log_info(&self, message: &str) {
        self.write_log("INFO", message);
    }
    
    /// Log a warning message
    pub fn log_warning(&self, message: &str) {
        self.write_log("WARN", message);
    }
    
    /// Log an error message
    pub fn log_error(&self, message: &str) {
        self.write_log("ERROR", message);
    }
    
    /// Log a debug message
    pub fn log_debug(&self, message: &str) {
        self.write_log("DEBUG", message);
    }
    
    /// Get the log file path
    pub fn get_log_path(&self) -> String {
        self.log_path.to_string_lossy().to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_logger_creation() {
        let logger = AppLogger::new();
        assert!(logger.is_ok());
    }
    
    #[test]
    fn test_logging() {
        let logger = AppLogger::new().unwrap();
        logger.log_info("Test info message");
        logger.log_warning("Test warning message");
        logger.log_error("Test error message");
        logger.log_debug("Test debug message");
    }
}
