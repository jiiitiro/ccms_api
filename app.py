from flask import Flask, render_template, url_for, redirect
from dotenv import load_dotenv, find_dotenv
import os
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from routes.customer_routes import customer_api
from routes.customer_admin_routes import customer_admin_api
from routes.payroll_routes import payroll_api
from routes.payroll_admin_routes import payroll_admin_api
from routes.billing_admin_routes import billing_admin_api
from routes.employee_admin_routes import employee_admin_api
from routes.inventory_admin_routes import inventory_admin_api
from routes.attendance_routes import attendance_api
from routes.service_routes import service_api
from routes.employee_routes import employee_api
from routes.superadmin_routes import superadmin_api, login_manager, custom_unauthorized_handler
from models import db
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5

APP_BASE_URL = "https://csms-rest-api.onrender.com"

# from mock_data_func import payroll_admin_data, inventory_admin_data, superadmin_data, employee_data

app = Flask(__name__)

app.config.from_pyfile('config.cfg')
app.config['SECRET_KEY'] = os.environ.get("FLASK_KEY")
app.register_blueprint(customer_api)
app.register_blueprint(customer_admin_api)
app.register_blueprint(payroll_api)
app.register_blueprint(payroll_admin_api)
app.register_blueprint(billing_admin_api)
app.register_blueprint(employee_admin_api)
app.register_blueprint(inventory_admin_api)
app.register_blueprint(service_api)
app.register_blueprint(employee_api)
app.register_blueprint(superadmin_api)
app.register_blueprint(attendance_api)

# os environment here
load_dotenv(find_dotenv())

# api-key
API_KEY = os.environ.get('API_KEY')
# email-smtp
MY_EMAIL = os.environ.get('MY_EMAIL')
MY_PASSWORD = os.environ.get("MY_PASSWORD")


mail = Mail(app)
Bootstrap5(app)
login_manager.init_app(app)
# Register custom unauthorized handler
app.register_error_handler(401, custom_unauthorized_handler)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///csms.db")
db.init_app(app)
migrate = Migrate(app, db)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

    # payroll_admin_data("mock_data/payroll_admin_data.csv")
    # inventory_admin_data("mock_data/inventory_admin_data.csv")
    # superadmin_data("mock_data/superadmin_data.csv")
    # employee_data("mock_data/employee_data.csv")


@app.route('/')
def home():
    return redirect(url_for('superadmin_api.superadmin_login'))


if __name__ == "__main__":
    app.run(debug=True, port=5013)
