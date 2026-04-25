from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from cxasset_api.config import settings
from cxasset_api.db import SessionLocal
from cxasset_api.models import Asset, FileRef, Library, SyncError, SyncRun, TreeNode


@dataclass
class SyncStats:
    library_name: str
    scanned_nodes: int = 0
    scanned_assets: int = 0
    error_count: int = 0


def _is_visible_dir(path: Path) -> bool:
    return path.is_dir() and not path.name.startswith(".")


def _is_visible_file(path: Path) -> bool:
    return path.is_file() and not path.name.startswith(".")


def parse_library_roots(raw_value: str) -> list[Path]:
    roots: list[Path] = []
    for item in raw_value.split(";"):
        cleaned = item.strip()
        if not cleaned:
            continue
        roots.append(Path(cleaned).resolve())
    return roots


def run_full_sync(library_roots: Iterable[Path] | None = None) -> list[SyncStats]:
    roots = list(library_roots) if library_roots is not None else parse_library_roots(settings.library_roots)
    results: list[SyncStats] = []
    with SessionLocal() as session:
        for root in roots:
            results.append(_sync_single_library(session, root))
        session.commit()
    return results


def _sync_single_library(session: Session, root: Path) -> SyncStats:
    library_name = root.name
    stats = SyncStats(library_name=library_name)
    library = _get_or_create_library(session, library_name=library_name, root_path=str(root))

    sync_run = SyncRun(library_id=library.id, status="running")
    session.add(sync_run)
    session.flush()

    if not root.exists() or not root.is_dir():
        _record_error(session, sync_run.id, f"library root not found or not directory: {root}")
        sync_run.status = "failed"
        sync_run.finished_at = datetime.now(timezone.utc)
        stats.error_count += 1
        return stats

    try:
        _clear_library_projection(session, library.id)
        node_index = _build_tree_nodes(session, library.id, root, stats)
        _build_assets_and_files(session, library.id, root, node_index, sync_run.id, stats)
        sync_run.status = "success"
    except Exception as exc:  # pragma: no cover - defensive guard for task state
        _record_error(session, sync_run.id, f"unexpected sync failure: {exc}")
        sync_run.status = "failed"
        stats.error_count += 1
    finally:
        sync_run.scanned_nodes = stats.scanned_nodes
        sync_run.scanned_assets = stats.scanned_assets
        sync_run.finished_at = datetime.now(timezone.utc)

    return stats


def _get_or_create_library(session: Session, library_name: str, root_path: str) -> Library:
    stmt = select(Library).where(Library.name == library_name)
    library = session.scalar(stmt)
    if library is None:
        library = Library(name=library_name, root_path=root_path)
        session.add(library)
        session.flush()
    else:
        library.root_path = root_path
    return library


def _clear_library_projection(session: Session, library_id: int) -> None:
    session.execute(delete(FileRef).where(FileRef.asset_id.in_(select(Asset.id).where(Asset.library_id == library_id))))
    session.execute(delete(Asset).where(Asset.library_id == library_id))
    session.execute(delete(TreeNode).where(TreeNode.library_id == library_id))


def _build_tree_nodes(session: Session, library_id: int, root: Path, stats: SyncStats) -> dict[Path, TreeNode]:
    node_index: dict[Path, TreeNode] = {}
    for directory in sorted([p for p in root.rglob("*") if _is_visible_dir(p)]):
        relative = directory.relative_to(root)
        parent_relative = relative.parent if relative.parent != Path(".") else None
        parent_node = node_index.get(parent_relative) if parent_relative is not None else None

        node = TreeNode(
            library_id=library_id,
            parent_id=parent_node.id if parent_node else None,
            name=directory.name,
            path=relative.as_posix(),
            depth=len(relative.parts),
            sort_order=0,
        )
        session.add(node)
        session.flush()
        node_index[relative] = node
        stats.scanned_nodes += 1
    return node_index


def _build_assets_and_files(
    session: Session,
    library_id: int,
    root: Path,
    node_index: dict[Path, TreeNode],
    sync_run_id: int,
    stats: SyncStats,
) -> None:
    for directory in sorted([p for p in root.rglob("*") if _is_visible_dir(p)]):
        child_dirs = [p for p in directory.iterdir() if _is_visible_dir(p)]
        if child_dirs:
            continue

        relative = directory.relative_to(root)
        current_node = node_index.get(relative)

        asset = Asset(
            library_id=library_id,
            node_id=current_node.id if current_node else None,
            name=directory.name,
            display_name=directory.name,
            status="active",
        )
        session.add(asset)
        session.flush()
        stats.scanned_assets += 1

        for file_path in sorted([p for p in directory.iterdir() if _is_visible_file(p)]):
            stat = file_path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            relative_path = file_path.relative_to(root).as_posix()
            role = "thumbnail" if file_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"} else "aux"

            file_ref = FileRef(
                asset_id=asset.id,
                file_role=role,
                relative_path=relative_path,
                size=stat.st_size,
                mtime=mtime,
                hash=None,
            )
            session.add(file_ref)


def _record_error(session: Session, sync_run_id: int, message: str, path: str | None = None) -> None:
    session.add(SyncError(sync_run_id=sync_run_id, severity="error", path=path, message=message))
