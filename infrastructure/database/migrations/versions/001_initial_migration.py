"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Create decks table
    op.create_table(
        'decks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_decks_user_id', 'decks', ['user_id'])

    # Create cards table
    op.create_table(
        'cards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('deck_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('front', sa.Text(), nullable=False),
        sa.Column('back', sa.Text(), nullable=False),
        sa.Column('audio_url', sa.String(500), nullable=True),
        sa.Column('stability', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('difficulty', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('ease_factor', sa.Float(), nullable=False, server_default='2.5'),
        sa.Column('interval', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('review_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_review', sa.DateTime(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['deck_id'], ['decks.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_cards_deck_id', 'cards', ['deck_id'])
    op.create_index('ix_cards_due_date', 'cards', ['due_date'])

    # Create study_sessions table
    op.create_table(
        'study_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('deck_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mode', sa.String(50), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('cards_studied', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cards_correct', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cards_incorrect', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['deck_id'], ['decks.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_study_sessions_user_id', 'study_sessions', ['user_id'])
    op.create_index('ix_study_sessions_deck_id', 'study_sessions', ['deck_id'])


def downgrade() -> None:
    op.drop_index('ix_study_sessions_deck_id', table_name='study_sessions')
    op.drop_index('ix_study_sessions_user_id', table_name='study_sessions')
    op.drop_table('study_sessions')
    op.drop_index('ix_cards_due_date', table_name='cards')
    op.drop_index('ix_cards_deck_id', table_name='cards')
    op.drop_table('cards')
    op.drop_index('ix_decks_user_id', table_name='decks')
    op.drop_table('decks')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
