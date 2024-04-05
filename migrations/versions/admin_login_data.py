"""empty message

Revision ID: 8013dd773e26
Revises: 
Create Date: 2024-04-06 00:41:06.947280

"""
from alembic import op
import sqlalchemy as sa
from passlib.hash import pbkdf2_sha256


# revision identifiers, used by Alembic.
revision = 'admin_login_data'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():

    # Insert data into the inventory_admin_login_tbl
    op.execute(
        """
        INSERT INTO inventory_admin_login_tbl (name, email, password, role, is_active, email_confirm)
        VALUES ('Alvin Galit', 'lvngalit26@gmail.com', '{}', 'Admin', TRUE, TRUE)
        """.format(pbkdf2_sha256.hash('12345678'))
    )

    # Insert data into the payroll_admin_login_tbl
    op.execute(
        """
        INSERT INTO payroll_admin_login_tbl (name, email, password, role, is_active, email_confirm)
        VALUES 
            ('Julito Tiro', 'tiro.julitoiii.14@gmail.com', '{}', 'Admin', TRUE, TRUE),
            ('Mark Aropon', 'markaropon@gmail.com', '{}', 'Admin', TRUE, TRUE),
            ('Mark Arca', 'markgervicarca@gmail.com', '{}', 'Admin', TRUE, TRUE)
        """.format(pbkdf2_sha256.hash("1234Julito"),
                   pbkdf2_sha256.hash("laffitte1234"),
                   pbkdf2_sha256.hash("qwerty1234"))
    )

    # Insert data into the payroll_admin_login_tbl
    op.execute(
        """
        INSERT INTO customer_admin_login_tbl (name, email, password, role, is_active, email_confirm)
        VALUES 
            ('Arthur Villanueva', 'villanueva.arthurjerard.06112003@gmail.com', '{}', 'Admin', TRUE, TRUE)
        """.format(pbkdf2_sha256.hash("12345Arthur"))
    )

    # Insert data into the payroll_admin_login_tbl
    op.execute(
        """
        INSERT INTO superadmin_login_tbl (name, email, password, role, is_active, email_confirm)
        VALUES 
            ('Julito Tiro', 'tiro.julitoiii.14@gmail.com', '{}', 'Admin', TRUE, TRUE)
        """.format(pbkdf2_sha256.hash("051421Superadmin"))
    )


def downgrade():
    pass

