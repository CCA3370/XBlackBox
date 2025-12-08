/**
 * XBlackBox Web Viewer - Main Application JavaScript
 */

// Global State
const state = {
    fileLoaded: false,
    header: null,
    parameters: [],
    selectedParams: [],
    currentPage: 1,
    pageSize: 100,
    theme: 'dark',
    timeRange: { start: 0, end: 0, max: 0 },
    colors: [
        '#0d7377', '#ff6b6b', '#4ecdc4', '#ffe66d', '#a8e6cf',
        '#ff8b94', '#6c5ce7', '#fd79a8', '#00b894', '#fdcb6e',
        '#e17055', '#74b9ff', '#00cec9', '#e84393', '#55efc4'
    ]
};

// API Functions - use the Tauri-compatible API from tauri-api.js
const api = window.xdrApi || {
    // Fallback API for direct web mode (should not be used in Tauri)
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch('/api/upload', { method: 'POST', body: formData });
        return response.json();
    },

    async loadFile(path) {
        const response = await fetch('/api/load', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filepath: path })
        });
        return response.json();
    },

    async getData(params, downsample = 1, timeRange = null) {
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
    },

    async getStatistics(params) {
        const response = await fetch('/api/statistics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ parameters: params })
        });
        return response.json();
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
        const response = await fetch('/api/correlation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ parameters: params })
        });
        return response.json();
    },

    async get3DPath() {
        const response = await fetch('/api/flight-path');
        return response.json();
    },

    async getTableData(start, count) {
        const response = await fetch('/api/table', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start, count })
        });
        return response.json();
    },

    async openFileDialog() {
        return null;
    }
};


// Error types for better messaging
const ErrorTypes = {
    FILE_TYPE: 'file_type',
    FILE_EMPTY: 'file_empty',
    FILE_TOO_LARGE: 'file_too_large',
    PARSE_ERROR: 'parse_error',
    NETWORK_ERROR: 'network_error',
    SERVER_ERROR: 'server_error',
    INVALID_FORMAT: 'invalid_format',
    NO_DATA: 'no_data',
    UNKNOWN: 'unknown'
};

const ErrorMessages = {
    [ErrorTypes.FILE_TYPE]: {
        title: 'Invalid File Type',
        message: 'Please select a valid XDR file. Only .xdr files are supported.',
        icon: 'fa-file-excel'
    },
    [ErrorTypes.FILE_EMPTY]: {
        title: 'Empty File',
        message: 'The selected file is empty. Please choose a valid XDR file.',
        icon: 'fa-file'
    },
    [ErrorTypes.FILE_TOO_LARGE]: {
        title: 'File Too Large',
        message: 'The file is too large to process. Maximum file size is 500MB.',
        icon: 'fa-weight-hanging'
    },
    [ErrorTypes.PARSE_ERROR]: {
        title: 'Parse Error',
        message: 'Failed to parse the XDR file. The file may be corrupted or in an unsupported format.',
        icon: 'fa-exclamation-triangle'
    },
    [ErrorTypes.NETWORK_ERROR]: {
        title: 'Network Error',
        message: 'Failed to connect to the server. Please check your connection and try again.',
        icon: 'fa-wifi'
    },
    [ErrorTypes.SERVER_ERROR]: {
        title: 'Server Error',
        message: 'The server encountered an error while processing your request.',
        icon: 'fa-server'
    },
    [ErrorTypes.INVALID_FORMAT]: {
        title: 'Invalid XDR Format',
        message: 'The file does not contain valid XDR data. Expected XFDR magic header.',
        icon: 'fa-file-code'
    },
    [ErrorTypes.NO_DATA]: {
        title: 'No Data Found',
        message: 'The file contains no data frames. Please select a file with recorded data.',
        icon: 'fa-database'
    },
    [ErrorTypes.UNKNOWN]: {
        title: 'Unknown Error',
        message: 'An unexpected error occurred. Please try again.',
        icon: 'fa-question-circle'
    }
};

// UI Functions
const ui = {
    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loading');
        overlay.querySelector('span').textContent = message;
        overlay.classList.remove('hidden');
    },

    hideLoading() {
        document.getElementById('loading').classList.add('hidden');
    },

    showModal(modalId) {
        document.getElementById(modalId).classList.add('active');
    },

    hideModal(modalId) {
        document.getElementById(modalId).classList.remove('active');
    },

    // Toast notification system
    showToast(message, type = 'info', duration = 5000) {
        const container = document.getElementById('toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-times-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        toast.innerHTML = `
            <i class="fas ${icons[type] || icons.info}"></i>
            <span class="toast-message">${message}</span>
            <button class="toast-close"><i class="fas fa-times"></i></button>
        `;
        
        container.appendChild(toast);
        
        // Animate in
        requestAnimationFrame(() => toast.classList.add('show'));
        
        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        });
        
        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
        
        return toast;
    },

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
        return container;
    },

    // Error dialog for detailed errors
    showError(errorType, details = '') {
        const errorInfo = ErrorMessages[errorType] || ErrorMessages[ErrorTypes.UNKNOWN];
        
        // Create error modal if not exists
        let errorModal = document.getElementById('error-modal');
        if (!errorModal) {
            errorModal = document.createElement('div');
            errorModal.id = 'error-modal';
            errorModal.className = 'modal';
            errorModal.innerHTML = `
                <div class="modal-content error-modal-content">
                    <div class="error-icon"><i class="fas fa-exclamation-circle"></i></div>
                    <h3 class="error-title"></h3>
                    <p class="error-message"></p>
                    <p class="error-details"></p>
                    <button class="btn btn-primary error-close">OK</button>
                </div>
            `;
            document.body.appendChild(errorModal);
            
            errorModal.querySelector('.error-close').addEventListener('click', () => {
                errorModal.classList.remove('active');
            });
            
            errorModal.addEventListener('click', (e) => {
                if (e.target === errorModal) {
                    errorModal.classList.remove('active');
                }
            });
        }
        
        errorModal.querySelector('.error-icon i').className = `fas ${errorInfo.icon}`;
        errorModal.querySelector('.error-title').textContent = errorInfo.title;
        errorModal.querySelector('.error-message').textContent = errorInfo.message;
        errorModal.querySelector('.error-details').textContent = details ? `Details: ${details}` : '';
        errorModal.querySelector('.error-details').style.display = details ? 'block' : 'none';
        
        errorModal.classList.add('active');
    },

    updateStatus(message, type = 'normal') {
        const statusEl = document.getElementById('status-message');
        statusEl.textContent = message;
        statusEl.className = `status-${type}`;
    },

    updateSelectionCount() {
        document.getElementById('status-selection').textContent = 
            `${state.selectedParams.length} parameters selected`;
    },

    updateFileInfo(header, frameCount) {
        if (!header) {
            document.querySelector('.info-placeholder').classList.remove('hidden');
            document.getElementById('file-details').classList.add('hidden');
            return;
        }

        document.querySelector('.info-placeholder').classList.add('hidden');
        document.getElementById('file-details').classList.remove('hidden');

        document.getElementById('info-filename').textContent = header.magic || 'XDR';
        document.getElementById('info-version').textContent = header.version || 'N/A';
        document.getElementById('info-level').textContent = header.level_name || 'N/A';
        document.getElementById('info-interval').textContent = `${(header.interval * 1000).toFixed(1)} ms`;
        document.getElementById('info-start').textContent = header.start_datetime?.split('T')[0] || 'N/A';
        
        const duration = header.duration || (frameCount * header.interval);
        const mins = Math.floor(duration / 60);
        const secs = (duration % 60).toFixed(1);
        document.getElementById('info-duration').textContent = `${mins}:${secs.padStart(4, '0')}`;
        document.getElementById('info-frames').textContent = frameCount?.toLocaleString() || 'N/A';
        document.getElementById('info-params').textContent = header.dataref_count || 'N/A';
        
        // Display airport information (Version 2+)
        const airportInfo = document.getElementById('airport-info');
        if (header.version >= 2 && (header.departure_airport || header.arrival_airport)) {
            airportInfo.classList.remove('hidden');
            
            // Format departure airport
            if (header.departure_airport && header.departure_airport.valid) {
                const dep = header.departure_airport;
                document.getElementById('info-departure').textContent = 
                    `${dep.icao} - ${dep.name}`;
                document.getElementById('info-departure').title = 
                    `${dep.icao}: ${dep.name}\nCoordinates: ${dep.lat.toFixed(4)}, ${dep.lon.toFixed(4)}`;
            } else {
                document.getElementById('info-departure').textContent = 'Not detected';
                document.getElementById('info-departure').title = 'Aircraft was not near any airport';
            }
            
            // Format arrival airport
            if (header.arrival_airport && header.arrival_airport.valid) {
                const arr = header.arrival_airport;
                document.getElementById('info-arrival').textContent = 
                    `${arr.icao} - ${arr.name}`;
                document.getElementById('info-arrival').title = 
                    `${arr.icao}: ${arr.name}\nCoordinates: ${arr.lat.toFixed(4)}, ${arr.lon.toFixed(4)}`;
            } else {
                document.getElementById('info-arrival').textContent = 'Not detected';
                document.getElementById('info-arrival').title = 'Aircraft was not near any airport';
            }
        } else {
            airportInfo.classList.add('hidden');
        }
    },

    enableButtons() {
        document.getElementById('btn-export').disabled = false;
        document.getElementById('btn-refresh').disabled = false;
        document.getElementById('btn-clear').disabled = false;
    }
};

// Parameter List Functions
function renderParameterList(filter = '') {
    const listEl = document.getElementById('param-list');
    const filterLower = filter.toLowerCase();
    const filteredParams = state.parameters.filter(p => 
        p.name.toLowerCase().includes(filterLower)
    );

    if (filteredParams.length === 0) {
        listEl.innerHTML = `<div class="param-placeholder">
            ${filter ? 'No matching parameters' : 'Load a file to see parameters'}
        </div>`;
        return;
    }

    listEl.innerHTML = filteredParams.map((param, idx) => {
        const colorIdx = state.parameters.indexOf(param) % state.colors.length;
        const isSelected = state.selectedParams.includes(param);
        const animDelay = Math.min(idx * 30, 300); // Staggered animation, max 300ms
        return `
            <div class="param-item ${isSelected ? 'selected' : ''}" data-index="${state.parameters.indexOf(param)}" style="animation-delay: ${animDelay}ms;">
                <input type="checkbox" ${isSelected ? 'checked' : ''}>
                <span class="param-name" title="${param.name}">${param.name}</span>
                <div class="param-color" style="background-color: ${state.colors[colorIdx]}"></div>
            </div>
        `;
    }).join('');
    
    // Trigger animation by adding a class
    listEl.querySelectorAll('.param-item').forEach(item => {
        item.classList.add('animate-in');
    });

    // Add click event to items
    listEl.querySelectorAll('.param-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (e.target.type === 'checkbox') return;
            const idx = parseInt(item.dataset.index);
            toggleParam(idx);
        });
        
        item.querySelector('input[type="checkbox"]').addEventListener('change', (e) => {
            const idx = parseInt(item.dataset.index);
            toggleParam(idx);
        });
    });
}

function toggleParam(idx) {
    const param = state.parameters[idx];
    const existingIdx = state.selectedParams.findIndex(p => 
        p.index === param.index && p.array_index === param.array_index
    );
    
    if (existingIdx >= 0) {
        state.selectedParams.splice(existingIdx, 1);
    } else {
        state.selectedParams.push(param);
    }
    
    renderParameterList(document.getElementById('param-search').value);
    ui.updateSelectionCount();
    updateFFTSelect();
}

function selectAllParams() {
    const filter = document.getElementById('param-search').value.toLowerCase();
    state.selectedParams = state.parameters.filter(p => 
        p.name.toLowerCase().includes(filter)
    );
    renderParameterList(filter);
    ui.updateSelectionCount();
}

function clearAllParams() {
    state.selectedParams = [];
    renderParameterList(document.getElementById('param-search').value);
    ui.updateSelectionCount();
}

// Flight Analysis Functions
async function loadFlightAnalysis() {
    const container = document.getElementById('flight-analysis-results');
    
    if (!state.fileLoaded) {
        container.innerHTML = `
            <div class="plot-placeholder">
                <i class="fas fa-plane-departure"></i>
                <p>Load a file first to analyze flight data</p>
            </div>
        `;
        return;
    }

    ui.showLoading('Analyzing flight phases...');

    try {
        const result = await api.analyzeFlight();
        
        if (result.error) {
            throw new Error(result.error);
        }

        let html = '<div class="analysis-summary">';
        html += '<h4><i class="fas fa-info-circle"></i> Flight Summary</h4>';
        html += '<div class="stats-grid">';
        html += `<div class="stat-item">
            <span class="stat-label">Total Flight Time</span>
            <span class="stat-value">${(result.total_flight_time / 60).toFixed(1)} min</span>
        </div>`;
        html += `<div class="stat-item">
            <span class="stat-label">Max Altitude</span>
            <span class="stat-value">${result.max_altitude.toFixed(0)} ft</span>
        </div>`;
        html += `<div class="stat-item">
            <span class="stat-label">Max Speed</span>
            <span class="stat-value">${result.max_speed.toFixed(1)} kts</span>
        </div>`;
        
        if (result.max_climb_rate) {
            html += `<div class="stat-item">
                <span class="stat-label">Max Climb Rate</span>
                <span class="stat-value">${result.max_climb_rate.toFixed(0)} fpm</span>
            </div>`;
        }
        
        if (result.max_descent_rate) {
            html += `<div class="stat-item">
                <span class="stat-label">Max Descent Rate</span>
                <span class="stat-value">${result.max_descent_rate.toFixed(0)} fpm</span>
            </div>`;
        }
        
        if (result.average_fuel_flow) {
            html += `<div class="stat-item">
                <span class="stat-label">Avg Fuel Flow</span>
                <span class="stat-value">${result.average_fuel_flow.toFixed(2)} lbs/hr</span>
            </div>`;
        }
        
        if (result.landing_g_force) {
            const gColor = result.landing_g_force > 2.0 ? 'color: #ff6b6b;' : '';
            html += `<div class="stat-item">
                <span class="stat-label">Landing G-Force</span>
                <span class="stat-value" style="${gColor}">${result.landing_g_force.toFixed(2)}G</span>
            </div>`;
        }
        
        html += '</div></div>';

        // Approach Analysis
        if (result.approach_analysis) {
            const approach = result.approach_analysis;
            const stableClass = approach.stable_approach ? 'stable' : 'unstable';
            html += '<div class="analysis-section approach-analysis">';
            html += '<h4><i class="fas fa-plane-arrival"></i> Approach Analysis</h4>';
            html += '<div class="approach-stats">';
            html += `<div class="approach-item">
                <span class="approach-label">Approach Stability:</span>
                <span class="approach-value ${stableClass}">
                    ${approach.stable_approach ? '✓ Stable' : '⚠ Unstable'}
                </span>
            </div>`;
            html += `<div class="approach-item">
                <span class="approach-label">Avg Descent Rate:</span>
                <span class="approach-value">${Math.abs(approach.average_descent_rate).toFixed(0)} fpm</span>
            </div>`;
            html += `<div class="approach-item">
                <span class="approach-label">Touchdown Speed:</span>
                <span class="approach-value">${approach.touchdown_speed.toFixed(1)} kts</span>
            </div>`;
            html += '</div></div>';
        }

        // Flight Phases
        if (result.phases && result.phases.length > 0) {
            html += '<div class="analysis-phases">';
            html += '<h4><i class="fas fa-list"></i> Flight Phases</h4>';
            html += '<table class="phases-table">';
            html += '<thead><tr><th>Phase</th><th>Start Time</th><th>Duration</th></tr></thead>';
            html += '<tbody>';
            
            result.phases.forEach(phase => {
                const startMin = (phase.start_time / 60).toFixed(1);
                const durationSec = phase.duration.toFixed(0);
                html += `<tr>
                    <td><strong>${phase.name}</strong></td>
                    <td>${startMin} min</td>
                    <td>${durationSec}s</td>
                </tr>`;
            });
            
            html += '</tbody></table>';
            html += '</div>';
        }

        // Anomalies
        if (result.anomalies && result.anomalies.length > 0) {
            html += '<div class="analysis-section anomalies-section">';
            html += '<h4><i class="fas fa-exclamation-triangle"></i> Detected Anomalies</h4>';
            html += '<div class="anomalies-list">';
            
            result.anomalies.forEach(anomaly => {
                const severityClass = `severity-${anomaly.severity}`;
                const timeMin = (anomaly.timestamp / 60).toFixed(1);
                html += `<div class="anomaly-item ${severityClass}">
                    <div class="anomaly-header">
                        <span class="anomaly-severity">${anomaly.severity.toUpperCase()}</span>
                        <span class="anomaly-time">${timeMin} min</span>
                    </div>
                    <div class="anomaly-desc">${anomaly.description}</div>
                    <div class="anomaly-detail">${anomaly.parameter}: ${anomaly.value.toFixed(1)}</div>
                </div>`;
            });
            
            html += '</div></div>';
        }

        container.innerHTML = html;
    } catch (error) {
        console.error('Flight analysis error:', error);
        container.innerHTML = `
            <div class="plot-placeholder">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Analysis error: ${error.message}</p>
            </div>
        `;
    } finally {
        ui.hideLoading();
    }
}

// Plotting Functions (using Plotly)
// Performance thresholds for rendering optimization
const PLOT_PERF_THRESHOLDS = {
    LARGE_DATASET: 10000,    // Switch to WebGL rendering
    DOWNSAMPLE_MIN: 20000,   // Start downsampling
    DOWNSAMPLE_MAX: 50000,   // Aggressive downsampling
    ANIMATION_LIMIT: 20000   // Disable animations
};

async function updatePlot() {
    const container = document.getElementById('main-plot');
    
    if (state.selectedParams.length === 0) {
        container.innerHTML = `
            <div class="plot-placeholder">
                <i class="fas fa-chart-area"></i>
                <p>Select parameters and click Update Plot</p>
            </div>
        `;
        return;
    }

    ui.showLoading('Loading data...');

    try {
        // Smart downsampling based on data size
        const frameCount = state.header?.frame_count || 10000;
        let downsample = 1;
        
        // Optimize rendering for large datasets
        if (frameCount > PLOT_PERF_THRESHOLDS.DOWNSAMPLE_MAX) {
            downsample = Math.ceil(frameCount / 10000); // Keep ~10k points max
        } else if (frameCount > PLOT_PERF_THRESHOLDS.DOWNSAMPLE_MIN) {
            downsample = Math.ceil(frameCount / 15000); // Keep ~15k points
        }
        
        console.log(`Data points: ${frameCount}, Downsampling: ${downsample}x`);
        
        // Get time range from sliders
        const timeRange = (state.timeRange.start !== 0 || state.timeRange.end !== state.timeRange.max) 
            ? [state.timeRange.start, state.timeRange.end] 
            : null;
        
        const data = await api.getData(state.selectedParams, downsample, timeRange);
        
        if (data.error) {
            throw new Error(data.error);
        }

        const traces = [];
        
        for (const [name, paramData] of Object.entries(data)) {
            const colorIdx = state.parameters.findIndex(p => p.name === name) % state.colors.length;
            traces.push({
                x: paramData.timestamps,
                y: paramData.values,
                name: name,
                type: frameCount > PLOT_PERF_THRESHOLDS.LARGE_DATASET ? 'scattergl' : 'scatter', // Use WebGL for large datasets
                mode: 'lines',
                line: { 
                    color: state.colors[colorIdx], 
                    width: frameCount > PLOT_PERF_THRESHOLDS.LARGE_DATASET ? 1 : 1.5 
                }
            });
        }

        const showGrid = document.getElementById('opt-grid').checked;
        
        const layout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: getComputedStyle(document.body).getPropertyValue('--text-primary') },
            xaxis: {
                title: 'Time (s)',
                showgrid: showGrid,
                gridcolor: getComputedStyle(document.body).getPropertyValue('--border-color'),
                color: getComputedStyle(document.body).getPropertyValue('--text-secondary'),
                zeroline: false
            },
            yaxis: {
                title: 'Value',
                showgrid: showGrid,
                gridcolor: getComputedStyle(document.body).getPropertyValue('--border-color'),
                color: getComputedStyle(document.body).getPropertyValue('--text-secondary'),
                zeroline: false
            },
            legend: {
                orientation: 'h',
                y: -0.15
            },
            margin: { l: 60, r: 30, t: 30, b: 60 },
            hovermode: 'x unified'
        };

        // Add animation configuration for smooth chart rendering
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            toImageButtonOptions: {
                format: 'png',
                filename: 'xblackbox_plot',
                height: 800,
                width: 1200
            }
        };

        // Create plot with animation
        await Plotly.newPlot(container, traces, layout, config);
        
        // Animate traces appearing
        Plotly.animate(container, {
            data: traces,
            traces: traces.map((_, i) => i),
            layout: {}
        }, {
            transition: {
                duration: 500,
                easing: 'cubic-in-out'
            },
            frame: {
                duration: 500
            }
        });

        ui.updateStatus(`Plotted ${state.selectedParams.length} parameter(s)`);
    } catch (error) {
        console.error('Plot error:', error);
        container.innerHTML = `
            <div class="plot-placeholder">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Plot error: ${error.message}</p>
            </div>
        `;
    } finally {
        ui.hideLoading();
    }
}

function clearPlot() {
    const container = document.getElementById('main-plot');
    container.innerHTML = `
        <div class="plot-placeholder">
            <i class="fas fa-chart-area"></i>
            <p>Select parameters and click Update Plot</p>
        </div>
    `;
}

// Statistics Functions
async function loadStatistics() {
    const container = document.getElementById('stats-body');
    
    if (state.selectedParams.length === 0) {
        container.innerHTML = `<tr><td colspan="8" style="text-align:center">Select parameters first</td></tr>`;
        return;
    }

    ui.showLoading('Calculating statistics...');

    try {
        const result = await api.getStatistics(state.selectedParams);
        
        if (result.error) {
            throw new Error(result.error);
        }

        container.innerHTML = result.map(stats => `
            <tr>
                <td>${stats.name}</td>
                <td>${stats.count?.toLocaleString() || 'N/A'}</td>
                <td>${stats.min?.toFixed(4) ?? 'N/A'}</td>
                <td>${stats.max?.toFixed(4) ?? 'N/A'}</td>
                <td>${stats.mean?.toFixed(4) ?? 'N/A'}</td>
                <td>${stats.median?.toFixed(4) ?? 'N/A'}</td>
                <td>${stats.std?.toFixed(4) ?? 'N/A'}</td>
                <td>${stats.range?.toFixed(4) ?? 'N/A'}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Statistics error:', error);
        container.innerHTML = `<tr><td colspan="8" style="text-align:center">Error: ${error.message}</td></tr>`;
    } finally {
        ui.hideLoading();
    }
}

// Correlation Functions
async function loadCorrelation() {
    const container = document.getElementById('corr-plot');
    
    if (state.selectedParams.length < 2) {
        container.innerHTML = `
            <div class="plot-placeholder">
                <i class="fas fa-th"></i>
                <p>Select at least 2 parameters to analyze correlations</p>
            </div>
        `;
        return;
    }

    ui.showLoading('Calculating correlation...');

    try {
        const result = await api.getCorrelation(state.selectedParams);
        
        if (result.error) {
            throw new Error(result.error);
        }

        const trace = {
            z: result.matrix,
            x: result.names,
            y: result.names,
            type: 'heatmap',
            colorscale: [
                [0, '#ff6b6b'],
                [0.5, '#ffffff'],
                [1, '#0d7377']
            ],
            zmin: -1,
            zmax: 1,
            showscale: true
        };

        const layout = {
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: getComputedStyle(document.body).getPropertyValue('--text-primary') },
            margin: { l: 120, r: 30, t: 30, b: 120 },
            xaxis: { tickangle: -45 },
            annotations: [],
            transition: {
                duration: 600,
                easing: 'cubic-in-out'
            }
        };

        // Add text annotations
        for (let i = 0; i < result.matrix.length; i++) {
            for (let j = 0; j < result.matrix[i].length; j++) {
                layout.annotations.push({
                    x: result.names[j],
                    y: result.names[i],
                    text: result.matrix[i][j].toFixed(2),
                    showarrow: false,
                    font: { color: Math.abs(result.matrix[i][j]) > 0.5 ? 'white' : 'black', size: 10 }
                });
            }
        }

        Plotly.newPlot(container, [trace], layout, { responsive: true });
    } catch (error) {
        console.error('Correlation error:', error);
        container.innerHTML = `
            <div class="plot-placeholder">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Correlation error: ${error.message}</p>
            </div>
        `;
    } finally {
        ui.hideLoading();
    }
}

// 3D Flight Path Functions
async function load3DPath() {
    const container = document.getElementById('flight-plot');

    ui.showLoading('Loading 3D flight path...');

    try {
        const result = await api.get3DPath();
        
        if (result.error) {
            throw new Error(result.error);
        }

        if (!result.latitudes || result.latitudes.length === 0) {
            throw new Error('No position data available');
        }

        const colorByAlt = document.getElementById('opt-color-altitude').checked;
        const showMarkers = document.getElementById('opt-show-markers').checked;
        
        // Optimize for large datasets
        const dataSize = result.latitudes.length;
        const useMarkers = showMarkers && dataSize < PLOT_PERF_THRESHOLDS.LARGE_DATASET;

        const trace = {
            x: result.longitudes,
            y: result.latitudes,
            z: result.altitudes,
            mode: useMarkers ? 'lines+markers' : 'lines',
            type: useMarkers ? 'scatter3d' : 'scatter3d',
            line: {
                width: dataSize > PLOT_PERF_THRESHOLDS.LARGE_DATASET ? 2 : 3,
                color: colorByAlt ? result.altitudes : state.colors[0],
                colorscale: colorByAlt ? 'Viridis' : undefined,
                showscale: colorByAlt,
                colorbar: colorByAlt ? {
                    title: 'Altitude (m)',
                    thickness: 15,
                    len: 0.5
                } : undefined
            },
            marker: useMarkers ? {
                size: 2,
                color: colorByAlt ? result.altitudes : state.colors[0],
                colorscale: 'Viridis'
            } : undefined,
            hovertemplate: '<b>Position</b><br>' +
                          'Lat: %{y:.4f}°<br>' +
                          'Lon: %{x:.4f}°<br>' +
                          'Alt: %{z:.0f} m<br>' +
                          '<extra></extra>'
        };

        const layout = {
            paper_bgcolor: 'transparent',
            font: { color: getComputedStyle(document.body).getPropertyValue('--text-primary') },
            scene: {
                xaxis: { 
                    title: 'Longitude', 
                    backgroundcolor: 'rgba(0,0,0,0)',
                    gridcolor: getComputedStyle(document.body).getPropertyValue('--border-color'),
                    showbackground: true
                },
                yaxis: { 
                    title: 'Latitude', 
                    backgroundcolor: 'rgba(0,0,0,0)',
                    gridcolor: getComputedStyle(document.body).getPropertyValue('--border-color'),
                    showbackground: true
                },
                zaxis: { 
                    title: 'Altitude (m)', 
                    backgroundcolor: 'rgba(0,0,0,0)',
                    gridcolor: getComputedStyle(document.body).getPropertyValue('--border-color'),
                    showbackground: true
                },
                bgcolor: 'transparent',
                camera: {
                    eye: { x: 1.5, y: 1.5, z: 1.2 },
                    center: { x: 0, y: 0, z: 0 }
                }
            },
            margin: { l: 0, r: 0, t: 30, b: 0 },
            showlegend: false
        };

        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            toImageButtonOptions: {
                format: 'png',
                filename: 'flight_path_3d',
                height: 800,
                width: 1200
            }
        };

        await Plotly.newPlot(container, [trace], layout, config);
        
        // Animate camera for 3D effect (only for smaller datasets)
        if (dataSize < PLOT_PERF_THRESHOLDS.ANIMATION_LIMIT) {
            Plotly.animate(container, {
                layout: {
                    scene: {
                        camera: {
                            eye: { x: 1.2, y: 1.2, z: 1.0 }
                        }
                    }
                }
            }, {
                transition: {
                    duration: 1000,
                    easing: 'cubic-in-out'
                },
                frame: {
                    duration: 1000
                }
            });
        }

        // Update stats
        const altMin = Math.min(...result.altitudes);
        const altMax = Math.max(...result.altitudes);
        const distanceKm = calculatePathDistance(result.latitudes, result.longitudes);
        
        document.getElementById('flight-stats').innerHTML = 
            `<b>Data points:</b> ${result.latitudes.length.toLocaleString()} | 
             <b>Altitude range:</b> ${altMin.toFixed(0)} - ${altMax.toFixed(0)} m | 
             <b>Distance:</b> ${distanceKm.toFixed(1)} km`;

    } catch (error) {
        console.error('3D path error:', error);
        container.innerHTML = `
            <div class="plot-placeholder">
                <i class="fas fa-exclamation-triangle"></i>
                <p>3D path error: ${error.message}</p>
            </div>
        `;
    } finally {
        ui.hideLoading();
    }
}

// Helper function to calculate path distance
function calculatePathDistance(lats, lons) {
    if (lats.length < 2) return 0;
    
    let totalDistance = 0;
    for (let i = 1; i < lats.length; i++) {
        const lat1 = lats[i-1] * Math.PI / 180;
        const lat2 = lats[i] * Math.PI / 180;
        const dLat = lat2 - lat1;
        const dLon = (lons[i] - lons[i-1]) * Math.PI / 180;
        
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                 Math.cos(lat1) * Math.cos(lat2) *
                 Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        totalDistance += 6371 * c; // Earth radius in km
    }
    
    return totalDistance;
}

// Data Table Functions
async function loadDataTable() {
    const container = document.getElementById('table-body');
    
    ui.showLoading('Loading data table...');

    try {
        const start = (state.currentPage - 1) * state.pageSize;
        const result = await api.getTableData(start, state.pageSize);
        
        if (result.error) {
            throw new Error(result.error);
        }

        // Build header
        const thead = document.getElementById('table-head');
        thead.innerHTML = `<tr>${result.headers.map(h => `<th>${h}</th>`).join('')}</tr>`;

        // Build body
        container.innerHTML = result.rows.map(row => {
            let cells = `<td>${row.index}</td><td>${row.timestamp.toFixed(3)}</td>`;
            cells += row.values.map(v => `<td>${typeof v === 'number' ? v.toFixed(4) : v}</td>`).join('');
            return `<tr>${cells}</tr>`;
        }).join('');

        // Update pagination
        const totalPages = Math.ceil(result.total / state.pageSize);
        document.getElementById('page-info').textContent = `Page ${state.currentPage} of ${totalPages}`;
        document.getElementById('btn-prev-page').disabled = state.currentPage <= 1;
        document.getElementById('btn-next-page').disabled = state.currentPage >= totalPages;

    } catch (error) {
        console.error('Data table error:', error);
        container.innerHTML = `<tr><td colspan="10" style="text-align:center">Error: ${error.message}</td></tr>`;
    } finally {
        ui.hideLoading();
    }
}

function nextPage() {
    state.currentPage++;
    loadDataTable();
}

function prevPage() {
    if (state.currentPage > 1) {
        state.currentPage--;
        loadDataTable();
    }
}

// File Validation
function validateFile(file) {
    // Check if file exists
    if (!file) {
        return { valid: false, errorType: ErrorTypes.FILE_EMPTY };
    }
    
    // Check file extension
    const fileName = file.name.toLowerCase();
    if (!fileName.endsWith('.xdr')) {
        return { 
            valid: false, 
            errorType: ErrorTypes.FILE_TYPE,
            details: `File "${file.name}" is not an XDR file`
        };
    }
    
    // Check file size (max 500MB)
    const maxSize = 500 * 1024 * 1024;
    if (file.size > maxSize) {
        return { 
            valid: false, 
            errorType: ErrorTypes.FILE_TOO_LARGE,
            details: `File size: ${(file.size / 1024 / 1024).toFixed(2)} MB`
        };
    }
    
    // Check if file is empty
    if (file.size === 0) {
        return { valid: false, errorType: ErrorTypes.FILE_EMPTY };
    }
    
    return { valid: true };
}

// Parse server error response
function parseServerError(error, response) {
    const errorMsg = error?.message?.toLowerCase() || '';
    
    if (errorMsg.includes('xfdr') || errorMsg.includes('magic') || errorMsg.includes('invalid file format')) {
        return { errorType: ErrorTypes.INVALID_FORMAT, details: error.message };
    }
    
    if (errorMsg.includes('parse') || errorMsg.includes('struct') || errorMsg.includes('unpack')) {
        return { errorType: ErrorTypes.PARSE_ERROR, details: error.message };
    }
    
    if (errorMsg.includes('no data') || errorMsg.includes('no frames') || errorMsg.includes('empty')) {
        return { errorType: ErrorTypes.NO_DATA, details: error.message };
    }
    
    if (errorMsg.includes('network') || errorMsg.includes('fetch') || errorMsg.includes('connection')) {
        return { errorType: ErrorTypes.NETWORK_ERROR, details: error.message };
    }
    
    return { errorType: ErrorTypes.SERVER_ERROR, details: error.message };
}

// Time Range Initialization
function initializeTimeRange(header, frameCount) {
    const maxTime = header.duration || (frameCount * header.interval);
    state.timeRange.max = maxTime;
    state.timeRange.start = 0;
    state.timeRange.end = maxTime;
    
    const timeStartSlider = document.getElementById('time-start-slider');
    const timeEndSlider = document.getElementById('time-end-slider');
    
    if (timeStartSlider && timeEndSlider) {
        timeStartSlider.max = maxTime;
        timeStartSlider.value = 0;
        timeEndSlider.max = maxTime;
        timeEndSlider.value = maxTime;
        
        document.getElementById('time-start-value').textContent = '0.0s';
        document.getElementById('time-end-value').textContent = maxTime.toFixed(1) + 's';
    }
}

// File Handling
async function handleFileUpload(file) {
    // Validate file first
    const validation = validateFile(file);
    if (!validation.valid) {
        ui.showError(validation.errorType, validation.details);
        return;
    }
    
    ui.showLoading('Loading file...');
    ui.updateStatus('Uploading file...', 'loading');

    try {
        const result = await api.uploadFile(file);
        
        if (result.error) {
            const errorInfo = parseServerError({ message: result.error });
            throw { ...errorInfo, originalMessage: result.error };
        }

        // Validate response data
        if (!result.header) {
            throw { errorType: ErrorTypes.PARSE_ERROR, details: 'No header information received' };
        }
        
        if (!result.frame_count || result.frame_count === 0) {
            ui.showToast('Warning: File contains no data frames', 'warning');
        }

        // Store data
        state.header = result.header;
        state.parameters = result.parameters || [];
        state.selectedParams = [];
        state.fileLoaded = true;

        // Initialize time range
        initializeTimeRange(result.header, result.frame_count);

        // Update UI
        ui.updateFileInfo(result.header, result.frame_count);
        renderParameterList();
        ui.updateSelectionCount();
        ui.enableButtons();
        ui.hideModal('file-modal');
        ui.updateStatus(`Loaded: ${file.name}`, 'success');
        ui.showToast(`Successfully loaded ${file.name}`, 'success');

        // Load table data
        loadDataTable();

    } catch (error) {
        console.error('File load error:', error);
        ui.updateStatus('Load failed', 'error');
        
        if (error.errorType) {
            ui.showError(error.errorType, error.details || error.originalMessage);
        } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
            ui.showError(ErrorTypes.NETWORK_ERROR, 'Cannot connect to server');
        } else {
            ui.showError(ErrorTypes.UNKNOWN, error.message);
        }
    } finally {
        ui.hideLoading();
    }
}

async function handlePathLoad(path) {
    // Validate path
    if (!path || path.trim() === '') {
        ui.showToast('Please enter a file path', 'warning');
        return;
    }
    
    if (!path.toLowerCase().endsWith('.xdr')) {
        ui.showError(ErrorTypes.FILE_TYPE, `Path "${path}" does not point to an XDR file`);
        return;
    }
    
    ui.showLoading('Loading file...');
    ui.updateStatus('Loading file...', 'loading');

    try {
        const result = await api.loadFile(path);
        
        if (result.error) {
            const errorInfo = parseServerError({ message: result.error });
            throw { ...errorInfo, originalMessage: result.error };
        }

        // Validate response data
        if (!result.header) {
            throw { errorType: ErrorTypes.PARSE_ERROR, details: 'No header information received' };
        }
        
        if (!result.frame_count || result.frame_count === 0) {
            ui.showToast('Warning: File contains no data frames', 'warning');
        }

        // Store data
        state.header = result.header;
        state.parameters = result.parameters || [];
        state.selectedParams = [];
        state.fileLoaded = true;

        // Initialize time range
        initializeTimeRange(result.header, result.frame_count);

        // Update UI
        ui.updateFileInfo(result.header, result.frame_count);
        renderParameterList();
        ui.updateSelectionCount();
        ui.enableButtons();
        ui.hideModal('file-modal');
        
        const fileName = path.split(/[\\/]/).pop();
        ui.updateStatus(`Loaded: ${fileName}`, 'success');
        ui.showToast(`Successfully loaded ${fileName}`, 'success');

        // Load table data
        loadDataTable();

    } catch (error) {
        console.error('File load error:', error);
        ui.updateStatus('Load failed', 'error');
        
        if (error.errorType) {
            ui.showError(error.errorType, error.details || error.originalMessage);
        } else if (error.message?.includes('not found') || error.message?.includes('404')) {
            ui.showError(ErrorTypes.UNKNOWN, `File not found: ${path}`);
        } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
            ui.showError(ErrorTypes.NETWORK_ERROR, 'Cannot connect to server');
        } else {
            ui.showError(ErrorTypes.UNKNOWN, error.message);
        }
    } finally {
        ui.hideLoading();
    }
}

// Theme Toggle
function toggleTheme() {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    document.body.setAttribute('data-theme', state.theme);
    localStorage.setItem('theme', state.theme);
    
    const icon = document.querySelector('#btn-theme i');
    icon.className = state.theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
}

// Tab Switching
function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
    
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    document.getElementById(`tab-${tabId}`).classList.add('active');
}

// CSV Export
function exportCSV() {
    window.location.href = '/api/export-csv';
}

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    state.theme = savedTheme;
    document.body.setAttribute('data-theme', savedTheme);
    document.querySelector('#btn-theme i').className = savedTheme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';

    // Modal controls - Top bar Open button
    document.getElementById('btn-open').addEventListener('click', async () => {
        if (window.isTauri) {
            // Use Tauri file dialog
            try {
                const filePath = await api.openFileDialog();
                if (filePath) {
                    await handlePathLoad(filePath);
                }
            } catch (error) {
                console.error('Error opening file dialog:', error);
                ui.showError(error.message || 'Failed to open file dialog');
            }
        } else {
            // Use modal for web mode
            ui.showModal('file-modal');
        }
    });
    document.getElementById('close-modal').addEventListener('click', () => ui.hideModal('file-modal'));

    // File Info Panel click - only works when no file is loaded
    const fileInfoPanel = document.getElementById('file-info');
    const infoPlaceholder = fileInfoPanel.querySelector('.info-placeholder');
    
    if (infoPlaceholder) {
        infoPlaceholder.style.cursor = 'pointer';
        infoPlaceholder.addEventListener('click', () => {
            // Only trigger modal if no file is loaded
            if (!state.fileLoaded) {
                ui.showModal('file-modal');
            }
        });
    }

    // File input handler
    document.getElementById('file-input').addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleFileUpload(file);
    });

    document.getElementById('btn-browse').addEventListener('click', () => {
        document.getElementById('file-input').click();
    });

    // Drop zone handlers (in modal)
    const dropZone = document.getElementById('drop-zone');
    
    if (dropZone) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file) handleFileUpload(file);
        });
    }

    // Global drag & drop - only process file, don't auto-open modal
    // Prevent default drag behaviors on whole page
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        document.body.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    // Show visual feedback when dragging over page (but don't open modal)
    ['dragenter', 'dragover'].forEach(eventName => {
        document.body.addEventListener(eventName, () => {
            document.body.classList.add('drag-active');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        document.body.addEventListener(eventName, () => {
            document.body.classList.remove('drag-active');
        }, false);
    });

    // Handle file drop on body - directly upload without opening modal
    document.body.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        document.body.classList.remove('drag-active');
        const file = e.dataTransfer.files[0];
        if (file) {
            // Let handleFileUpload do the validation
            handleFileUpload(file);
        }
    }, false);

    // Path load button
    document.getElementById('btn-load-path').addEventListener('click', () => {
        const path = document.getElementById('file-path').value.trim();
        if (path) handlePathLoad(path);
    });

    // Parameter controls
    document.getElementById('param-search').addEventListener('input', (e) => {
        renderParameterList(e.target.value);
    });

    document.getElementById('btn-select-all').addEventListener('click', selectAllParams);
    document.getElementById('btn-clear-selection').addEventListener('click', clearAllParams);

    // Tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    // Theme toggle
    document.getElementById('btn-theme').addEventListener('click', toggleTheme);

    // Plot controls
    document.getElementById('btn-update-plot').addEventListener('click', updatePlot);
    document.getElementById('btn-refresh').addEventListener('click', updatePlot);
    document.getElementById('btn-clear').addEventListener('click', clearPlot);

    // Time range sliders
    const timeStartSlider = document.getElementById('time-start-slider');
    const timeEndSlider = document.getElementById('time-end-slider');
    const timeStartValue = document.getElementById('time-start-value');
    const timeEndValue = document.getElementById('time-end-value');

    function updateTimeRangeDisplay() {
        timeStartValue.textContent = state.timeRange.start.toFixed(1) + 's';
        timeEndValue.textContent = state.timeRange.end.toFixed(1) + 's';
    }

    timeStartSlider.addEventListener('input', (e) => {
        const startValue = parseFloat(e.target.value);
        const endValue = parseFloat(timeEndSlider.value);
        const minGap = Math.max(0.1, state.timeRange.max * 0.001); // Minimum 0.1s or 0.1% of total
        
        // Ensure start is always less than end with minimum gap
        if (startValue >= endValue) {
            e.target.value = Math.max(0, endValue - minGap);
        }
        
        state.timeRange.start = parseFloat(e.target.value);
        updateTimeRangeDisplay();
    });

    timeEndSlider.addEventListener('input', (e) => {
        const startValue = parseFloat(timeStartSlider.value);
        const endValue = parseFloat(e.target.value);
        const minGap = Math.max(0.1, state.timeRange.max * 0.001); // Minimum 0.1s or 0.1% of total
        
        // Ensure end is always greater than start with minimum gap
        if (endValue <= startValue) {
            e.target.value = Math.min(state.timeRange.max, startValue + minGap);
        }
        
        state.timeRange.end = parseFloat(e.target.value);
        updateTimeRangeDisplay();
    });

    document.getElementById('btn-reset-time').addEventListener('click', () => {
        timeStartSlider.value = 0;
        timeEndSlider.value = state.timeRange.max;
        state.timeRange.start = 0;
        state.timeRange.end = state.timeRange.max;
        updateTimeRangeDisplay();
    });

    // Statistics
    document.getElementById('btn-calc-stats').addEventListener('click', loadStatistics);

    // Flight Analysis
    document.getElementById('btn-analyze-flight').addEventListener('click', loadFlightAnalysis);

    // Correlation
    document.getElementById('btn-calc-corr').addEventListener('click', loadCorrelation);

    // 3D Flight Path
    document.getElementById('btn-update-flight').addEventListener('click', load3DPath);

    // Export
    document.getElementById('btn-export').addEventListener('click', exportCSV);

    // Data table pagination
    document.getElementById('btn-prev-page').addEventListener('click', prevPage);
    document.getElementById('btn-next-page').addEventListener('click', nextPage);
    document.getElementById('table-page-size').addEventListener('change', (e) => {
        state.pageSize = parseInt(e.target.value);
        state.currentPage = 1;
        if (state.fileLoaded) loadDataTable();
    });

    // Panel collapse functionality
    document.querySelectorAll('.panel-header').forEach(header => {
        header.addEventListener('click', (e) => {
            // Don't collapse if clicking on the info placeholder
            if (e.target.closest('.info-placeholder')) {
                return;
            }
            const panel = header.closest('.panel');
            panel.classList.toggle('collapsed');
            
            // Save collapse state
            const panelId = panel.id || panel.className.split(' ')[1];
            if (panelId) {
                const isCollapsed = panel.classList.contains('collapsed');
                localStorage.setItem(`panel-${panelId}-collapsed`, isCollapsed);
            }
        });
    });

    // Restore panel collapse states
    document.querySelectorAll('.panel').forEach(panel => {
        const panelId = panel.id || panel.className.split(' ')[1];
        if (panelId) {
            const isCollapsed = localStorage.getItem(`panel-${panelId}-collapsed`) === 'true';
            if (isCollapsed) {
                panel.classList.add('collapsed');
            }
        }
    });

    // Close modals on backdrop click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });

    // Initial UI state
    ui.updateStatus('Ready');
});
