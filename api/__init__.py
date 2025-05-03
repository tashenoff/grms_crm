import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from api.routes import register_routes

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    # Load environment variables
    load_dotenv()
    
    # Create Flask application
    app = Flask(__name__, template_folder='../templates')
    
    # Enable CORS
    CORS(app)
    
    # Register routes
    register_routes(app)
    
    # Return the configured application
    return app 