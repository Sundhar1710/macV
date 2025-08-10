from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.project_model import Project
from app.models.task_model import Task

project_bp = Blueprint('project_bp', __name__, url_prefix="/projects")

@project_bp.route('/', methods=['POST'])
@jwt_required()
def create_project():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify({'message': 'Project name is required'}), 400

    user_id = get_jwt_identity()
    new_project = Project(name=name, description=description, user_id=user_id)
    db.session.add(new_project)
    db.session.commit()

    return jsonify({'message': 'Project created successfully'}), 201



@project_bp.route('/', methods=['GET'])
@jwt_required()
def get_projects():
    user_id = get_jwt_identity()
    projects = Project.query.filter_by(user_id=user_id).all()

    result = []
    for project in projects:
        result.append({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'created_at': project.created_at
        })

    return jsonify(result), 200



@project_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project_details(project_id):
    user_id = get_jwt_identity()
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()

    if not project:
        return jsonify({'message': 'Project not found'}), 404

    tasks = Task.query.filter_by(project_id=project.id).all()
    task_list = [{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'completed': task.is_completed
    } for task in tasks]

    return jsonify({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'created_at': project.created_at,
        'tasks': task_list
    }), 200


@project_bp.route('/<int:project_id>', methods=['PATCH'])
@jwt_required()
def update_project(project_id):
    data = request.get_json()
    user_id = get_jwt_identity()

    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({'message': 'Project not found'}), 404

    project.name = data.get('name', project.name)
    project.description = data.get('description', project.description)

    db.session.commit()
    return jsonify({'message': 'Project updated successfully'}), 200



@project_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    user_id = get_jwt_identity()
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404

    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Project deleted successfully'}), 200
