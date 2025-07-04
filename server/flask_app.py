import json
import time
import urllib.parse
import csv
import io
import base64
from flask import Flask, request, Response, stream_template_string
import threading

app = Flask(__name__)

def generate_mock_csv_data(repo_url):
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

def generate_progress_events(url):
    """Generator function that yields Server-Sent Events for progress updates"""
    
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
            
            yield f"data: {json.dumps(event_data)}\n\n"
            
            # Simulate processing time
            time.sleep(step["delay"])
        
        # Generate CSV data
        csv_data = generate_mock_csv_data(url)
        csv_b64 = base64.b64encode(csv_data.encode('utf-8')).decode('utf-8')
        
        # Send completion event with CSV data
        completion_data = {
            "type": "complete",
            "message": "Analysis completed successfully!",
            "timestamp": time.time(),
            "csv_data": csv_b64,
            "filename": "repository-analysis.csv"
        }
        
        yield f"data: {json.dumps(completion_data)}\n\n"
        
    except Exception as e:
        error_data = {
            "type": "error",
            "message": f"Analysis failed: {str(e)}",
            "timestamp": time.time()
        }
        
        yield f"data: {json.dumps(error_data)}\n\n"

@app.route('/analyze', methods=['GET', 'OPTIONS'])
def analyze():
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    
    # Get URL parameter
    url = request.args.get('url')
    
    if not url:
        return 'Missing URL parameter', 400
    
    # Create Server-Sent Events response
    def event_stream():
        for event in generate_progress_events(url):
            yield event
    
    response = Response(event_stream(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    
    return response

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'message': 'Flask server is running'}

if __name__ == '__main__':
    print("Starting Flask development server...")
    print("Server will be available at: http://localhost:5000")
    print("Analyze endpoint: http://localhost:5000/analyze?url=<github_url>")
    print("Health check: http://localhost:5000/health")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)