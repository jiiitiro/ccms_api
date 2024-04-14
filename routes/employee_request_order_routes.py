import os
from db import db
from flask import Blueprint, request, jsonify
from models import EmployeeRequestOrder

employee_request_api = Blueprint("employee_request_api", __name__)

API_KEY = os.environ.get("API_KEY")

