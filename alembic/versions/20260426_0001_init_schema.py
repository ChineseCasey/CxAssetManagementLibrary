"""init schema

Revision ID: 20260426_0001
Revises:
Create Date: 2026-04-26 00:50:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260426_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "libraries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("root_path", sa.Text(), nullable=False),
        sa.Column("config_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_tags_name"), "tags", ["name"], unique=False)

    op.create_table(
        "tree_nodes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("library_id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("depth", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["library_id"], ["libraries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["tree_nodes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("library_id", "parent_id", "name", name="uq_tree_node_sibling_name"),
    )
    op.create_index(op.f("ix_tree_nodes_library_id"), "tree_nodes", ["library_id"], unique=False)
    op.create_index(op.f("ix_tree_nodes_parent_id"), "tree_nodes", ["parent_id"], unique=False)
    op.create_index(op.f("ix_tree_nodes_name"), "tree_nodes", ["name"], unique=False)
    op.create_index(op.f("ix_tree_nodes_path"), "tree_nodes", ["path"], unique=False)

    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("library_id", sa.Integer(), nullable=False),
        sa.Column("node_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["library_id"], ["libraries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["node_id"], ["tree_nodes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("library_id", "node_id", "name", name="uq_asset_per_node_name"),
    )
    op.create_index(op.f("ix_assets_library_id"), "assets", ["library_id"], unique=False)
    op.create_index(op.f("ix_assets_node_id"), "assets", ["node_id"], unique=False)
    op.create_index(op.f("ix_assets_name"), "assets", ["name"], unique=False)

    op.create_table(
        "sync_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("library_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scanned_nodes", sa.Integer(), nullable=False),
        sa.Column("scanned_assets", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["library_id"], ["libraries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sync_runs_library_id"), "sync_runs", ["library_id"], unique=False)

    op.create_table(
        "file_refs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("file_role", sa.String(length=32), nullable=False),
        sa.Column("relative_path", sa.Text(), nullable=False),
        sa.Column("size", sa.BigInteger(), nullable=True),
        sa.Column("mtime", sa.DateTime(timezone=True), nullable=True),
        sa.Column("hash", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("asset_id", "relative_path", name="uq_asset_relative_path"),
    )
    op.create_index(op.f("ix_file_refs_asset_id"), "file_refs", ["asset_id"], unique=False)

    op.create_table(
        "asset_tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("asset_id", "tag_id", name="uq_asset_tag_pair"),
    )
    op.create_index(op.f("ix_asset_tags_asset_id"), "asset_tags", ["asset_id"], unique=False)
    op.create_index(op.f("ix_asset_tags_tag_id"), "asset_tags", ["tag_id"], unique=False)

    op.create_table(
        "sync_errors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sync_run_id", sa.Integer(), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("path", sa.Text(), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["sync_run_id"], ["sync_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sync_errors_sync_run_id"), "sync_errors", ["sync_run_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_sync_errors_sync_run_id"), table_name="sync_errors")
    op.drop_table("sync_errors")

    op.drop_index(op.f("ix_asset_tags_tag_id"), table_name="asset_tags")
    op.drop_index(op.f("ix_asset_tags_asset_id"), table_name="asset_tags")
    op.drop_table("asset_tags")

    op.drop_index(op.f("ix_file_refs_asset_id"), table_name="file_refs")
    op.drop_table("file_refs")

    op.drop_index(op.f("ix_sync_runs_library_id"), table_name="sync_runs")
    op.drop_table("sync_runs")

    op.drop_index(op.f("ix_assets_name"), table_name="assets")
    op.drop_index(op.f("ix_assets_node_id"), table_name="assets")
    op.drop_index(op.f("ix_assets_library_id"), table_name="assets")
    op.drop_table("assets")

    op.drop_index(op.f("ix_tree_nodes_path"), table_name="tree_nodes")
    op.drop_index(op.f("ix_tree_nodes_name"), table_name="tree_nodes")
    op.drop_index(op.f("ix_tree_nodes_parent_id"), table_name="tree_nodes")
    op.drop_index(op.f("ix_tree_nodes_library_id"), table_name="tree_nodes")
    op.drop_table("tree_nodes")

    op.drop_index(op.f("ix_tags_name"), table_name="tags")
    op.drop_table("tags")

    op.drop_table("libraries")
