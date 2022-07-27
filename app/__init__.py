from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/ontime_development'

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes import routine_bp
    app.register_blueprint(routine_bp)
    from .routes import task_bp
    app.register_blueprint(task_bp)

    return app
