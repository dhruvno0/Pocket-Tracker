from flask import Flask, redirect, url_for
from config import config
from auth import auth_bp
from main import main_bp
import os

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    
    # Root route redirect
    @app.route('/')
    def index():
        return redirect(url_for('main.dashboard'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return redirect(url_for('main.dashboard'))
    
    @app.errorhandler(500)
    def internal_error(error):
        return "Internal server error", 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)