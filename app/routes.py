from flask import Blueprint, request, jsonify, make_response, abort
from app import db
from app.models.routine import Routine
from app.models.task import Task


##### TABLE OF CONTENTS #############################################

#   [0] IMPORTS
#   [1] BLUEPRINT DEFINITIONS
#   [2] HELPER FUNCTIONS
#   [3] ROUTINE ENDPOINTS
#   [4] TASKS ENDPOINTS


##### [1] BLUEPRINT DEFINITIONS #####################################

routine_bp = Blueprint('routine_bp', __name__, url_prefix='/routines')
task_bp = Blueprint('task_bp', __name__, url_prefix='/tasks')


##### [2] HELPER FUNCTIONS ##########################################

def validate_id(object_id, object_type):
    '''
    Validates the routine or task based on ID and fetches the object from the database.
        *object_id:  id of a routine or task
        *object_type: "routine" or "task" depending on endpoint
        OUTPUT: routine or task object fetched from database.
    '''
    try:
        object_id = int(object_id)
    except:
        abort(make_response({"message":f"{object_type} {object_id} invalid"}, 400))

    if object_type == "routine":
        response = Routine.query.get(object_id)
    elif object_type == "task":
        response = Task.query.get(object_id)
    else:
        abort(make_response({"message":f"{object_type} {object_id} not found"}, 404))

    if not response:
        abort(make_response({"message":f"{object_type} {object_id} not found"}, 404))

    return response


##### [3] ROUTINE ENDPOINTS #########################################

@routine_bp.route("", methods=["GET"])
def get_all_routines():
    routines = Routine.query.all()
    return jsonify([routine.to_dict() for routine in routines]), 200


@routine_bp.route("/<routine_id>", methods=["GET"])
def get_one_routine(routine_id):
    routine = validate_id(routine_id, "routine")
    return jsonify(routine.to_dict()), 200


@routine_bp.route("", methods=["POST"])
def post_routine():
    request_body = request.get_json()

    if "title" in request_body and "description" in request_body:
        new_routine = Routine(
            title=request_body["title"],
            description=request_body["description"],
            )
    else:
        abort(make_response({"details": "Invalid data"}, 400))

    db.session.add(new_routine)
    db.session.commit()

    return make_response(new_routine.to_dict(), 201)


@routine_bp.route("/<routine_id>", methods=["DELETE"])
def delete_routine(routine_id):
    #This should also delete all tasks that are part of the routine
    routine = validate_id(routine_id, "routine")
    #for card in board.cards:
        #delete_one_card(card.card_id)
    db.session.delete(routine)
    db.session.commit()
    return {"message":f'Routine {routine_id} successfully deleted'}, 200



##### [4] TASKS ENDPOINTS ###########################################

@task_bp.route("", methods=["GET"])
def get_all_tasks():
    routine_id = request.args.get("routine_id")
    if routine_id:
        tasks = Task.query.filter_by(routine_id=routine_id)#.order_by(asc(Task.task_id))
    else:
        tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks]), 200


@task_bp.route("/<task_id>", methods=["GET"])
def get_one_task(task_id):
    task = validate_id(task_id, "task")
    return jsonify(task.to_dict()), 200


@task_bp.route("", methods=["POST"])
def post_task():
    request_body = request.get_json()

    if ("title" in request_body) and ("time" in request_body) and ("routine_id" in request_body):
        if len(request_body["title"]) > 40:
            abort(make_response({"details": "Titles cannot be longer than 40 characters"}, 400))
        if type(request_body["time"]) != int:
            abort(make_response({"details": "Time must be an integer"}, 400))
        if request_body["time"] < 1:
            abort(make_response({"details": "Time must be an integer that is equal to 1 or more"}, 400))
        new_task = Task(
            title=request_body["title"],
            time=request_body["time"],
            routine_id=request_body["routine_id"],
            )
    else:
        abort(make_response({"details": "Invalid data"}, 400))

    db.session.add(new_task)
    db.session.commit()

    return make_response(new_task.to_dict(), 201)


@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_one_task(task_id):
    task = validate_id(task_id, "task")
    db.session.delete(task)
    db.session.commit()
    return {"message" : f'Task {task_id} successfully deleted'}, 200







