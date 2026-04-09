from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Task

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    data = request.get_json()
    user_id = int(get_jwt_identity())

    new_task = Task(
        title=data["title"],
        description=data.get("description", ""),
        status=data.get("status", "pending"),
        user_id=user_id,
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify({"message": "Task created successfully"}), 201


@tasks_bp.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    user_id = int(get_jwt_identity())
    tasks = Task.query.filter_by(user_id=user_id).all()

    result = []
    for task in tasks:
        result.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
        })

    return jsonify(result), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"message": "Task not found"}), 404

    data = request.get_json()

    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.status = data.get("status", task.status)

    db.session.commit()

    return jsonify({"message": "Task updated successfully"}), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"message": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted successfully"}), 200