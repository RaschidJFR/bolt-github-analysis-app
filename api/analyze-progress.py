import json
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler

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
        
        # Mock analysis process with progress updates
        progress_steps = [
            {"message": "🚀 Starting repository analysis...", "delay": 1},
            {"message": "📥 Cloning repository and scanning files...", "delay": 5},
            {"message": "🔍 Analyzing code structure and dependencies...", "delay": 4},
            {"message": "📊 Generating comprehensive report...", "delay": 3},
            {"message": "✅ Analysis complete! Preparing download...", "delay": 2}
        ]
        
        try:
            # Send progress updates
            for step in progress_steps:
                event_data = {
                    "type": "progress",
                    "message": step["message"],
                    "timestamp": time.time()
                }
                
                self.wfile.write(f"data: {json.dumps(event_data)}\n\n".encode())
                self.wfile.flush()
                
                # Simulate processing time
                time.sleep(step["delay"])
            
            # Send completion event
            completion_data = {
                "type": "complete",
                "message": "Analysis completed successfully!",
                "timestamp": time.time()
            }
            
            self.wfile.write(f"data: {json.dumps(completion_data)}\n\n".encode())
            self.wfile.flush()
            
            # Add small delay to allow client to process the completion event
            time.sleep(0.1)
            
        except Exception as e:
            error_data = {
                "type": "error",
                "message": f"Analysis failed: {str(e)}",
                "timestamp": time.time()
            }
            
            self.wfile.write(f"data: {json.dumps(error_data)}\n\n".encode())
            self.wfile.flush()