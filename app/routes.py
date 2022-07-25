from flask import Blueprint, request, jsonify, make_response, abort
from app import db
from app.models.routine import Routine


routine_bp = Blueprint('routine_bp', __name__, url_prefix='/routines')
