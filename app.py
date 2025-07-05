from flask import Flask, render_template, request, Response, jsonify
import json
import time
import urllib.parse
import base64
import os
from dotenv import load_dotenv
from ghIssueAnalyzer import IssueAnalyzer, ChatGPT
import pandas as pd
from pydispatch import dispatcher

load_dotenv()

app = Flask(__name__)

class AnalysisHandler:
    def __init__(self):
        self.progress_updates = []
        self.is_complete = False
        self.error = None
        self.csv_data = None
        self.filename = None

    def on_progress_update(self, step, data={}):
        """Handle progress updates from the analyzer"""
        message = "In progress..."
        
        if step == IssueAnalyzer.Steps.FETCHING_ISSUES:
            message = "🔍 Fetching repo issues (1/5)..."
        elif step == IssueAnalyzer.Steps.TRACTION_ANALYSIS_STARTED:
            message = "📣 Analyzing interactions (2/5)..."
        elif step == IssueAnalyzer.Steps.ISSUE_SUMMARIZATION_STARTED:
            message = "📖 Reading top issues (3/5)..."
        elif step == IssueAnalyzer.Steps.IMPACT_ANALYSIS_STARTED:
            message = "📊 Analyzing impact (4/5)..."
        elif step == IssueAnalyzer.Steps.SCORING_STARTED:
            message = "🏅 Ranking issues (5/5)..."
        
        self.progress_updates.append({
            "type": "progress",
            "message": message,
            "timestamp": time.time()
        })
    
    def on_error(self, data="Unknown error"):
        """Handle errors from the analyzer"""
        self.error = data
        self.progress_updates.append({
            "type": "error",
            "message": data,
            "timestamp": time.time()
        })
    
    def on_completion(self, data=[]):
        """Handle completion from the analyzer"""
        self.filename = "analysis.csv"
        csv_data = pd.DataFrame(data).to_csv(index=False)
        self.csv_data = base64.b64encode(csv_data.encode('utf-8')).decode('utf-8')
        self.is_complete = True
        self.progress_updates.append({
            "type": "complete",
            "message": "Analysis completed successfully!",
            "timestamp": time.time(),
            "csv_data": self.csv_data,
            "filename": self.filename
        })

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/api/analyze')
def analyze():
    """Handle repository analysis requests"""
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "Missing URL parameter"}), 400
    
    # Validate GitHub URL
    if not url.startswith('https://github.com/'):
        return jsonify({"error": "Please enter a valid GitHub repository URL"}), 400
    
    # Extract repo name and owner from URL
    parsed_url = urllib.parse.urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) < 2:
        return jsonify({"error": "Invalid repository URL"}), 400
    
    repo_owner = path_parts[0]
    repo_name = path_parts[1]
    
    if not repo_owner or not repo_name:
        return jsonify({"error": "Invalid repository name or owner"}), 400
    
    # Check for required environment variables
    if not os.getenv('GITHUB_TOKEN'):
        return jsonify({"error": "Missing GITHUB_TOKEN environment variable"}), 500
    
    if not os.getenv('OPENAI_API_KEY'):
        return jsonify({"error": "Missing OPENAI_API_KEY environment variable"}), 500
    
    def generate():
        """Generate Server-Sent Events for real-time updates"""
        handler = AnalysisHandler()
        
        try:
            # Initialize the IssueAnalyzer
            agent = IssueAnalyzer(
                f"{repo_owner}/{repo_name}", 
                os.getenv('GITHUB_TOKEN'), 
                ChatGPT(os.getenv('OPENAI_API_KEY'))
            )
            
            # Connect signals to handlers
            dispatcher.connect(
                handler.on_progress_update,
                sender=agent,
                signal=IssueAnalyzer.Signals.PROGRESS_UPDATE
            )
            dispatcher.connect(
                handler.on_completion,
                sender=agent,
                signal=IssueAnalyzer.Signals.TASK_COMPLETED
            )
            dispatcher.connect(
                handler.on_error,
                sender=agent,
                signal=IssueAnalyzer.Signals.ERROR
            )
            
            # Start the analysis process in a separate thread
            import threading
            def run_analysis():
                try:
                    agent.fetch_issues().analyze()
                except Exception as e:
                    handler.on_error(str(e))
            
            analysis_thread = threading.Thread(target=run_analysis)
            analysis_thread.start()
            
            # Send progress updates
            while not handler.is_complete and handler.error is None:
                if handler.progress_updates:
                    update = handler.progress_updates.pop(0)
                    yield f"data: {json.dumps(update)}\n\n"
                time.sleep(0.1)
            
            # Send final update
            if handler.error:
                yield f"data: {json.dumps({'type': 'error', 'message': handler.error})}\n\n"
            elif handler.is_complete:
                yield f"data: {json.dumps({'type': 'complete', 'csv_data': handler.csv_data, 'filename': handler.filename})}\n\n"
                
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True) 