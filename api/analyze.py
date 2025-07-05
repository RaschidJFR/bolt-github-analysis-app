import json
import time
import urllib.parse
import base64
from http.server import BaseHTTPRequestHandler
from ghIssueAnalyzer import IssueAnalyzer, ChatGPT
import pandas as pd
from pydispatch import dispatcher
import os
from dotenv import load_dotenv
load_dotenv()

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Handle CORS preflight request
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        # Parse query parameters
        query_params = urllib.parse.parse_qs(self.path.split('?')[1] if '?' in self.path else '')
        url = query_params.get('url', [''])[0]
        
        if not url:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Missing URL parameter')
            return
        
        # Set headers for Server-Sent Events
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Keep the connection open for SSE
        self.close_connection = False
        
        try:
            
            # Extract repo name and owner from URL
            parsed_url = urllib.parse.urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            if len(path_parts) < 2:
                self.on_error("Invalid repository URL")
                return
            repo_owner = path_parts[0]
            repo_name = path_parts[1]
            if not repo_owner or not repo_name:
                self.on_error("Invalid repository URL")
                return
            
            # Initialize the IssueAnalyzer with the repository and API token
            if not os.getenv('GITHUB_TOKEN'):
                self.on_error("Missing GITHUB_TOKEN environment variable")
                return
            if not os.getenv('OPENAI_API_KEY'):
                self.on_error("Missing OPENAI_API_KEY environment variable")
            if not repo_name or not repo_owner:
                self.on_error("Invalid repository name or owner")
            agent = IssueAnalyzer(f"{repo_owner}/{repo_name}", os.getenv('GITHUB_TOKEN'), ChatGPT(os.getenv('OPENAI_API_KEY')))
            
            # Connect signals to handlers
            dispatcher.connect(
                self.on_progress_update,
                sender=agent,
                signal=IssueAnalyzer.Signals.PROGRESS_UPDATE)
            dispatcher.connect(
                self.on_completion,
                sender=agent,
                signal=IssueAnalyzer.Signals.TASK_COMPLETED)
            dispatcher.connect(
                self.on_error,
                sender=agent,
                signal=IssueAnalyzer.Signals.ERROR)
            
            # Start the analysis process
            agent.fetch_issues().analyze()
            
        except Exception as e:
            self.on_error(str(e))
    
    def on_progress_update(self, step: IssueAnalyzer.Steps, data={}):
        """Send a single SSE update"""
        message = "In progress..."
        
        if step==IssueAnalyzer.Steps.FETCHING_ISSUES:
            message = "🔍 Fetching repo issues (1/5)..."
        elif step==IssueAnalyzer.Steps.TRACTION_ANALYSIS_STARTED:
            message = "📣 Analyzing interactions (2/5)..."
        elif step==IssueAnalyzer.Steps.ISSUE_SUMMARIZATION_STARTED:
            message = "📖 Reading top issues (3/5)..."
        elif step==IssueAnalyzer.Steps.IMPACT_ANALYSIS_STARTED:
            message = "📊 Analyzing impact (4/5)..."
        elif step==IssueAnalyzer.Steps.SCORING_STARTED:
            message = "🏅 Ranking issues (5/5)..."
        
        event_data = {
            "type": "update",
            "message": message,
            "timestamp": time.time()
        }
        self.wfile.write(f"data: {json.dumps(event_data)}\n\n".encode())
        self.wfile.flush()
            
    def on_error(self, data="Unknown error"):
        """Send error event"""
        error_data = {
            "type": "error",
            "message": data,
            "timestamp": time.time()
        }
        self.wfile.write(f"data: {json.dumps(error_data)}\n\n".encode())
        self.wfile.flush()
        
    def on_completion(self, data: list[dict]=[]):
        """Send completion event with CSV data"""
        filename = "analysis.csv"
        csv_data = pd.DataFrame(data).to_csv(index=False)
        csv_b64 = base64.b64encode(csv_data.encode('utf-8')).decode('utf-8')
        
        completion_data = {
            "type": "complete",
            "message": "Analysis completed successfully!",
            "timestamp": time.time(),
            "csv_data": csv_b64,
            "filename": filename
        }
        
        self.wfile.write(f"data: {json.dumps(completion_data)}\n\n".encode())
        self.wfile.flush()