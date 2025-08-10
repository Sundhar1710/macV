from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.task_model import Task
from datetime import datetime
from app.models.project_model import Project  

task_bp = Blueprint('task_bp', __name__, url_prefix="/tasks")


def serialize_task(task):
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'is_completed': task.is_completed,
        'project_id': task.project_id,
        'assigned_user': task.assigned_user,
        'due_date': task.due_date
    }


@task_bp.route('/', methods=['POST'])  
@jwt_required()
def create_task():
    data = request.get_json()

    try:
        user_id = int(get_jwt_identity())
        new_task = Task(
            title=data.get('title'),
            description=data.get('description'),
            priority=data.get('priority'),
            due_date=datetime.strptime(data.get('due_date'), "%Y-%m-%d") if data.get('due_date') else None,
            user_id=user_id,
            project_id=data.get('project_id'),
            assigned_user=data.get('assigned_user'),
            status=data.get('status', 'pending'),
            is_completed=(data.get('status', '').lower() == 'completed')
        )

        db.session.add(new_task)
        db.session.commit()

        return jsonify({"message": "Task created successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@task_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    q = Task.query.filter_by(user_id=user_id)

    status = request.args.get('status')
    if status:
        q = q.filter_by(status=status.lower())

    priority = request.args.get('priority')
    if priority:
        q = q.filter_by(priority=priority)

    project_id = request.args.get('project_id')
    if project_id:
        q = q.filter_by(project_id=project_id)


    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'desc')
    if hasattr(Task, sort_by):
        col = getattr(Task, sort_by)
        q = q.order_by(col.desc() if order == 'desc' else col.asc())

    page = max(int(request.args.get('page', 1)), 1)
    limit = max(int(request.args.get('limit', 10)), 1)
    paginated = q.paginate(page=page, per_page=limit, error_out=False)

    return jsonify({
        'total': paginated.total,
        'page': page,
        'limit': limit,
        'tasks': [serialize_task(t) for t in paginated.items]
    }), 200

@task_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'message': 'Task not found'}), 404
    return jsonify(serialize_task(task)), 200

@task_bp.route('/<int:task_id>', methods=['PATCH'])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'message': 'Task not found'}), 404

    data = request.get_json() or {}

    if 'project_id' in data:
        project = Project.query.filter_by(id=data['project_id'], user_id=user_id).first()
        if not project:
            return jsonify({'message': 'Project not found or not owned by user'}), 404

    for field in ['title', 'description', 'status', 'priority', 'is_completed', 'project_id', 'due_date', 'assigned_user']:
        if field in data:
            setattr(task, field, data[field])

    if 'status' in data:
        task.is_completed = (task.status.lower() == 'completed')

    db.session.commit()
    return jsonify({'message': 'Task updated successfully', 'task': serialize_task(task)}), 200

@task_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'message': 'Task not found'}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'}), 200
