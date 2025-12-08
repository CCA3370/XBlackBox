use std::path::{Path, PathBuf};
use std::fs;

/// Maximum file size allowed (500MB)
const MAX_FILE_SIZE: u64 = 500 * 1024 * 1024;

/// Security validation errors
#[derive(Debug)]
pub enum SecurityError {
    InvalidPath(String),
    PathTraversal(String),
    FileTooBig(u64),
    FileNotFound(String),
    InvalidExtension(String),
    PermissionDenied(String),
}

impl std::fmt::Display for SecurityError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            SecurityError::InvalidPath(msg) => write!(f, "Invalid path: {}", msg),
            SecurityError::PathTraversal(msg) => write!(f, "Path traversal detected: {}", msg),
            SecurityError::FileTooBig(size) => write!(f, "File too large: {} bytes (max: {} bytes)", size, MAX_FILE_SIZE),
            SecurityError::FileNotFound(msg) => write!(f, "File not found: {}", msg),
            SecurityError::InvalidExtension(msg) => write!(f, "Invalid file extension: {}", msg),
            SecurityError::PermissionDenied(msg) => write!(f, "Permission denied: {}", msg),
        }
    }
}

impl std::error::Error for SecurityError {}

/// Validate and sanitize a file path for XDR file loading
pub fn validate_file_path(path_str: &str) -> Result<PathBuf, SecurityError> {
    // Check for empty path
    if path_str.trim().is_empty() {
        return Err(SecurityError::InvalidPath("Path cannot be empty".to_string()));
    }
    
    // Create path object
    let path = Path::new(path_str);
    
    // Canonicalize the path to resolve any symlinks and relative paths
    let canonical_path = path.canonicalize().map_err(|e| {
        match e.kind() {
            std::io::ErrorKind::NotFound => {
                SecurityError::FileNotFound(format!("File does not exist: {}", path_str))
            }
            std::io::ErrorKind::PermissionDenied => {
                SecurityError::PermissionDenied(format!("Cannot access file: {}", path_str))
            }
            _ => {
                SecurityError::InvalidPath(format!("Cannot resolve path: {}", e))
            }
        }
    })?;
    
    // Note: Canonicalization resolves all relative path components (including ..)
    // to absolute paths. The path is now safe from traversal attacks.
    // If additional directory restrictions are needed in the future, validate
    // that the canonical path is within allowed directories here.
    
    // Validate file extension
    match canonical_path.extension() {
        Some(ext) if ext.eq_ignore_ascii_case("xdr") => {},
        Some(ext) => {
            return Err(SecurityError::InvalidExtension(
                format!("Expected .xdr file, got .{}", ext.to_string_lossy())
            ));
        }
        None => {
            return Err(SecurityError::InvalidExtension(
                "File has no extension, expected .xdr".to_string()
            ));
        }
    }
    
    // Check file size
    let metadata = fs::metadata(&canonical_path).map_err(|e| {
        SecurityError::InvalidPath(format!("Cannot read file metadata: {}", e))
    })?;
    
    if !metadata.is_file() {
        return Err(SecurityError::InvalidPath(
            "Path does not point to a regular file".to_string()
        ));
    }
    
    let file_size = metadata.len();
    if file_size > MAX_FILE_SIZE {
        return Err(SecurityError::FileTooBig(file_size));
    }
    
    if file_size == 0 {
        return Err(SecurityError::InvalidPath(
            "File is empty".to_string()
        ));
    }
    
    Ok(canonical_path)
}

/// Sanitize error messages to prevent information leakage
pub fn sanitize_error_message(error: &str) -> String {
    // Remove full paths from error messages, keep only filename
    let sanitized = error.split(|c| c == '/' || c == '\\')
        .last()
        .unwrap_or(error);
    
    // Limit error message length
    if sanitized.len() > 200 {
        format!("{}...", &sanitized[..200])
    } else {
        sanitized.to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    use std::io::Write;
    
    #[test]
    fn test_empty_path() {
        let result = validate_file_path("");
        assert!(matches!(result, Err(SecurityError::InvalidPath(_))));
    }
    
    #[test]
    fn test_invalid_extension() {
        // This test requires an actual file, so we'll create a temp file
        let temp_dir = std::env::temp_dir();
        let test_file = temp_dir.join("test.txt");
        let _ = File::create(&test_file);
        
        let result = validate_file_path(test_file.to_str().unwrap());
        assert!(matches!(result, Err(SecurityError::InvalidExtension(_))));
        
        let _ = fs::remove_file(&test_file);
    }
    
    #[test]
    fn test_nonexistent_file() {
        let result = validate_file_path("/nonexistent/path/to/file.xdr");
        assert!(matches!(result, Err(SecurityError::FileNotFound(_))));
    }
    
    #[test]
    fn test_sanitize_error_message() {
        let error = "/home/user/secret/path/to/file.xdr: Permission denied";
        let sanitized = sanitize_error_message(error);
        assert!(!sanitized.contains("/home/user/secret"));
    }
}
