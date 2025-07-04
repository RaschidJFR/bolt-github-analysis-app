# GitHub Repository Analyzer

A modern web application for analyzing GitHub repositories and generating comprehensive CSV reports. Built with React frontend and Python backend, optimized for Vercel deployment.

## Features

- **GitHub URL Validation**: Real-time validation of GitHub repository URLs
- **Progress Tracking**: Live progress updates using Server-Sent Events
- **CSV Export**: Automatic download of detailed analysis reports
- **Modern UI**: Beautiful, responsive interface with smooth animations
- **Vercel Optimized**: Designed specifically for Vercel's serverless platform

## Tech Stack

### Frontend
- React 18 with TypeScript
- Tailwind CSS for styling
- Lucide React for icons
- Vite for build tooling

### Backend
- Python serverless functions
- Server-Sent Events for real-time updates
- CSV generation and download

## Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Deployment

This project is optimized for Vercel deployment:

1. Connect your GitHub repository to Vercel
2. Vercel will automatically detect the configuration
3. Deploy with a single click

The `vercel.json` configuration ensures:
- Python serverless functions are properly configured
- Extended timeout for analysis operations
- Proper routing for API endpoints

## API Endpoints

### `/api/analyze`
- **Method**: GET
- **Description**: Server-Sent Events endpoint for real-time progress updates
- **Parameters**: `url` (GitHub repository URL)
- **Response**: Stream of progress events

### `/api/download-csv`
- **Method**: GET
- **Description**: Download CSV report for analyzed repository
- **Parameters**: `url` (GitHub repository URL)
- **Response**: CSV file download

## CSV Report Contents

The generated CSV report includes:
- Repository metadata (name, owner, size, stars, forks)
- Code metrics (lines of code, languages, complexity)
- Dependencies and package information
- File structure analysis
- Quality and security scores
- Commit and contributor statistics

## Architecture

The application uses Server-Sent Events to handle long-running analysis operations while staying within Vercel's serverless function limits. The frontend maintains a persistent connection to receive real-time updates, and automatically downloads the CSV report when analysis is complete.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this project for your own purposes.