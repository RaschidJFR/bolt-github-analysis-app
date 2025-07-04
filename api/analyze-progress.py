import json
import time
import urllib.parse
import csv
import io
import base64
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
            
            # Generate CSV data
            csv_data = self.generate_mock_csv_data(url)
            csv_b64 = base64.b64encode(csv_data.encode('utf-8')).decode('utf-8')
            
            # Send completion event with CSV data
            completion_data = {
                "type": "complete",
                "message": "Analysis completed successfully!",
                "timestamp": time.time(),
                "csv_data": csv_b64,
                "filename": "repository-analysis.csv"
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
    
    def generate_mock_csv_data(self, repo_url):
        """Generate mock CSV data for the repository analysis"""
        
        # Extract repository info from URL
        repo_parts = repo_url.rstrip('/').split('/')
        repo_name = repo_parts[-1] if repo_parts else 'unknown'
        owner = repo_parts[-2] if len(repo_parts) > 1 else 'unknown'
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Metric', 'Value', 'Description'])
        
        # Write mock data
        mock_data = [
            ['Repository Name', repo_name, 'Name of the analyzed repository'],
            ['Owner', owner, 'Repository owner/organization'],
            ['Total Files', '156', 'Total number of files in the repository'],
            ['Lines of Code', '12,847', 'Total lines of code (excluding comments and blank lines)'],
            ['Primary Language', 'JavaScript', 'Most used programming language'],
            ['Languages Used', 'JavaScript, TypeScript, CSS, HTML', 'All programming languages detected'],
            ['Dependencies', '23', 'Number of external dependencies'],
            ['Dev Dependencies', '15', 'Number of development dependencies'],
            ['Commits', '89', 'Total number of commits'],
            ['Contributors', '4', 'Number of unique contributors'],
            ['Last Updated', '2024-01-15', 'Date of last commit'],
            ['Repository Size', '2.3 MB', 'Total repository size'],
            ['Open Issues', '7', 'Number of open issues'],
            ['Stars', '42', 'Number of stars'],
            ['Forks', '12', 'Number of forks'],
            ['License', 'MIT', 'Repository license'],
            ['README Present', 'Yes', 'Whether README file exists'],
            ['Package Manager', 'npm', 'Package manager used'],
            ['CI/CD', 'GitHub Actions', 'Continuous integration setup'],
            ['Code Quality Score', '8.5/10', 'Overall code quality assessment'],
            ['Security Score', '9.2/10', 'Security vulnerability assessment'],
            ['Maintainability', 'High', 'Code maintainability rating'],
            ['Documentation Coverage', '78%', 'Percentage of documented code'],
            ['Test Coverage', '85%', 'Percentage of code covered by tests'],
            ['Complexity Score', 'Medium', 'Code complexity assessment']
        ]
        
        for row in mock_data:
            writer.writerow(row)
        
        # Add file structure section
        writer.writerow([])  # Empty row for spacing
        writer.writerow(['File Structure', '', ''])
        writer.writerow(['Path', 'Type', 'Size (bytes)'])
        
        file_structure = [
            ['src/', 'directory', ''],
            ['src/components/', 'directory', ''],
            ['src/components/App.tsx', 'file', '2,456'],
            ['src/components/Header.tsx', 'file', '1,234'],
            ['src/utils/', 'directory', ''],
            ['src/utils/helpers.ts', 'file', '987'],
            ['package.json', 'file', '1,567'],
            ['README.md', 'file', '3,421'],
            ['tsconfig.json', 'file', '456'],
            ['.gitignore', 'file', '234']
        ]
        
        for file_info in file_structure:
            writer.writerow(file_info)
        
        return output.getvalue()