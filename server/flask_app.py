import sys
import os
from flask import Flask, request, Response
from flask_cors import CORS

# Add the api directory to the Python path so we can import the module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))

# Import the handler class from analyze.py
from analyze_progress import handler

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class MockRequest:
    """Mock request object to simulate the request structure expected by the handler"""
    def __init__(self, path, method='GET'):
        self.path = path
        self.method = method

class MockResponse:
    """Mock response object to capture the handler's output"""
    def __init__(self):
        self.status_code = 200
        self.headers = {}
        self.body = b''
        
    def send_response(self, code):
        self.status_code = code
        
    def send_header(self, name, value):
        self.headers[name] = value
        
    def end_headers(self):
        pass
        
    def write(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.body += data
        
    def flush(self):
        pass

@app.route('/analyze', methods=['GET', 'OPTIONS'])
def analyze():
    """Analyze endpoint that uses the handler from analyze.py"""
    
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
    
    # Create a mock request object with the full path including query parameters
    mock_path = f"/analyze?url={url}"
    mock_request = MockRequest(mock_path)
    
    # Create handler instance and mock response
    handler_instance = handler()
    handler_instance.path = mock_path
    
    # Create a generator function that yields Server-Sent Events
    def event_stream():
        # Mock the wfile attribute to capture streaming output
        class StreamCapture:
            def __init__(self):
                self.buffer = []
                
            def write(self, data):
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                # Yield each SSE event as it's written
                if data.strip():
                    return data
                    
            def flush(self):
                pass
        
        # Replace the handler's wfile with our stream capture
        stream_capture = StreamCapture()
        handler_instance.wfile = stream_capture
        
        # Override the write method to yield data immediately
        original_write = stream_capture.write
        
        def streaming_write(data):
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            if data.strip():
                return data
            return None
        
        # Monkey patch the write method to yield data
        def patched_write(data):
            result = streaming_write(data)
            if result:
                return result
        
        # Create a custom wfile that yields data
        class YieldingWriter:
            def write(self, data):
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                return data
                
            def flush(self):
                pass
        
        yielding_writer = YieldingWriter()
        
        # Override handler methods to capture and yield output
        original_send_response = handler_instance.send_response
        original_send_header = handler_instance.send_header
        original_end_headers = handler_instance.end_headers
        
        def mock_send_response(code):
            pass
            
        def mock_send_header(name, value):
            pass
            
        def mock_end_headers():
            pass
        
        handler_instance.send_response = mock_send_response
        handler_instance.send_header = mock_send_header
        handler_instance.end_headers = mock_end_headers
        
        # Capture the wfile writes
        writes = []
        
        def capturing_write(data):
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            writes.append(data)
            
        def capturing_flush():
            # Yield all accumulated writes
            for write_data in writes:
                if write_data.strip():
                    yield write_data
            writes.clear()
        
        class CapturingWriter:
            def write(self, data):
                capturing_write(data)
                
            def flush(self):
                for write_data in writes:
                    if write_data.strip():
                        yield write_data
                writes.clear()
        
        # Use a different approach - directly call the handler's logic
        # Import and use the functions directly
        import json
        import time
        import urllib.parse
        import csv
        import io
        import base64
        
        # Parse query parameters
        query_params = urllib.parse.parse_qs(mock_path.split('?')[1] if '?' in mock_path else '')
        url_param = query_params.get('url', [''])[0]
        
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
                time.sleep(step["delay"])
            
            # Generate CSV data using the handler's method
            csv_data = handler_instance.generate_mock_csv_data(url_param)
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
    
    # Create Server-Sent Events response
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