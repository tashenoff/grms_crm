from flask import Blueprint

# Create blueprint for leads routes
leads_bp = Blueprint('leads', __name__, url_prefix='')

# Import routes after creating the blueprint to avoid circular imports
from api.routes import lead_routes

def register_routes(app):
    """Register all blueprints with the Flask application"""
    app.register_blueprint(leads_bp) 