/**
 * XBlackBox Tauri Viewer - Tauri API Wrapper
 * This module wraps Tauri's invoke API to match the original fetch-based API
 */

// Check if we're running in Tauri
const isTauri = window.__TAURI__ !== undefined;
// Helper function to validate JSON content-type
// Accepts 'application/json' with or without charset (e.g., 'application/json; charset=utf-8')
function validateJsonResponse(response) {
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.toLowerCase().includes('application/json')) {
        throw new Error('Server returned an invalid response format');
    }
}

// Tauri API wrapper
const tauriApi = isTauri ? {
    async invoke(cmd, args = {}) {
        try {
            // Use the public invoke API. Avoid internal `core.invoke` which may behave differently
            // across platforms or versions.
            return await window.__TAURI__.invoke(cmd, args);
        } catch (error) {
            // Handle Tauri invoke errors properly
            console.error(`Tauri invoke error for ${cmd}:`, error);
            
            // Check if error is an object with a message
            if (typeof error === 'object' && error !== null) {
                throw new Error(error.message || JSON.stringify(error));
            }
            throw error;
        }
    },
    
    async openDialog() {
        const { open } = window.__TAURI__.dialog;
        const res = await open({
            multiple: false,
            filters: [{
                name: 'XDR Files',
                extensions: ['xdr']
            }]
        });

        // Tauri may return a string or an array depending on options/platform.
        // Normalize to a single string path (take the first entry if array).
        if (Array.isArray(res)) {
            return res.length > 0 ? res[0] : null;
        }
        return res;
    },
    
    async getLogPath() {
        try {
            return await window.__TAURI__.invoke('get_log_path');
        } catch (error) {
            console.error('Failed to get log path:', error);
            return null;
        }
    }
} : null;

// Safe wrapper to set native window theme. This centralizes platform differences
// and prevents runtime errors when the API is unavailable.
if (isTauri && typeof tauriApi === 'object' && tauriApi !== null) {
    tauriApi.setWindowTheme = async function(theme) {
        try {
            if (window.__TAURI__ && window.__TAURI__.window) {
                const getter = window.__TAURI__.window.getCurrentWindow;
                if (typeof getter === 'function') {
                    const win = getter();
                    if (win && typeof win.setTheme === 'function') {
                        return await win.setTheme(theme);
                    }
                }
            }
        } catch (err) {
            console.warn('Failed to set native window theme via tauri:', err);
        }
        // no-op fallback
        return null;
    };
}

// API Functions adapted for Tauri
const api = {
    async uploadFile(file) {
        // In Tauri, we use native file dialogs instead of file upload
        // Guide users to use the "Open File" button which triggers the file dialog
        if (isTauri) {
            console.warn('File upload not supported in Tauri. Please use the "Open File" button to select a file.');
            return { error: 'Please use the "Open File" button to select files' };
        }
        // Web mode fallback
        throw new Error('File upload not implemented in web mode.');
    },

    async loadFile(path) {
        if (isTauri) {
            try {
                const result = await tauriApi.invoke('load_file', { filepath: path });

                // Handle different response types from Tauri
                if (result === null || result === undefined) {
                    throw new Error('No response received from Tauri backend');
                }

                // If result is a string, it might be an error message
                if (typeof result === 'string') {
                    throw new Error(result);
                }

                // Validate response structure
                if (typeof result !== 'object') {
                    throw new Error('Invalid response from server: expected object, got ' + typeof result);
                }

                // Check if result has expected properties
                if (result.success === undefined) {
                    throw new Error('Invalid response structure: missing success property');
                }

                return result;
            } catch (error) {
                console.error('Load file error:', error);

                // Enhanced error handling for Tauri-specific errors
                let errorMessage = error.message || 'Unknown error occurred while loading file';

                // Handle Tauri-specific error formats
                if (errorMessage.includes('<!DOCTYPE')) {
                    errorMessage = 'Server returned HTML instead of JSON. Please check server configuration.';
                } else if (errorMessage.includes('Unexpected token')) {
                    errorMessage = 'Invalid response format from server. Please try again.';
                }

                return {
                    success: false,
                    error: errorMessage
                };
            }
        } else {
            const response = await fetch('/api/load', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filepath: path })
            });

            validateJsonResponse(response);
            return response.json();
        }
    },

    async getData(params, downsample = 1, timeRange = null) {
        if (isTauri) {
            try {
                const result = await tauriApi.invoke('get_data', {
                    request: {
                        parameters: params,
                        downsample,
                        time_range: timeRange
                    }
                });
                
                if (typeof result !== 'object' || result === null) {
                    throw new Error('Invalid response from server');
                }
                
                return result;
            } catch (error) {
                console.error('Get data error:', error);
                return { error: error.message || 'Failed to retrieve data' };
            }
        } else {
            const response = await fetch('/api/data', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    parameters: params, 
                    downsample,
                    time_range: timeRange 
                })
            });
            
            validateJsonResponse(response);
            return response.json();
        }
    },

    async getStatistics(params) {
        if (isTauri) {
            return await tauriApi.invoke('get_statistics', {
                request: {
                    parameters: params
                }
            });
        } else {
            const response = await fetch('/api/statistics', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ parameters: params })
            });
            return response.json();
        }
    },

    async analyzeFlight() {
        if (isTauri) {
            return await tauriApi.invoke('analyze_flight');
        } else {
            const response = await fetch('/api/analyze-flight');
            return response.json();
        }
    },

    async getCorrelation(params) {
        if (isTauri) {
            return await tauriApi.invoke('get_correlation', {
                request: {
                    parameters: params
                }
            });
        } else {
            const response = await fetch('/api/correlation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ parameters: params })
            });
            return response.json();
        }
    },

    async get3DPath() {
        if (isTauri) {
            return await tauriApi.invoke('get_flight_path');
        } else {
            const response = await fetch('/api/flight-path');
            return response.json();
        }
    },

    async getTableData(start, count) {
        if (isTauri) {
            return await tauriApi.invoke('get_table_data', {
                request: {
                    start,
                    count
                }
            });
        } else {
            const response = await fetch('/api/table', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start, count })
            });
            return response.json();
        }
    },

    async openFileDialog() {
        if (isTauri) {
            return await tauriApi.openDialog();
        } else {
            // In web mode, use the file input
            return null;
        }
    },
    
    async getLogPath() {
        if (isTauri) {
            return await tauriApi.getLogPath();
        } else {
            return null;
        }
    }
};

// Export for use in main app
window.xdrApi = api;
// keep legacy global name `api` for older code that expects it
window.api = api;
window.isTauri = isTauri;
