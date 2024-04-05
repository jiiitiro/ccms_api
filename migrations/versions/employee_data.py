"""empty message

Revision ID: 8013dd773e26
Revises: 
Create Date: 2024-04-06 00:41:06.947280

"""
from alembic import op
import sqlalchemy as sa
from passlib.hash import pbkdf2_sha256


# revision identifiers, used by Alembic.
revision = 'employee_data'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Hash passwords
    hashed_passwords = [
        pbkdf2_sha256.hash('rjcabrera1234'),
        pbkdf2_sha256.hash('102002Del'),
        pbkdf2_sha256.hash('061703DS'),
        pbkdf2_sha256.hash('07162002xy'),
        pbkdf2_sha256.hash('agentx44')
    ]

    # Insert data into employee_tbl
    op.execute("""
            INSERT INTO employee_tbl 
                (first_name, middle_name, last_name, address, email, password, phone, position, hire_date, daily_rate, is_active, email_confirm, de_minimis)
            VALUES 
                ('Rachel Jhoy', 'Llena', 'Cabrera', '11 Ibayo II Brgy. Bagbag Nova. Q.C', 'cabrera.racheljhoy.02202002@gmail', '{}', '09667721260', 'Housekeeper', '2024-01-05', 610, TRUE, TRUE, 0),
                ('Giebert', '', 'Reyes Delotavo', '2340 Kapatiran St. Brgy Comm. Q.C.', 'delotavo.giebert.10202002@gmail.com', '{}', '09091706139', 'Housekeeper', '2024-01-05', 610, TRUE, TRUE, 0),
                ('Cris Christian', '', 'Dalag Delos Santos', 'Blk 5 Lot 5 Orient Street San Agustin, Quezon City', 'delossantos.cris.06172003@gmail.com', '{}', '09458904624', 'Housekeeper', '2024-01-05', 610, TRUE, TRUE, 0),
                ('Allyson', '', 'Eser Canales', '21 sta veronica st. Brgy gulod novaliches, Quezon City', 'canalesallyson07162002@gmail.com', '{}', '09459756018', 'Housekeeper', '2024-01-05', 610, TRUE, TRUE, 0),
                ('Dane Justine', '', 'Calura Cabaya', 'Barangay Salvacion Laloma, Quezon City', 'cabaya.danejustine.102801@gmail.com', '{}', '09687685698', 'Electrician', '2024-01-05', 610, TRUE, TRUE, 0)
        """.format(hashed_passwords[0], hashed_passwords[1], hashed_passwords[2], hashed_passwords[3],
                   hashed_passwords[4]))

    # Insert data into schedule_tbl
    op.execute("""
            INSERT INTO schedule_tbl 
                (employee_id, start_time, end_time, day_off)
            SELECT 
                e.employee_id,
                CASE e.first_name
                    WHEN 'Rachel Jhoy' THEN '08:00:00'::time
                    WHEN 'Giebert' THEN '08:00:00'::time
                    WHEN 'Cris Christian' THEN '08:00:00'::time
                    WHEN 'Allyson' THEN '08:00:00'::time
                    WHEN 'Dane Justine' THEN '08:00:00'::time
                END AS start_time,
                CASE e.first_name
                    WHEN 'Rachel Jhoy' THEN '17:00:00'::time
                    WHEN 'Giebert' THEN '17:00:00'::time
                    WHEN 'Cris Christian' THEN '17:00:00'::time
                    WHEN 'Allyson' THEN '17:00:00'::time
                    WHEN 'Dane Justine' THEN '17:00:00'::time
                END AS end_time,
                CASE e.first_name
                    WHEN 'Rachel Jhoy' THEN 'Monday'
                    WHEN 'Giebert' THEN 'Tuesday'
                    WHEN 'Cris Christian' THEN 'Wednesday'
                    WHEN 'Allyson' THEN 'Thursday'
                    WHEN 'Dane Justine' THEN 'Friday'
                END AS day_off
            FROM 
                employee_tbl e
            WHERE 
                e.first_name IN ('Rachel Jhoy', 'Giebert', 'Cris Christian', 'Allyson', 'Dane Justine')
        """)


def downgrade():
    pass

