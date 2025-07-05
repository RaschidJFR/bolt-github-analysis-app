// Repository Analyzer - Frontend JavaScript

class RepositoryAnalyzer {
    constructor() {
        this.url = '';
        this.isValid = false;
        this.error = '';
        this.isLoading = false;
        this.progress = [];
        this.eventSource = null;
        
        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        this.urlInput = document.getElementById('github-url');
        this.urlStatus = document.getElementById('url-status');
        this.errorMessage = document.getElementById('error-message');
        this.errorText = document.getElementById('error-text');
        this.analyzeBtn = document.getElementById('analyze-btn');
        this.progressContainer = document.getElementById('progress-container');
        this.progressList = document.getElementById('progress-list');
        this.progressSpinner = document.querySelector('#progress-container svg.animate-spin');
    }

    bindEvents() {
        this.urlInput.addEventListener('input', (e) => this.handleUrlChange(e));
        this.analyzeBtn.addEventListener('click', () => this.handleAnalyze());
        
        // Enable input on page load
        this.urlInput.disabled = false;
    }

    validateGitHubUrl(url) {
        const githubRegex = /^https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9._-]+\/[a-zA-Z0-9._-]+\/?$/;
        return githubRegex.test(url);
    }

    handleUrlChange(e) {
        const newUrl = e.target.value;
        this.url = newUrl;
        
        if (newUrl.trim() === '') {
            this.setValid(false);
            this.setError('');
            return;
        }
        
        if (this.validateGitHubUrl(newUrl)) {
            this.setValid(true);
            this.setError('');
        } else {
            this.setValid(false);
            this.setError('Please enter a valid GitHub repository URL (e.g., https://github.com/username/repository)');
        }
    }

    setValid(isValid) {
        this.isValid = isValid;
        this.updateUrlStatus();
        this.updateAnalyzeButton();
    }

    setError(error) {
        this.error = error;
        this.updateErrorDisplay();
    }

    updateUrlStatus() {
        this.urlStatus.innerHTML = '';
        this.urlStatus.classList.remove('hidden');
        
        if (this.isValid) {
            this.urlStatus.innerHTML = `
                <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
            `;
            this.urlInput.classList.remove('border-red-300', 'focus:border-red-500');
            this.urlInput.classList.add('border-green-300', 'focus:border-green-500');
        } else if (this.error) {
            this.urlStatus.innerHTML = `
                <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
            `;
            this.urlInput.classList.remove('border-green-300', 'focus:border-green-500');
            this.urlInput.classList.add('border-red-300', 'focus:border-red-500');
        } else {
            this.urlStatus.classList.add('hidden');
            this.urlInput.classList.remove('border-red-300', 'focus:border-red-500', 'border-green-300', 'focus:border-green-500');
            this.urlInput.classList.add('border-gray-300', 'focus:border-blue-500');
        }
    }

    updateErrorDisplay() {
        if (this.error) {
            this.errorText.textContent = this.error;
            this.errorMessage.classList.remove('hidden');
        } else {
            this.errorMessage.classList.add('hidden');
        }
    }

    updateAnalyzeButton() {
        if (this.isValid && !this.isLoading) {
            this.analyzeBtn.disabled = false;
            this.analyzeBtn.classList.remove('bg-gray-300', 'cursor-not-allowed');
            this.analyzeBtn.classList.add('bg-blue-600', 'hover:bg-blue-700', 'hover:scale-105', 'shadow-lg', 'hover:shadow-xl', 'btn-enabled');
        } else {
            this.analyzeBtn.disabled = true;
            this.analyzeBtn.classList.remove('bg-blue-600', 'hover:bg-blue-700', 'hover:scale-105', 'shadow-lg', 'hover:shadow-xl', 'btn-enabled');
            this.analyzeBtn.classList.add('bg-gray-300', 'cursor-not-allowed');
        }
    }

    downloadCSV(csvData, filename) {
        // Decode base64 CSV data
        const decodedData = atob(csvData);
        const blob = new Blob([decodedData], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Clean up the URL object
        window.URL.revokeObjectURL(url);
    }

    async handleAnalyze() {
        if (!this.isValid || !this.url.trim()) return;

        // Reset form state when starting new analysis
        this.isLoading = true;
        this.progress = [];
        this.setError('');
        this.updateLoadingState();
        this.updateAnalyzeButton();
        this.updateProgressDisplay();
        this.startProgressSpinner();
        
        try {
            // Start SSE connection for progress updates
            const es = new EventSource(`/api/analyze?url=${encodeURIComponent(this.url)}`);
            this.eventSource = es;
            
            es.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'progress') {
                    this.progress.push({
                        message: data.message,
                        timestamp: new Date().toLocaleTimeString()
                    });
                    this.updateProgressDisplay();
                } else if (data.type === 'complete') {
                    // Analysis complete, download CSV from base64 data
                    if (data.csv_data && data.filename) {
                        this.downloadCSV(data.csv_data, data.filename);
                    }
                    
                    // Add completion message to progress
                    this.progress.push({
                        message: '✅ Analysis complete! Your CSV file will download automatically.',
                        timestamp: new Date().toLocaleTimeString()
                    });
                    this.updateProgressDisplay();
                    
                    // Stop loading and update UI
                    this.isLoading = false;
                    this.updateLoadingState();
                    this.updateAnalyzeButton();
                    this.stopProgressSpinner();
                    es.close();
                    this.eventSource = null;
                } else if (data.type === 'error') {
                    this.setError(data.message || 'An error occurred during analysis.');
                    this.isLoading = false;
                    this.updateLoadingState();
                    this.updateAnalyzeButton();
                    this.stopProgressSpinner();
                    es.close();
                    this.eventSource = null;
                }
            };
            
            es.onerror = (error) => {
                console.error('SSE error:', error);
                this.isLoading = false;
                this.setError('An error occurred during analysis. Please try again.');
                this.updateLoadingState();
                this.updateAnalyzeButton();
                this.stopProgressSpinner();
                es.close();
                this.eventSource = null;
            };
        } catch (error) {
            console.error('Analysis error:', error);
            this.isLoading = false;
            this.setError('An error occurred during analysis. Please try again.');
            this.updateLoadingState();
            this.updateAnalyzeButton();
            this.stopProgressSpinner();
        }
    }

    updateProgressDisplay() {
        if (this.progress.length > 0) {
            this.progressContainer.classList.remove('hidden');
            this.progressList.innerHTML = this.progress.map((update, index) => `
                <div class="flex items-center justify-between text-sm bg-white rounded-lg p-3 shadow-sm">
                    <span class="text-gray-700">${update.message}</span>
                    <span class="text-gray-500 text-xs">${update.timestamp}</span>
                </div>
            `).join('');
        } else {
            this.progressContainer.classList.add('hidden');
        }
    }

    startProgressSpinner() {
        if (this.progressSpinner) {
            this.progressSpinner.classList.add('animate-spin');
        }
    }

    stopProgressSpinner() {
        if (this.progressSpinner) {
            this.progressSpinner.classList.remove('animate-spin');
        }
    }

    updateLoadingState() {
        if (this.isLoading) {
            this.analyzeBtn.innerHTML = `
                <span class="flex items-center justify-center space-x-2">
                    <svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                    </svg>
                    <span>Analyzing...</span>
                </span>
            `;
        } else {
            this.analyzeBtn.innerHTML = `
                <span class="flex items-center justify-center space-x-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                    </svg>
                    <span>Analyze Repository</span>
                </span>
            `;
        }
    }

    // Cleanup on page unload
    cleanup() {
        if (this.eventSource) {
            this.eventSource.close();
        }
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new RepositoryAnalyzer();
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        app.cleanup();
    });
}); 