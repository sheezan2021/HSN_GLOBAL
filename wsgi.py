import os
import sys
import logging
from app import app as application

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log the current working directory and files in the root directory
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Files in root directory: {os.listdir('.')}")

# Log the static folder path
if hasattr(application, 'static_folder'):
    logger.info(f"Static folder: {application.static_folder}")
    if os.path.exists(application.static_folder):
        logger.info(f"Static folder exists. Contents: {os.listdir(application.static_folder)}")
    else:
        logger.error("Static folder does not exist!")

# Ensure the static folder exists for Vercel
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
if not os.path.exists(static_path):
    os.makedirs(static_path, exist_ok=True)
    logger.info(f"Created static directory at: {static_path}")

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)
