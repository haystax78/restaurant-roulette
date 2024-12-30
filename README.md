# Restaurant Roulette

A simple web application to track your favorite restaurants and help you decide where to eat!

## Features

- Add restaurants with names, notes, and ratings
- View all restaurants in a clean, responsive interface
- Delete restaurants you no longer want to track
- Automatic date tracking for when restaurants are added

## Local Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Visit http://localhost:5000 in your browser

## Deployment on Render.com

1. Create a free account on Render.com
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Click "Create Web Service"

Your application will be deployed and accessible via a Render.com URL.
