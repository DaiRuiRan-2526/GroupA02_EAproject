from flask import Flask
from app.config import Config
from flask_migrate import Migrate
from app.extensions import db, login_manager, bootstrap



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    migrate = Migrate(app, db)
    
    
    from app.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.blueprints.tutorials import bp as tutorials_bp
    app.register_blueprint(tutorials_bp, url_prefix='/tutorials')
    
    from app.blueprints.resources import bp as resources_bp
    app.register_blueprint(resources_bp, url_prefix='/resources')
    
    from app.blueprints.community import bp as community_bp
    app.register_blueprint(community_bp, url_prefix='/community')
    
    from app.blueprints.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    return app