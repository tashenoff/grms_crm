import logging
from api import create_app

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create application
app = create_app()

if __name__ == "__main__":
    print('=== Flask URL MAP ===')
    print(app.url_map)
    logger.info('Starting Flask server')
    app.run(host="0.0.0.0", port=5000) 