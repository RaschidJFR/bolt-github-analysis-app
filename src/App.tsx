import React, { useState, useEffect } from 'react';
import { Github, Download, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';

interface ProgressUpdate {
  message: string;
  timestamp: string;
}

function App() {
  const [url, setUrl] = useState('');
  const [isValid, setIsValid] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState<ProgressUpdate[]>([]);
  const [eventSource, setEventSource] = useState<EventSource | null>(null);

  // GitHub URL validation
  const validateGitHubUrl = (url: string): boolean => {
    const githubRegex = /^https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9._-]+\/[a-zA-Z0-9._-]+\/?$/;
    return githubRegex.test(url);
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newUrl = e.target.value;
    setUrl(newUrl);
    
    if (newUrl.trim() === '') {
      setIsValid(false);
      setError('');
      return;
    }
    
    if (validateGitHubUrl(newUrl)) {
      setIsValid(true);
      setError('');
    } else {
      setIsValid(false);
      setError('Please enter a valid GitHub repository URL (e.g., https://github.com/username/repository)');
    }
  };

  const handleAnalyze = async () => {
    if (!isValid || !url.trim()) return;

    // Reset form state when starting new analysis
    setIsLoading(true);
    setProgress([]);
    setError('');
    
    try {
      // Start SSE connection for progress updates
      const es = new EventSource(`/api/analyze-progress?url=${encodeURIComponent(url)}`);
      setEventSource(es);
      
      es.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'progress') {
          setProgress(prev => [...prev, {
            message: data.message,
            timestamp: new Date().toLocaleTimeString()
          }]);
        } else if (data.type === 'complete') {
          // Analysis complete, download CSV
          const downloadUrl = `/api/download-csv?url=${encodeURIComponent(url)}`;
          const link = document.createElement('a');
          link.href = downloadUrl;
          link.download = `analysis-${Date.now()}.csv`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          
          // Only stop loading, don't reset form
          setIsLoading(false);
          es.close();
          setEventSource(null);
        }
      };
      
      es.onerror = (error) => {
        console.error('SSE error:', error);
        setIsLoading(false);
        setError('An error occurred during analysis. Please try again.');
        es.close();
        setEventSource(null);
      };
    } catch (error) {
      console.error('Analysis error:', error);
      setIsLoading(false);
      setError('An error occurred during analysis. Please try again.');
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [eventSource]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-3">
            <Github className="w-12 h-12 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">
              Repository Analyzer
            </h1>
          </div>
          <p className="text-lg text-gray-600 max-w-lg mx-auto">
            Paste a GitHub repository URL below to analyze its structure, dependencies, and generate a comprehensive CSV report.
          </p>
        </div>

        {/* Main Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
          {/* URL Input */}
          <div className="space-y-3">
            <label htmlFor="github-url" className="block text-sm font-semibold text-gray-700">
              GitHub Repository URL
            </label>
            <div className="relative">
              <input
                id="github-url"
                type="text"
                value={url}
                onChange={handleUrlChange}
                placeholder="https://github.com/username/repository"
                className={`w-full px-4 py-3 border-2 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200 ${
                  error 
                    ? 'border-red-300 focus:border-red-500' 
                    : isValid 
                      ? 'border-green-300 focus:border-green-500' 
                      : 'border-gray-300 focus:border-blue-500'
                }`}
                disabled={isLoading}
              />
              {isValid && (
                <CheckCircle2 className="absolute right-3 top-3.5 w-5 h-5 text-green-500" />
              )}
              {error && (
                <AlertCircle className="absolute right-3 top-3.5 w-5 h-5 text-red-500" />
              )}
            </div>
            {error && (
              <p className="text-sm text-red-600 flex items-center space-x-1">
                <AlertCircle className="w-4 h-4" />
                <span>{error}</span>
              </p>
            )}
          </div>

          {/* Analyze Button */}
          <button
            onClick={handleAnalyze}
            disabled={!isValid || isLoading}
            className={`w-full py-3 px-6 rounded-xl font-semibold text-white transition-all duration-200 transform ${
              isValid && !isLoading
                ? 'bg-blue-600 hover:bg-blue-700 hover:scale-105 shadow-lg hover:shadow-xl'
                : 'bg-gray-300 cursor-not-allowed'
            }`}
          >
            {isLoading ? (
              <span className="flex items-center justify-center space-x-2">
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Analyzing...</span>
              </span>
            ) : (
              <span className="flex items-center justify-center space-x-2">
                <Download className="w-5 h-5" />
                <span>Analyze Repository</span>
              </span>
            )}
          </button>

          {/* Progress Updates */}
          {progress.length > 0 && (
            <div className="bg-gray-50 rounded-xl p-4 space-y-3">
              <h3 className="font-semibold text-gray-800 flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                <span>Analysis Progress</span>
              </h3>
              <div className="space-y-2">
                {progress.map((update, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between text-sm bg-white rounded-lg p-3 shadow-sm"
                  >
                    <span className="text-gray-700">{update.message}</span>
                    <span className="text-gray-500 text-xs">{update.timestamp}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Info Section */}
        <div className="text-center text-sm text-gray-500">
          <p>
            The analysis will generate a comprehensive CSV report containing repository metrics,
            file structure, dependencies, and code statistics.
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;