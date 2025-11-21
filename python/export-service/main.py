from flask import Flask, send_from_directory
from flask_cors import CORS
from app.core.config import Config
from app.core.database import db
from app.api.endpoints import notes_bp, export_bp


def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    CORS(app)  # Enable CORS for frontend

    # Register blueprints
    app.register_blueprint(notes_bp, url_prefix='/api/notes')
    app.register_blueprint(export_bp, url_prefix='/api/export')

    # Serve frontend from root
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
