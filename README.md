# GitHub Repository Analyzer

A modern web application for analyzing GitHub repositories and generating comprehensive CSV reports. Built with Flask backend and vanilla JavaScript frontend, optimized for PythonAnywhere deployment.

## Features

- **GitHub URL Validation**: Real-time validation of GitHub repository URLs
- **Progress Tracking**: Live progress updates using Server-Sent Events
- **CSV Export**: Automatic download of detailed analysis reports
- **Modern UI**: Beautiful, responsive interface with smooth animations
- **PythonAnywhere Optimized**: Designed specifically for PythonAnywhere hosting

## Tech Stack

### Frontend
- Vanilla JavaScript (ES6+)
- Tailwind CSS for styling
- SVG icons for UI elements
- Server-Sent Events for real-time updates

### Backend
- Flask web framework
- Python server-side processing
- Server-Sent Events for real-time updates
- CSV generation and download

## Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your GitHub token and OpenAI API key
   ```
5. Start the development server:
   ```bash
   python app.py
   ```
6. Open http://localhost:5000 in your browser

## Deployment

This project is optimized for PythonAnywhere deployment. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deployment Steps:

1. Create a PythonAnywhere account
2. Clone your repository
3. Set up a virtual environment and install dependencies
4. Configure environment variables
5. Set up the web app with WSGI configuration
6. Configure static files
7. Reload and test

## API Endpoints

### `/api/analyze`
- **Method**: GET
- **Description**: Server-Sent Events endpoint for real-time progress updates
- **Parameters**: `url` (GitHub repository URL)
- **Response**: Stream of progress events

### `/`
- **Method**: GET
- **Description**: Main application interface
- **Response**: HTML page with the analyzer interface

## CSV Report Contents

The generated CSV report includes:
- Repository metadata (name, owner, size, stars, forks)
- Code metrics (lines of code, languages, complexity)
- Dependencies and package information
- File structure analysis
- Quality and security scores
- Commit and contributor statistics

## Architecture

The application uses Server-Sent Events to handle long-running analysis operations. The Flask backend processes GitHub repository analysis in the background while the frontend maintains a persistent connection to receive real-time updates. The CSV report is automatically downloaded when analysis is complete.

### Project Structure

```
├── app.py                 # Main Flask application
├── wsgi.py               # WSGI configuration for PythonAnywhere
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html       # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css    # Custom styles
│   └── js/
│       └── app.js       # Frontend JavaScript
├── api/
│   └── analyze.py       # Original Vercel function (for reference)
└── DEPLOYMENT.md        # Deployment guide
```

## Environment Variables

Create a `.env` file with the following variables:

```
GITHUB_TOKEN=your_github_personal_access_token
OPENAI_API_KEY=your_openai_api_key
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this project for your own purposes.