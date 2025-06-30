from app import app
from flask import send_from_directory
import os
from waitress import serve

# Serve static files directly
@app.route('/<path:path>')
def serve_static(path):
    if path.startswith('static/'):
        return send_from_directory('.', path)
    return app.send_static_file(path)

# This is the Vercel serverless function handler
handler = app

# This is needed for local development
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    print(f"Starting Waitress server on port {port}...")
    serve(app, host='0.0.0.0', port=port)
