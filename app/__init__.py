from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask import redirect, url_for
import os

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.project import project_bp
    from app.routes.task import task_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(project_bp, url_prefix='/projects')
    app.register_blueprint(task_bp, url_prefix='/tasks')

    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/register')
    def register():
        return render_template('register.html')
 

    @app.route('/home')
    def home():
        username = request.args.get('username')
        if not username:
            return redirect(url_for('index'))
        return render_template('home.html', username=username)
    
    # in app/__init__.py — replace the existing project_detail route with this
    @app.route('/project_detail/<int:project_id>')
    def project_detail(project_id):
        username = request.args.get('username', '')
        return render_template('project_detail.html', project_id=project_id, username=username)
    
    @app.route('/add_task')
    def add_task_page():
        return render_template('add_task.html')




    return app




