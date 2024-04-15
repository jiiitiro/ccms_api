from email.mime.application import MIMEApplication
import os
from flask import Blueprint, request, jsonify, render_template_string
from models import Payroll, Employee, Attendance, PayrollContributionRate, PayrollDeduction
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import calendar
from datetime import date
from db import db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio
import pdfcrowd
import sys

payroll_api = Blueprint('payroll_api', __name__)

# api-key
API_KEY = os.environ.get('API_KEY')
# email-smtp
MY_EMAIL = os.environ.get('MY_EMAIL')
MY_PASSWORD = os.environ.get("MY_PASSWORD")
BASE_URL = os.environ.get("BASE_URL")


# Get all payroll table data
@payroll_api.get('/payroll/all')
def payroll_data():
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        query_data = Payroll.query.all()
        payroll_dict = [{
            'payroll_id': data.payroll_id,
            'employee_id': data.employee_id,
            'employee_name': f"{data.employee.first_name} {data.employee.middle_name} {data.employee.last_name}",
            'employee_position': data.employee.position,
            'period_start': data.period_start,
            'period_end': data.period_end,
            'daily_rate': float(data.employee.daily_rate),
            'base_salary': data.base_salary,
            'gross_pay': data.gross_pay,
            'net_pay': data.net_pay,
            'total_ot_hrs': data.total_ot_hrs,
            'total_tardiness': data.total_tardiness,
            'total_days_of_work': data.total_days_of_work,
            'sss_contribution': data.deductions[0].sss_contribution,
            'philhealth_contribution': data.deductions[0].philhealth_contribution,
            'pagibig_contribution': data.deductions[0].pagibig_contribution,
            'withholding_tax': data.deductions[0].withholding_tax,
            'other_deduction': data.deductions[0].other_deductions,
            'thirteenth_month_pay': data.thirteenth_month_pay,
            'status': data.status
        } for data in query_data]

        return jsonify(success={"payroll_data": payroll_dict}), 200

    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@payroll_api.get("/payroll/<int:employee_id>")
def get_specific_payroll(employee_id):
    api_key_header = request.headers.get("x-api-key")
    if api_key_header == API_KEY:
        query_data = Employee.query.filter_by(employee_id=employee_id).first()

        if query_data is None:
            return jsonify(error={"message": "Employee id not found."}), 404

        employee_data = []

        if query_data:

            employee_dict = {'employee_id': query_data.employee_id,
                             'employee_name': f"{query_data.first_name} {query_data.middle_name} "
                                              f"{query_data.last_name}",
                             'employee_position': query_data.position,
                             'daily_rate': float(query_data.daily_rate),
                             "payrolls": [
                                {
                                    'payroll_id': payroll.payroll_id,
                                    'period_start': payroll.period_start,
                                    'period_end': payroll.period_end,
                                    'base_salary': payroll.base_salary,
                                    'gross_pay': payroll.gross_pay,
                                    'net_pay': payroll.net_pay,
                                    'total_ot_hrs': payroll.total_ot_hrs,
                                    'total_tardiness': payroll.total_tardiness,
                                    'total_days_of_work': payroll.total_days_of_work,
                                    'sss_contribution': payroll.deductions[0].sss_contribution,
                                    'philhealth_contribution': payroll.deductions[0].philhealth_contribution,
                                    'pagibig_contribution': payroll.deductions[0].pagibig_contribution,
                                    'withholding_tax': payroll.deductions[0].withholding_tax,
                                    'other_deduction': payroll.deductions[0].other_deductions,
                                    'thirteenth_month_pay': payroll.thirteenth_month_pay,
                                    'status': payroll.status
                                } for payroll in query_data.payrolls
                                ]}

            employee_data.append(employee_dict)

            response = jsonify({"employee_payroll_data": employee_data})

            return response, 200

        else:
            return jsonify(error={"message": "Payroll id not found."}), 404
    else:
        return jsonify(
            error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


@payroll_api.post("/payroll/add")
def add_payroll():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_employee_id = Employee.query.filter_by(employee_id=request.form.get("employee_id")).first()

        if query_employee_id is None:
            return jsonify(error={"message": "Employee id not found."}), 404

        new_payroll = Payroll(
            employee_id=query_employee_id.employee_id,
            period_start=request.form.get("period_start"),
            period_end=request.form.get("period_end"),
            total_ot_hrs=request.form.get("total_ot_hrs"),
            total_tardiness=request.form.get("total_tardiness"),
            total_days_of_work=int(request.form.get("total_days_of_work")),
            base_salary=float(request.form.get("base_salary")),
            gross_pay=float(request.form.get("gross_pay")),
            net_pay=float(request.form.get("net_pay")),
            thirteenth_month_pay=float(request.form.get("thirteenth_month_pay")),
            status=request.form.get("status"),
        )

        if (request.form.get("sss_contribution") and request.form.get("philhealth_contribution")
                and request.form.get("pagibig_contribution") and request.form.get("withholding_tax")
                and request.form.get("other_deductions")):
            new_payroll_deduction = PayrollDeduction(
                payroll_id=new_payroll.payroll_id,
                sss_contribution=float(request.form.get("sss_contribution")),
                philhealth_contribution=float(request.form.get("philhealth_contribution")),
                pagibig_contribution=float(request.form.get("pagibig_contribution")),
                withholding_tax=float(request.form.get("withholding_tax")),
                other_deductions=float(request.form.get("other_deductions"))
            )

        else:
            new_payroll_deduction = PayrollDeduction(
                payroll_id=new_payroll.payroll_id,
                sss_contribution=0.0,
                philhealth_contribution=0.0,
                pagibig_contribution=0.0,
                withholding_tax=0.0,
                other_deductions=0.0
            )

        new_payroll.deductions.append(new_payroll_deduction)

        db.session.add(new_payroll)
        db.session.commit()

        return jsonify(success={"message": "Payroll successfully added."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@payroll_api.get("/payroll-contribution")
def get_payroll_contribution_data():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = PayrollContributionRate.query.first()

        payroll_contribution_rate_data = [
            {
                "payroll_contribution_rate_id": query_data.payroll_contribution_rate_id,
                "sss": query_data.sss,
                "philhealth": query_data.philhealth,
                "pagibig": query_data.pagibig
            }
        ]

        return jsonify(success={"payroll_contribution_rate_data": payroll_contribution_rate_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@payroll_api.post("/payroll-contribution/add")
def add_payroll_contribution():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        new_payroll_contribution_rate = PayrollContributionRate(
            payroll_contribution_rate_id=1,
            sss=float(4.5),
            philhealth=float(5),
            pagibig=float(200),
            minimum_rate=float(610)
        )

        db.session.add(new_payroll_contribution_rate)
        db.session.commit()

        return jsonify(sucess={"message": "Payroll contribution rate successfully added."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@payroll_api.patch("/payroll-contribution/update/1")
def update_payroll_contribution_rate():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = PayrollContributionRate.query.filter_by(payroll_contribution_rate_id=1).first()

        query_data.sss = request.form.get("sss", query_data.sss)
        query_data.philhealth = request.form.get("philhealth", query_data.philhealth)
        query_data.pagibig = request.form.get("pagibig", query_data.pagibig)
        query_data.minimum_rate = request.form.get("minimum_rate", query_data.minimum_rate)

        db.session.commit()

        payroll_contribution_rate_data = [
            {
                "payroll_contribution_rate_id": query_data.payroll_contribution_rate_id,
                "sss": float(query_data.sss),
                "philhealth": float(query_data.philhealth),
                "pagibig": float(query_data.pagibig),
                "minimum_rate": float(query_data.minimum_rate)
            }
        ]

        return jsonify(success={"message": "Payroll contribution rate successfully updated.",
                                "payroll_contribution_rate_data": payroll_contribution_rate_data}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@payroll_api.delete("/payroll/delete/<int:payroll_id>")
def delete_payroll(payroll_id):
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(
                error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        query_data = PayrollDeduction.query.filter_by(payroll_id=payroll_id).first()

        if query_data is None:
            return jsonify(error={"message": "Payroll id not found."}), 404

        db.session.delete(query_data)
        db.session.delete(query_data.payroll)
        db.session.commit()

        return jsonify(success={"message": "Payroll successfully deleted."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


@payroll_api.post("/payroll/email-payslip/all")
async def send_payslip():
    try:
        api_key_header = request.headers.get("x-api-key")
        if api_key_header != API_KEY:
            return jsonify(error={"Not Authorised": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

        period_start = request.form.get("period_start")
        period_end = request.form.get("period_end")

        # Query payrolls based on the filters
        query_data = Payroll.query.filter(
            Payroll.period_start == period_start,
            Payroll.period_end == period_end
        ).all()

        if not query_data:
            return jsonify(error={"message": "Payroll with that period start and end not found."}), 404

        tasks = []
        for payroll in query_data:
            if payroll.employee and payroll.employee.email and payroll.employee.is_active:
                pdf = await create_pdf(payroll)
                tasks.append(send_email(payroll.employee.email, pdf, period_start, period_end, payroll.employee.last_name))

        await asyncio.gather(*tasks)

        return jsonify(success={"message": "Payslip sent successfully."}), 200

    except Exception as e:
        return jsonify(error={"message": f"An error occurred: {str(e)}"}), 500


async def create_pdf(payroll):
    payslip_data = {
        'employee_id': payroll.employee_id,
        'employee_name': f"{payroll.employee.first_name} {payroll.employee.middle_name} {payroll.employee.last_name}",
        'employee_position': payroll.employee.position,
        'period_start': payroll.period_start,
        'period_end': payroll.period_end,
        'daily_rate': payroll.employee.daily_rate,
        'base_salary': payroll.base_salary,
        'gross_pay': payroll.gross_pay,
        'net_pay': payroll.net_pay,
        'total_ot_hrs': payroll.total_ot_hrs,
        'total_tardiness': payroll.total_tardiness,
        'total_days_of_work': payroll.total_days_of_work,
        'sss_contribution': payroll.deductions[0].sss_contribution,
        'philhealth_contribution': payroll.deductions[0].philhealth_contribution,
        'pagibig_contribution': payroll.deductions[0].pagibig_contribution,
        'withholding_tax': payroll.deductions[0].withholding_tax,
        'other_deduction': payroll.deductions[0].other_deductions,
        'thirteenth_month_pay': payroll.thirteenth_month_pay
    }

    payslip_html = render_template_string("""
        <html>
            <head></head>
            <body>
                <table border="1">
                    <tr>
                        <td colspan="6">COMPANY NAME</td>
                        <td colspan="4">PAYSLIP - SEMI-MONTHLY PAYROLL</td>
                        <td>PERIOD: {{ period_start }} - {{ period_end }}</td>
                    </tr>
        
                    <tr>
                        <td>EMPLOYEE:</td>
                        <td>{{ employee_name }}</td>
                        <td>STATUS:</td>
                        <td>{{ status }}</td>
                        <td>BASIC PAY:</td>
                        <td>{{ basic_pay }}</td>
                    </tr>
        
                    <tr>
                        <td>Position:</td>
                        <td>{{ employee_position }}</td>
                        <td>Net Pay:</td>
                        <td>{{ net_pay }}</td>
                        <td>Other Row:</td>
                        <td>{{ other_row_value }}</td>
                    </tr>
        
                    <!-- Additional rows based on payslip_data -->
                    <tr>
                        <td>Daily Rate:</td>
                        <td>{{ daily_rate }}</td>
                        <td>Total OT Hours:</td>
                        <td>{{ total_ot_hrs }}</td>
                    </tr>
                    <tr>
                        <td>Base Salary:</td>
                        <td>{{ base_salary }}</td>
                        <td>Gross Pay:</td>
                        <td>{{ gross_pay }}</td>
                        <td>Total Tardiness:</td>
                        <td>{{ total_tardiness }}</td>
                    </tr>
                    <tr>
                        <td>Total Days of Work:</td>
                        <td>{{ total_days_of_work }}</td>
                        <td>SSS Contribution:</td>
                        <td>{{ sss_contribution }}</td>
                        <td>Philhealth Contribution:</td>
                        <td>{{ philhealth_contribution }}</td>
                    </tr>
                    <tr>
                        <td>Pagibig Contribution:</td>
                        <td>{{ pagibig_contribution }}</td>
                        <td>Withholding Tax:</td>
                        <td>{{ withholding_tax }}</td>
                        <td>Other Deduction:</td>
                        <td>{{ other_deduction }}</td>
                    </tr>
                    <tr>
                        <td>13th Month Pay:</td>
                        <td>{{ thirteenth_month_pay }}</td>
                        <td colspan="2"></td>
                        <td colspan="2"></td>
                    </tr>
        
                </table>
        
                </body>
            </html>
    """, **payslip_data)

    try:
        # Create the API client instance
        client = pdfcrowd.HtmlToPdfClient('JTiro14', '47bf533ed48d35294b7fedd267986fc1')

        # Set to use HTTP
        client.setUseHttp(True)

        # Convert HTML string to PDF
        pdf_output = client.convertString(payslip_html)

        return pdf_output

    except pdfcrowd.Error as why:
        sys.stderr.write('Pdfcrowd Error: {}\n'.format(why))
        raise


async def send_email(recipient_email, pdf_bytes, period_start, period_end, last_name):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = MY_EMAIL
    sender_password = MY_PASSWORD

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "Your Payslip"

    message.attach(MIMEText("Please find attached your payslip.", "plain"))

    attachment = MIMEApplication(pdf_bytes, "pdf")
    attachment.add_header("Content-Disposition", "attachment",
                          filename=f"payslips_{period_start}-{period_end}_{last_name}.pdf")
    message.attach(attachment)

    context = smtplib.SMTP(smtp_server, smtp_port)
    context.starttls()
    context.login(sender_email, sender_password)
    context.sendmail(sender_email, recipient_email, message.as_string())
    context.quit()


# Function to generate payroll for employees
def generate_payroll():
    try:
        # Get all active employees
        active_employees = Employee.query.filter_by(is_active=True).all()

        # Get payroll contributions
        payroll_contributions = PayrollContributionRate.query.first()
        sss_contribution_rate = payroll_contributions.sss
        philhealth_contribution_rate = payroll_contributions.philhealth
        pagibig_contribution_rate = payroll_contributions.pagibig
        minimum_rate = payroll_contributions.minimum_rate

        # Calculate payroll for each employee
        for employee in active_employees:
            # Get the attendances within the period
            attendances_within_period = Attendance.query.filter(
                Attendance.employee_id == employee.employee_id,
                Attendance.work_date.between(get_period_start(), get_period_end())
            ).all()

            # Initialize total days worked
            total_days_worked = 0
            total_ot_hrs = 0
            total_tardiness = 0

            # Calculate total days worked by iterating over attendances
            for attendance in attendances_within_period:
                if attendance.login_time and attendance.logout_time:
                    total_days_worked += 1
                    total_ot_hrs += attendance.ot_hrs
                    total_tardiness += attendance.tardiness

            # Calculate base salary based on total days worked
            base_salary = employee.daily_rate * total_days_worked

            # Calculate gross pay
            gross_pay = base_salary + employee.de_minimis

            # 13th month
            thirteenth_month_pay = thirteenth_month_pay_computation(employee)

            # other_deductions = calculate_other_deductions()

            # Deduct contributions based on the period start date
            if employee.period_start.day >= 16:

                sss_contribution = base_salary * (sss_contribution_rate / 100)
                philhealth_contribution = (base_salary * (philhealth_contribution_rate / 100)) / 2
                pagibig_contribution = pagibig_contribution_rate
            else:
                sss_contribution = 0.0
                philhealth_contribution = 0.0
                pagibig_contribution = 0.0

            # Calculate withholding tax and other deductions (if any)
            if employee.daily_rate <= minimum_rate:
                withholding_tax = 0.0
            else:
                withholding_tax = calculate_withholding_tax(gross_pay)

            # Calculate net pay
            net_pay = gross_pay - (sss_contribution + philhealth_contribution + pagibig_contribution +
                                   withholding_tax)

            # Create Payroll instance
            payroll = Payroll(
                employee_id=employee.employee_id,
                period_start=get_period_start(),
                period_end=get_period_end(),
                total_ot_hrs=total_ot_hrs,
                total_tardiness=total_tardiness,
                base_salary=base_salary,
                gross_pay=gross_pay,
                net_pay=net_pay,
                thirteenth_month_pay=thirteenth_month_pay,
                status="Calculated"
            )

            other_deductions = 0.0
            # Create Payroll Deduction instance
            deduction = PayrollDeduction(
                payroll_id=payroll.payroll_id,
                sss_contribution=float(sss_contribution),
                philhealth_contribution=float(philhealth_contribution),
                pagibig_contribution=float(pagibig_contribution),
                withholding_tax=float(withholding_tax),
                other_deductions=float(other_deductions),
            )

            # Associate deduction with payroll
            payroll.deductions.append(deduction)

            db.session.add(payroll)

        db.session.commit()

        print("Payroll successfully created.")

    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {str(e)}")


def calculate_withholding_tax(gross_pay):
    # Tax rates and brackets for 2024
    tax_brackets = [
        (250000, 0.20),
        (400000, 0.25),
        (800000, 0.30),
        (2000000, 0.32),
        (8000000, 0.35),
        (16000000, 0.40),
        (32000000, 0.42),
        (64000000, 0.45),
        (64000000, 0.50)  # For incomes above 64M
    ]

    # Compute withholding tax
    tax_due = 0
    taxable_income = gross_pay * 12  # Annualized gross pay assuming monthly salary

    for i, (threshold, rate) in enumerate(tax_brackets):
        if taxable_income <= threshold:
            tax_due += taxable_income * rate
            break
        else:
            if i == len(tax_brackets) - 1:
                # Apply the highest tax rate for incomes above the highest threshold
                tax_due += (taxable_income - tax_brackets[-1][0]) * tax_brackets[-1][1]
            else:
                # Apply the tax rate for this bracket
                tax_due += (threshold - tax_brackets[i - 1][0]) * rate

    # Convert annual tax due to monthly withholding tax
    withholding_tax = tax_due / 12

    return withholding_tax


# Function to calculate other deductions
def calculate_other_deductions():
    # Your logic to calculate other deductions
    pass


# Function to get the start date of the payroll period
def get_period_start():
    today = datetime.now()
    if today.day <= 15:
        return today.replace(day=1)
    else:
        return today.replace(day=16)


# Function to get the end date of the payroll period
def get_period_end():
    today = datetime.now()
    last_day_of_month = calendar.monthrange(today.year, today.month)[1]
    if today.day <= 15:
        return today.replace(day=15)
    else:
        return today.replace(day=last_day_of_month)


def thirteenth_month_pay_computation(employee):
    today = date.today()
    thirteenth_month_pay = 0
    # Check if the current date is December 20th
    if today.month == 12 and today.day == 20:
        # Calculate total basic salary earned during the year
        total_base_salary = calculate_total_base_salary(employee)

        # Calculate thirteenth month pay
        thirteenth_month_pay = total_base_salary / 12

    return thirteenth_month_pay


def calculate_total_base_salary(employee):
    # Get the current year
    current_year = date.today().year

    # Query all the payrolls for the employee within the current year
    payrolls_within_year = Payroll.query.filter_by(employee_id=employee.employee_id) \
        .filter(Payroll.period_start >= date(current_year, 1, 1)) \
        .filter(Payroll.period_end <= date(current_year, 12, 31)) \
        .all()

    # Sum up the base_salary from all the payrolls
    total_basic_salary = sum(payroll.base_salary for payroll in payrolls_within_year)

    return total_basic_salary


# Create a scheduler
scheduler = BackgroundScheduler()

# Add the payroll generation job to run on the 10th and 25th of every month
scheduler.add_job(generate_payroll, 'cron', day='5,20')
