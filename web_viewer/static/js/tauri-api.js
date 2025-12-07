/**
 * XBlackBox Tauri Viewer - Tauri API Wrapper
 * This module wraps Tauri's invoke API to match the original fetch-based API
 */

// Check if we're running in Tauri
const isTauri = window.__TAURI__ !== undefined;

// Tauri API wrapper
const tauriApi = isTauri ? {
    async invoke(cmd, args = {}) {
        return window.__TAURI__.core.invoke(cmd, args);
    },
    
    async openDialog() {
        const { open } = window.__TAURI__.dialog;
        return await open({
            multiple: false,
            filters: [{
                name: 'XDR Files',
                extensions: ['xdr']
            }]
        });
    }
} : null;

// API Functions adapted for Tauri
const api = {
    async uploadFile(file) {
        // In Tauri, we use file paths instead of uploading
        // This is not directly supported - we need to use file dialog
        throw new Error('Direct file upload not supported in Tauri. Use the file dialog instead.');
    },

    async loadFile(path) {
        if (isTauri) {
            const result = await tauriApi.invoke('load_file', { filepath: path });
            return result;
        } else {
            const response = await fetch('/api/load', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filepath: path })
            });
            return response.json();
        }
    },

    async getData(params, downsample = 1, timeRange = null) {
        if (isTauri) {
            return await tauriApi.invoke('get_data', {
                request: {
                    parameters: params,
                    downsample,
                    time_range: timeRange
                }
            });
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

    async getFFT(param) {
        if (isTauri) {
            return await tauriApi.invoke('get_fft', {
                request: {
                    index: param.index,
                    array_index: param.array_index || 0
                }
            });
        } else {
            const response = await fetch('/api/fft', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ index: param.index, array_index: param.array_index || 0 })
            });
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
    }
};

// Export for use in main app
window.xdrApi = api;
window.isTauri = isTauri;
