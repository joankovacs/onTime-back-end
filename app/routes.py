from flask import Blueprint, request, jsonify, make_response, abort
from sqlalchemy import asc
import datetime
import math

from app import db
from app.models.routine import Routine
from app.models.task import Task

##### TODO ##########################################################
'''
    CURRENT: order routines by datetimes (if possible disregard date!)
    ?Make position_x, position_y attributes for Task
    ?Make Task start times return isoformat datetime
'''

##### TABLE OF CONTENTS #############################################

#   [0] IMPORTS
#   [1] BLUEPRINT DEFINITIONS
#   [2] HELPER FUNCTIONS
#   [3] ROUTINE ENDPOINTS
#   [4] INITIATION ENDPOINTS & HELPER FUNCTIONS
#   [5] TASKS ENDPOINTS


##### [1] BLUEPRINT DEFINITIONS #####################################

routine_bp = Blueprint('routine_bp', __name__, url_prefix='/routines')
task_bp = Blueprint('task_bp', __name__, url_prefix='/tasks')


##### [2] HELPER FUNCTIONS ##########################################

def calculate_start_times(init_time, tasks):
    '''
    INPUT: the time the routine initiated; the list of tasks in the routine
    OUTPUT: a list of datetime objects that correspond to the task list; these
    objects are when each task should start given init time
    USED IN: GET Routine initiation special endpoints
    '''
    task_minutes = [task.time for task in tasks]
    task_start_times = []
    for i in range(len(task_minutes)):
        total_minutes = sum(task_minutes[:i])
        task_start_times.append(init_time + datetime.timedelta(minutes=total_minutes))
    return task_start_times


def calculate_task(init_time, tasks):
    '''
    INPUT: time the routine initiated, a list of tasks in the routine
    OUTPUT: the current task given time passed since init
    USED IN: GET Routine initiation special endpoints
    '''
    now = datetime.datetime.today()
    task_start_times = calculate_start_times(init_time, tasks)

    for task, start_time in zip(tasks, task_start_times):
        if now > start_time:
            current_start_time = start_time
            current_task = task

    return current_task, current_start_time


def calculate_progress(task, task_start_time):
    '''
    INPUT: the current task at hand (assuming the routine is running), the time the task started
    OUTPUT: an integer representing the % the task is completed
    USED IN: GET routine initiation special endpoints
    '''
    now = datetime.datetime.today()
    time_diff = (now - task_start_time).seconds

    task_seconds = datetime.timedelta(minutes=task.time).seconds

    return math.floor((time_diff/task_seconds)*100)


def update_task_start_times(routine_id):
    '''
    This function is called in endpoints where the complete_time of a routine
    can change in any way, or the time of any tasks can change in any way.
    This function is called in update_routine_start_time() and
    update_total_routine_time(), which makes this function run in the
    following endpoints:
        ROUTINE: POST
        ROUTINE: PUT
        TASKS: POST
        TASKS: PUT
        TASKS: DELETE
    '''
    routine = validate_id(routine_id, "routine")
    if routine.start_time:
        task_start_times = calculate_start_times(routine.start_time, routine.tasks)

        for i in range(len(routine.tasks)):
            routine.tasks[i].start_time = task_start_times[i]
    db.session.commit()


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
        abort(make_response({"details":f"{object_type} {object_id} invalid"}, 400))

    if object_type == "routine":
        response = Routine.query.get(object_id)
    elif object_type == "task":
        response = Task.query.get(object_id)
    else:
        abort(make_response({"details":f"{object_type} {object_id} not found"}, 404))

    if not response:
        abort(make_response({"details":f"{object_type} {object_id} not found"}, 404))

    return response


def update_routine_start_time(routine_id):
    '''
    If the routine [by routine id] has a complete time, this function updates the start time.
    This function is called in endpoints where routine time information is changed.
    The endpoints are:
        ROUTINE: POST
        ROUTINE: PUT
    Additionally, this function is always called in update_total_routine_time().
    These endpoints are:
        TASKS: POST
        TASKS: PUT
        TASKS: DELETE
    '''
    routine = validate_id(routine_id, "routine")

    if routine.complete_time:
        time_diff = datetime.timedelta(minutes=routine.total_time)
        routine.start_time = routine.complete_time - time_diff
        db.session.commit()

        update_task_start_times(routine_id)


def update_total_routine_time(routine_id):
    '''
    This function is called in endpoints where the tasks in a routine change in any way.
    The endpoints are:
        TASKS: POST
        TASKS: PUT
        TASKS: DELETE
    '''
    routine = validate_id(routine_id, "routine")
    routine.set_total_time()

    update_routine_start_time(routine_id)

    db.session.commit()


def dict_to_datetime(time):
    '''
    Given a dict with 5 time fields, this returns a datetime object
    This function runs in the following endpoints:
        Routine PUT
        Routine POST
    '''
    now = datetime.datetime.today()

    dt = datetime.datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=time["hour"],
        minute=time["minute"]
    )



    return dt


##### [3] ROUTINE ENDPOINTS #########################################

@routine_bp.route("", methods=["GET"])
def get_all_routines():
    routines = Routine.query.all()

    #1 Initialize empty lists for if a routine has a time or no time
    time_routines = []
    no_time_routines = []

    #2 Add routines in time_routines by complete_time.time(), else no_time_routines
    for routine in routines:
        if routine.complete_time:
            time_routines.append(routine)
        else:
            no_time_routines.append(routine)

    #sort the respective lists and combine them for the return
    time_routines.sort(key=lambda routine: routine.complete_time.time())
    no_time_routines.sort(key=lambda routine: routine.routine_id)

    sorted_routines = time_routines + no_time_routines

    return jsonify([routine.to_dict() for routine in sorted_routines]), 200


@routine_bp.route("/<routine_id>", methods=["GET"])
def get_one_routine(routine_id):
    routine = validate_id(routine_id, "routine")
    return jsonify(routine.to_dict()), 200


@routine_bp.route("", methods=["POST"])
def post_routine():
    request_body = request.get_json()

    if "title" in request_body:
        new_routine = Routine(title=request_body["title"])

        attr_list = ["description", "destination", "complete_time", "start_time", "total_time", "saved"]
        for attribute in attr_list:
            if attribute in request_body:
                if "complete_time" == attribute:
                    setattr(new_routine, "complete_time", iso_to_datetime(request_body["complete_time"]))
                else:
                    setattr(new_routine, attribute, request_body[attribute])

    else:
        abort(make_response({"details": "Invalid data"}, 400))

    db.session.add(new_routine)
    db.session.commit()

    update_routine_start_time(new_routine.routine_id)

    return make_response(new_routine.to_dict(), 201)


@routine_bp.route("/<routine_id>", methods=["PUT"])
def update_routine(routine_id):
    routine = validate_id(routine_id, "routine")
    request_body = request.get_json()

    routine_dict = routine.__dict__

    for key in dict(request_body):
        if key in routine_dict:
            if key == "complete_time":
                setattr(routine, "complete_time", iso_to_datetime(request_body["complete_time"]))
            else:
                setattr(routine, key, request_body[key])

    update_routine_start_time(routine_id)
    db.session.commit()

    return jsonify(routine.to_dict()), 200


@routine_bp.route("/<routine_id>", methods=["DELETE"])
def delete_routine(routine_id):
    #This should also delete all tasks that are part of the routine
    routine = validate_id(routine_id, "routine")
    for task in routine.tasks:
        delete_one_task(task.task_id)
    db.session.delete(routine)
    db.session.commit()
    return {"details":f'Routine {routine_id} successfully deleted'}, 200



##### [4] INITIATION ENDPOINTS ######################################

@routine_bp.route("/init/<routine_id>", methods=["PUT"])
def initiate_routine(routine_id):
    routine = validate_id(routine_id, "routine")

    routine.initiated_time = datetime.datetime.today()
    db.session.commit()

    return jsonify(routine.to_dict()), 200


@routine_bp.route("/init/<routine_id>", methods=["GET"])
def get_routine_progress(routine_id):
    '''
    Set up starter variables:
        1. validated routine
        2. List of tasks including a new field "initiated_time" (based of off routine.initiated_time)
            2a. Start times for all tasks
            2b. Add new dict key for each task in list of tasks
    Calculate return values:
        1. Current task, current start time
        2. Percent remaining
        3. Complete tasks    { These are calculated based off of current_task
        4. Incomplete tasks   { 

    '''
    routine = validate_id(routine_id, "routine")

    task_start_times = calculate_start_times(routine.initiated_time, routine.tasks)
    tasks = [task.to_dict() for task in routine.tasks]
    for task, start_time in zip(tasks, task_start_times):
        task["initiated_time"] = start_time.isoformat()

    #------------------------

    current_task, current_start_time = calculate_task(routine.initiated_time, routine.tasks)

    percent_remaining = calculate_progress(current_task, current_start_time)

    current_task_index = routine.tasks.index(current_task)
    complete_tasks = tasks[:current_task_index]
    incomplete_tasks = tasks[current_task_index:]

    #------------------------

    return {
        "current_task": current_task.to_dict(),
        "percent": percent_remaining,
        "complete_tasks":complete_tasks,
        "incomplete_tasks":incomplete_tasks,
        }



##### [5] TASKS ENDPOINTS ###########################################

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
    update_total_routine_time(request_body["routine_id"])
    db.session.commit()

    return make_response(new_task.to_dict(), 201)


@task_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = validate_id(task_id, "task")
    request_body = request.get_json()

    task.title = request_body["title"]
    task.time = request_body["time"]

    update_total_routine_time(request_body["routine_id"])
    db.session.commit()

    return jsonify(task.to_dict()), 200


@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_one_task(task_id):
    task = validate_id(task_id, "task")

    db.session.delete(task)
    update_total_routine_time(task.routine_id)
    db.session.commit()
    return {"details" : f'Task {task_id} successfully deleted'}, 200

