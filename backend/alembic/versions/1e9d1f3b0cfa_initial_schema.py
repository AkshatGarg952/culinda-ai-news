"""initial schema

Revision ID: 1e9d1f3b0cfa
Revises: 
Create Date: 2026-03-18 22:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector.sqlalchemy

revision: str = '1e9d1f3b0cfa'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')

    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('admin', 'user', name='userrole'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    op.create_table('sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('rss', 'api', 'scrape', name='sourcetype'), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url')
    )
    
    op.create_table('news_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_duplicate', sa.Boolean(), nullable=True),
        sa.Column('impact_score', sa.Float(), nullable=True),
        sa.Column('cluster_id', sa.String(), nullable=True),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(dim=1536), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url')
    )
    
    op.create_table('favorites',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('news_item_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['news_item_id'], ['news_items.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('broadcast_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('favorite_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('platform', sa.Enum('email', 'linkedin', 'whatsapp', 'blog', 'newsletter', name='platformtype'), nullable=False),
        sa.Column('status', sa.Enum('sent', 'failed', 'pending', name='broadcaststatus'), nullable=True),
        sa.Column('content_snapshot', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['favorite_id'], ['favorites.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('broadcast_logs')
    op.drop_table('favorites')
    op.drop_table('news_items')
    op.drop_table('sources')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS broadcaststatus;')
    op.execute('DROP TYPE IF EXISTS platformtype;')
    op.execute('DROP TYPE IF EXISTS sourcetype;')
    op.execute('DROP TYPE IF EXISTS userrole;')
    op.execute('DROP EXTENSION IF EXISTS vector;')
