# Deployment Guide: PythonAnywhere

This guide will help you deploy the Repository Analyzer Flask application on PythonAnywhere.

## Prerequisites

1. A PythonAnywhere account (free or paid)
2. GitHub repository with your code
3. GitHub Personal Access Token
4. OpenAI API Key

## Step 1: Set up PythonAnywhere

1. Go to [PythonAnywhere](https://www.pythonanywhere.com/) and create an account
2. Log in to your PythonAnywhere dashboard

## Step 2: Clone your repository

1. Open a Bash console in PythonAnywhere
2. Navigate to your home directory: `cd ~`
3. Clone your repository:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

## Step 3: Set up a virtual environment

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Step 4: Configure environment variables

1. Create a `.env` file in your project directory:
   ```bash
   nano .env
   ```

2. Add your environment variables:
   ```
   GITHUB_TOKEN=your_github_personal_access_token
   OPENAI_API_KEY=your_openai_api_key
   ```

3. Save and exit (Ctrl+X, Y, Enter)

## Step 5: Set up the web app

1. Go to the "Web" tab in your PythonAnywhere dashboard
2. Click "Add a new web app"
3. Choose "Manual configuration" (not "Flask")
4. Select Python 3.9 or higher
5. Note your domain name (e.g., `yourusername.pythonanywhere.com`)

## Step 6: Configure the WSGI file

1. In the "Web" tab, click on the WSGI configuration file link
2. Replace the content with the path to your `wsgi.py` file:
   ```python
   import sys
   import os
   
   # Add your project directory to the Python path
   path = '/home/yourusername/your-repo-name'
   if path not in sys.path:
       sys.path.append(path)
   
   # Import the Flask app
   from app import app as application
   ```

3. Save the file

## Step 7: Configure the virtual environment

1. In the "Web" tab, set the "Working directory" to: `/home/yourusername/your-repo-name`
2. Set the "WSGI configuration file" to point to your `wsgi.py` file
3. In the "Virtual environment" section, enter: `/home/yourusername/your-repo-name/venv`

## Step 8: Set up static files

1. In the "Web" tab, go to "Static files"
2. Add a static files mapping:
   - URL: `/static/`
   - Directory: `/home/yourusername/your-repo-name/static`

## Step 9: Reload the web app

1. Click the "Reload" button in the "Web" tab
2. Your app should now be accessible at `yourusername.pythonanywhere.com`

## Step 10: Test the application

1. Visit your domain in a web browser
2. Enter a GitHub repository URL
3. Test the analysis functionality

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure your virtual environment is activated and dependencies are installed
2. **Environment variables not found**: Check that your `.env` file is in the correct location
3. **Static files not loading**: Verify the static files configuration in the Web tab
4. **Permission errors**: Make sure your files have the correct permissions

### Logs

- Check the error logs in the "Web" tab for debugging information
- Use the "Files" tab to view and edit files directly on PythonAnywhere

### Performance

- The free tier has limitations on CPU and memory usage
- Consider upgrading to a paid plan for better performance
- Monitor your usage in the "Account" tab

## Security Notes

1. Never commit your `.env` file to version control
2. Use strong, unique tokens for GitHub and OpenAI
3. Regularly rotate your API keys
4. Monitor your API usage to avoid unexpected charges

## Maintenance

1. Regularly update your dependencies: `pip install -r requirements.txt --upgrade`
2. Monitor your PythonAnywhere usage
3. Keep your virtual environment clean
4. Backup your configuration and data regularly 