"""added some action tables

Revision ID: af79fd9d5f90
Revises: 36b472f93b45
Create Date: 2022-07-18 18:41:06.190715

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "af79fd9d5f90"
down_revision = "36b472f93b45"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "message_delete_actions",
        sa.Column("id", sa.BigInteger(), nullable=False, auto_increment=True),
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("message_id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "message_send_actions",
        sa.Column("id", sa.BigInteger(), nullable=False, auto_increment=True),
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("message_send_actions")
    op.drop_table("message_delete_actions")
    # ### end Alembic commands ###
