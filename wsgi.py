import os
from app import app
from flask import send_from_directory

# This is the Vercel serverless function handler
handler = app

# Serve static files directly
@app.route('/<path:path>')
def serve_static(path):
    if path.startswith('static/'):
        return send_from_directory('.', path)
    return app.send_static_file(path)

# This is needed for local development
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))
