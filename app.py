from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics

from database import get_db_connection, init_db

app = Flask(__name__)

metrics = PrometheusMetrics(app)

init_db()


@app.route("/")
def home():
    return "Student Task Management System"


@app.route("/health")
def health():
    return {"status": "healthy"}


@app.route("/tasks", methods=["GET"])
def get_tasks():
    connection = get_db_connection()

    tasks = connection.execute(
        "SELECT * FROM tasks"
    ).fetchall()

    connection.close()

    return jsonify([dict(task) for task in tasks])


@app.route("/tasks", methods=["POST"])
def create_task():

    data = request.get_json()

    title = data.get("title")
    description = data.get("description", "")

    if not title:
        return {"error": "Title is required"}, 400

    connection = get_db_connection()

    cursor = connection.execute(
        """
        INSERT INTO tasks (title, description)
        VALUES (?, ?)
        """,
        (title, description)
    )

    connection.commit()

    task_id = cursor.lastrowid

    connection.close()

    return {
        "message": "Task created",
        "task_id": task_id
    }, 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):

    data = request.get_json()

    completed = data.get("completed")

    connection = get_db_connection()

    connection.execute(
        """
        UPDATE tasks
        SET completed = ?
        WHERE id = ?
        """,
        (completed, task_id)
    )

    connection.commit()

    connection.close()

    return {
        "message": "Task updated"
    }


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):

    connection = get_db_connection()

    connection.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    connection.commit()

    connection.close()

    return {
        "message": "Task deleted"
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)