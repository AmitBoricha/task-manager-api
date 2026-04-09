from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Task

tasks_bp = Blueprint("tasks", __name__)

VALID_STATUSES = {"pending", "completed"}


@tasks_bp.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "Missing or invalid JSON body"}), 400

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    status = data.get("status", "pending").strip().lower()

    if not title:
        return jsonify({"message": "title is required"}), 400

    if status not in VALID_STATUSES:
        return jsonify({"message": "status must be 'pending' or 'completed'"}), 400

    user_id = int(get_jwt_identity())

    new_task = Task(
        title=title,
        description=description,
        status=status,
        user_id=user_id,
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        "message": "Task created successfully",
        "task": {
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "status": new_task.status,
            "user_id": new_task.user_id,
            "created_at": new_task.created_at.isoformat(),
        }
    }), 201


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
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"message": "Missing or invalid JSON body"}), 400

    user_id = int(get_jwt_identity())
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"message": "Task not found"}), 404

    title = data.get("title")
    description = data.get("description")
    status = data.get("status")

    if title is None and description is None and status is None:
        return jsonify({"message": "At least one field must be provided"}), 400

    if title is not None:
        title = title.strip()
        if not title:
            return jsonify({"message": "title cannot be empty"}), 400
        task.title = title

    if description is not None:
        task.description = description.strip()

    if status is not None:
        status = status.strip().lower()
        if status not in VALID_STATUSES:
            return jsonify({"message": "status must be 'pending' or 'completed'"}), 400
        task.status = status

    db.session.commit()

    return jsonify({
        "message": "Task updated successfully",
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
        }
    }), 200


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