from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cxasset_api.db import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Library(TimestampMixin, Base):
    __tablename__ = "libraries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    root_path: Mapped[str] = mapped_column(Text, nullable=False)
    config_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    nodes: Mapped[list["TreeNode"]] = relationship(back_populates="library", cascade="all, delete-orphan")
    assets: Mapped[list["Asset"]] = relationship(back_populates="library", cascade="all, delete-orphan")


class TreeNode(TimestampMixin, Base):
    __tablename__ = "tree_nodes"
    __table_args__ = (
        UniqueConstraint("library_id", "parent_id", "name", name="uq_tree_node_sibling_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    library_id: Mapped[int] = mapped_column(ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("tree_nodes.id", ondelete="CASCADE"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    path: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    library: Mapped["Library"] = relationship(back_populates="nodes")
    parent: Mapped["TreeNode | None"] = relationship(remote_side=[id], back_populates="children")
    children: Mapped[list["TreeNode"]] = relationship(back_populates="parent")
    assets: Mapped[list["Asset"]] = relationship(back_populates="node")


class UserFavorite(TimestampMixin, Base):
    """Single-user favorites; stored in API DB (desktop and future clients)."""

    __tablename__ = "user_favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )

    asset: Mapped["Asset"] = relationship()


class Asset(TimestampMixin, Base):
    __tablename__ = "assets"
    __table_args__ = (
        UniqueConstraint("library_id", "node_id", "name", name="uq_asset_per_node_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    library_id: Mapped[int] = mapped_column(ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id: Mapped[int | None] = mapped_column(ForeignKey("tree_nodes.id", ondelete="SET NULL"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    library: Mapped["Library"] = relationship(back_populates="assets")
    node: Mapped["TreeNode | None"] = relationship(back_populates="assets")
    file_refs: Mapped[list["FileRef"]] = relationship(back_populates="asset", cascade="all, delete-orphan")
    tags: Mapped[list["Tag"]] = relationship(secondary="asset_tags", back_populates="assets")


class FileRef(TimestampMixin, Base):
    __tablename__ = "file_refs"
    __table_args__ = (
        UniqueConstraint("asset_id", "relative_path", name="uq_asset_relative_path"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    file_role: Mapped[str] = mapped_column(String(32), nullable=False, default="aux")
    relative_path: Mapped[str] = mapped_column(Text, nullable=False)
    size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    mtime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    hash: Mapped[str | None] = mapped_column(String(128), nullable=True)

    asset: Mapped["Asset"] = relationship(back_populates="file_refs")


class Tag(TimestampMixin, Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    assets: Mapped[list["Asset"]] = relationship(secondary="asset_tags", back_populates="tags")


class AssetTag(Base):
    __tablename__ = "asset_tags"
    __table_args__ = (
        UniqueConstraint("asset_id", "tag_id", name="uq_asset_tag_pair"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True)


class SyncRun(Base):
    __tablename__ = "sync_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    library_id: Mapped[int] = mapped_column(ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="running")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scanned_nodes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    scanned_assets: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    errors: Mapped[list["SyncError"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class SyncError(Base):
    __tablename__ = "sync_errors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sync_run_id: Mapped[int] = mapped_column(ForeignKey("sync_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default="error")
    path: Mapped[str | None] = mapped_column(Text, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    run: Mapped["SyncRun"] = relationship(back_populates="errors")
