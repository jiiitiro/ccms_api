"""empty message

Revision ID: 8013dd773e26
Revises: 
Create Date: 2024-04-06 00:41:06.947280

"""
from alembic import op
import sqlalchemy as sa
from passlib.hash import pbkdf2_sha256

# revision identifiers, used by Alembic.
revision = 'customer_data'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Insert data into customer_tbl
    customer_data = [
        ('Kathleen Mae', 'Agni', 'Pecoro', 'pecoro.kathleenmae.01312003@gmail.com', pbkdf2_sha256.hash('_kath8914'),
         '09776723516', True, True),
        (
        'Ashley Nicole', 'Roble', 'Lagleva', 'lagleva.ashleynicole.02042002@gmail.com', pbkdf2_sha256.hash('ashnic@04'),
        '09672372219', True, True),
        ('Maria Alesa', 'Seroya', 'Tabios', 'tabios.mariaalesa.march102003@gmail.com', pbkdf2_sha256.hash('alesa10-'),
         '09306193749', True, True),
        ('Kathleen', 'Basul', 'Balberan', 'balberan.kathleen.11092001@gmail.com', pbkdf2_sha256.hash('ezreal09'),
         '09369226800', True, True),
        ('Janiela', 'Auxilio', 'Tablizo', 'tablizo.janiela.12172002@gmail.com', pbkdf2_sha256.hash('jaja1234'),
         '09691403344', True, True)
    ]

    for data in customer_data:
        op.execute(f"""
                INSERT INTO customer_tbl (first_name, middle_name, last_name, email, password, phone, is_active, email_confirm)
                VALUES 
                    ('{data[0]}', '{data[1]}', '{data[2]}', '{data[3]}', '{data[4]}', '{data[5]}', {data[6]}, {data[7]})
            """)

    op.execute("""
            INSERT INTO customer_address
                (customer_id, houseno_street, barangay, city, region, zipcode)
            SELECT 
                c.customer_id,
                CASE c.first_name
                    WHEN 'Kathleen Mae' THEN '#2 Felipe Street'
                    WHEN 'Ashley Nicole' THEN '#16 Daisy Street'
                    WHEN 'Maria Alesa' THEN 'Blk 5 Lot 6 CMP1 Sitio'
                    WHEN 'Kathleen' THEN '#21 Ukay Street'
                    WHEN 'Janiela' THEN 'Ibayo'
                END AS houseno_street,
                CASE c.first_name
                    WHEN 'Kathleen Mae' THEN 'Damayan'
                    WHEN 'Ashley Nicole' THEN 'N.S. Amoranto'
                    WHEN 'Maria Alesa' THEN 'Baesa'
                    WHEN 'Kathleen' THEN 'Culiat'
                    WHEN 'Janiela' THEN 'Bagbag'
                END AS barangay,
                CASE c.first_name
                    WHEN 'Kathleen Mae' THEN 'Quezon City'
                    WHEN 'Ashley Nicole' THEN 'Quezon City'
                    WHEN 'Maria Alesa' THEN 'Quezon City'
                    WHEN 'Kathleen' THEN 'Quezon City'
                    WHEN 'Janiela' THEN 'Quezon City'
                END AS city,
                CASE c.first_name
                    WHEN 'Kathleen Mae' THEN 'Metro Manila'
                    WHEN 'Ashley Nicole' THEN 'Metro Manila'
                    WHEN 'Maria Alesa' THEN 'Metro Manila'
                    WHEN 'Kathleen' THEN 'Metro Manila'
                    WHEN 'Janiela' THEN 'Metro Manila'
                END AS region,
                CASE c.first_name
                    WHEN 'Kathleen Mae' THEN '1105'
                    WHEN 'Ashley Nicole' THEN '1801'
                    WHEN 'Maria Alesa' THEN '2105'
                    WHEN 'Kathleen' THEN '1112'
                    WHEN 'Janiela' THEN '1801'
                END AS zipcode
            FROM 
                customer_tbl c
            WHERE 
                c.first_name IN ('Kathleen Mae', 'Ashley Nicole', 'Maria Alesa', 'Kathleen', 'Janiela')
        """)
def downgrade():
    # Delete data from customer_tbl
    op.execute("""
        DELETE FROM customer_tbl
        WHERE email IN (
            'pecoro.kathleenmae.01312003@gmail.com',
            'lagleva.ashleynicole.02042002@gmail.com',
            'tabios.mariaalesa.march102003@gmail.com',
            'balberan.kathleen.11092001@gmail.com',
            'tablizo.janiela.12172002@gmail.com'
        )
    """)

    # Delete data from customer_address_tbl
    op.execute("""
        DELETE FROM customer_address_tbl
        WHERE customer_id IN (
            SELECT customer_id FROM customer_tbl
            WHERE email IN (
                'pecoro.kathleenmae.01312003@gmail.com',
                'lagleva.ashleynicole.02042002@gmail.com',
                'tabios.mariaalesa.march102003@gmail.com',
                'balberan.kathleen.11092001@gmail.com',
                'tablizo.janiela.12172002@gmail.com'
            )
        )
    """)
