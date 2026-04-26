from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path, PurePosixPath
import shutil
import time
from typing import Literal
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import asc, desc, func, or_, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased, selectinload

from cxasset_api.config import settings
from cxasset_api.db import SessionLocal
from cxasset_api.models import Asset, FileRef, Library, TreeNode, UserFavorite

app = FastAPI(title=settings.app_name, version=settings.app_version)
ANTD_WEB_DIR = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if ANTD_WEB_DIR.exists():
    app.mount("/antd", StaticFiles(directory=str(ANTD_WEB_DIR), html=True), name="antd")
logger = logging.getLogger("cxasset.api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class LibraryItem(BaseModel):
    id: int
    name: str
    root_path: str
    created_at: datetime
    updated_at: datetime


class LibraryListResponse(BaseModel):
    items: list[LibraryItem]
    meta: PageMeta


class TreeNodeItem(BaseModel):
    id: int
    library_id: int
    parent_id: int | None
    name: str
    path: str
    depth: int


class TreeNodeListResponse(BaseModel):
    items: list[TreeNodeItem]
    meta: PageMeta


class AssetItem(BaseModel):
    id: int
    library_id: int
    node_id: int | None
    node_path: str | None = None
    name: str
    display_name: str | None
    status: str
    thumbnail_relative_path: str | None = None
    file_format: str | None = None
    created_at: datetime
    updated_at: datetime


class AssetListResponse(BaseModel):
    items: list[AssetItem]
    meta: PageMeta


class FileRefItem(BaseModel):
    id: int
    file_role: str
    relative_path: str
    size: int | None
    mtime: datetime | None
    hash: str | None


class AssetDetailResponse(BaseModel):
    id: int
    library_id: int
    node_id: int | None
    name: str
    display_name: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    files: list[FileRefItem]


class CreateNodeRequest(BaseModel):
    library_id: int
    parent_id: int | None = None
    parent_path: str | None = None
    name: str


class CreateNodeResponse(BaseModel):
    id: int
    library_id: int
    parent_id: int | None
    name: str
    path: str
    depth: int


class CreateAssetResponse(BaseModel):
    id: int
    library_id: int
    node_id: int
    name: str
    files: list[FileRefItem]


class FavoritesListResponse(BaseModel):
    asset_ids: list[int]


def _error_payload(code: str, message: str, request_id: str) -> dict:
    return {"error": {"code": code, "message": message, "request_id": request_id}}


def _build_page_meta(page: int, page_size: int, total: int) -> PageMeta:
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PageMeta(page=page, page_size=page_size, total=total, total_pages=total_pages)


def _build_thumbnail_map(session, asset_ids: list[int]) -> dict[int, str]:
    if not asset_ids:
        return {}
    rows = session.scalars(
        select(FileRef)
        .where(
            FileRef.asset_id.in_(asset_ids),
            or_(
                FileRef.file_role == "thumbnail",
                FileRef.relative_path.ilike("%.jpg"),
                FileRef.relative_path.ilike("%.jpeg"),
                FileRef.relative_path.ilike("%.png"),
                FileRef.relative_path.ilike("%.webp"),
            ),
        )
        .order_by(FileRef.asset_id.asc(), FileRef.id.asc())
    ).all()
    thumbnail_map: dict[int, str] = {}
    for row in rows:
        if row.asset_id not in thumbnail_map:
            thumbnail_map[row.asset_id] = row.relative_path
    return thumbnail_map


def _build_file_format_map(session, asset_ids: list[int]) -> dict[int, str]:
    if not asset_ids:
        return {}
    rows = session.scalars(
        select(FileRef).where(FileRef.asset_id.in_(asset_ids)).order_by(FileRef.asset_id.asc(), FileRef.id.asc())
    ).all()
    format_map: dict[int, str] = {}
    for row in rows:
        ext = Path(row.relative_path).suffix.upper().lstrip(".")
        if not ext:
            continue
        # Prefer explicit primary file, otherwise first non-image file, then fallback to first extension.
        if row.file_role == "primary":
            format_map[row.asset_id] = ext
            continue
        current = format_map.get(row.asset_id)
        if ext not in {"JPG", "JPEG", "PNG", "WEBP"}:
            format_map[row.asset_id] = ext
            continue
        if current is None:
            format_map[row.asset_id] = ext
    return format_map


def _build_node_path_map(session, node_ids: list[int]) -> dict[int, str]:
    if not node_ids:
        return {}
    rows = session.scalars(select(TreeNode).where(TreeNode.id.in_(node_ids))).all()
    return {row.id: row.path for row in rows}


def _verify_media_token(
    authorization: str | None = Header(default=None),
    x_api_token: str | None = Header(default=None),
) -> None:
    expected = settings.media_token.strip()
    bearer = f"Bearer {expected}"
    if authorization == bearer or x_api_token == expected:
        return
    raise HTTPException(status_code=401, detail="unauthorized")


def _sanitize_relative_path(raw_relative_path: str) -> str:
    normalized = raw_relative_path.replace("\\", "/").strip("/")
    if not normalized:
        raise HTTPException(status_code=400, detail="invalid relative path")
    parts = PurePosixPath(normalized).parts
    if any(part in {"..", "."} for part in parts):
        raise HTTPException(status_code=400, detail="invalid relative path")
    return normalized


def _safe_library_join(library_root: str, relative_path: str) -> Path:
    root = Path(library_root).resolve()
    target = (root / relative_path).resolve()
    if root not in target.parents and target != root:
        raise HTTPException(status_code=400, detail="invalid target path")
    return target


def _get_or_create_node_chain(session, library_id: int, parent_path: str) -> TreeNode | None:
    clean = parent_path.strip().replace("\\", "/").strip("/")
    if not clean:
        return None
    parts = [x for x in clean.split("/") if x]
    current_parent_id: int | None = None
    current_path = ""
    current_node: TreeNode | None = None
    for idx, part in enumerate(parts):
        current_path = f"{current_path}/{part}" if current_path else part
        node = session.scalar(
            select(TreeNode).where(
                TreeNode.library_id == library_id,
                TreeNode.parent_id == current_parent_id,
                TreeNode.name == part,
            )
        )
        if node is None:
            node = TreeNode(
                library_id=library_id,
                parent_id=current_parent_id,
                name=part,
                path=current_path,
                depth=idx + 1,
                sort_order=0,
            )
            session.add(node)
            session.flush()
        current_node = node
        current_parent_id = node.id
    return current_node


@app.get("/", include_in_schema=False)
def home() -> RedirectResponse:
    return RedirectResponse(url=settings.frontend_url)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    started_at = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = int((time.perf_counter() - started_at) * 1000)
        logger.exception(
            "request_failed request_id=%s method=%s path=%s elapsed_ms=%s",
            request_id,
            request.method,
            request.url.path,
            elapsed_ms,
        )
        raise
    elapsed_ms = int((time.perf_counter() - started_at) * 1000)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_done request_id=%s method=%s path=%s status=%s elapsed_ms=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", str(uuid4()))
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload("HTTP_ERROR", str(exc.detail), request_id),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", str(uuid4()))
    logger.exception("unhandled_exception request_id=%s", request_id)
    return JSONResponse(
        status_code=500,
        content=_error_payload("INTERNAL_ERROR", "internal server error", request_id),
    )


@app.get("/health")
def health() -> dict:
    with SessionLocal() as session:
        session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}


@app.get("/version")
def version() -> dict:
    return {"app": settings.app_name, "version": settings.app_version}


@app.get("/favorites", response_model=FavoritesListResponse)
def list_favorites(
    library_id: int | None = Query(default=None, description="Only return ids for this library, if set"),
) -> FavoritesListResponse:
    with SessionLocal() as session:
        if library_id is None:
            rows = session.scalars(select(UserFavorite.asset_id).order_by(UserFavorite.asset_id.asc())).all()
        else:
            rows = session.scalars(
                select(UserFavorite.asset_id)
                .join(Asset, Asset.id == UserFavorite.asset_id)
                .where(Asset.library_id == library_id)
                .order_by(UserFavorite.asset_id.asc())
            ).all()
    return FavoritesListResponse(asset_ids=[int(x) for x in rows])


@app.post("/favorites/{asset_id}", status_code=201)
def add_favorite(asset_id: int) -> dict:
    with SessionLocal() as session:
        asset = session.get(Asset, asset_id)
        if asset is None:
            raise HTTPException(status_code=404, detail="asset not found")
        existing = session.scalar(select(UserFavorite).where(UserFavorite.asset_id == asset_id))
        if existing is not None:
            return {"ok": True, "asset_id": asset_id, "existed": True}
        session.add(UserFavorite(asset_id=asset_id))
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
        return {"ok": True, "asset_id": asset_id, "existed": False}


@app.delete("/favorites/{asset_id}", status_code=204)
def remove_favorite(asset_id: int) -> None:
    with SessionLocal() as session:
        row = session.scalar(select(UserFavorite).where(UserFavorite.asset_id == asset_id))
        if row is not None:
            session.delete(row)
            session.commit()


@app.get("/metrics")
def metrics() -> dict:
    with SessionLocal() as session:
        libraries = session.scalar(select(func.count(Library.id))) or 0
        assets = session.scalar(select(func.count(Asset.id))) or 0
        files = session.scalar(select(func.count(FileRef.id))) or 0
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "libraries": libraries,
        "assets": assets,
        "file_refs": files,
    }


@app.get("/libraries", response_model=LibraryListResponse)
def list_libraries(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
) -> LibraryListResponse:
    offset = (page - 1) * page_size
    with SessionLocal() as session:
        total = session.scalar(select(func.count(Library.id))) or 0
        rows = session.scalars(
            select(Library).order_by(Library.id.asc()).offset(offset).limit(page_size)
        ).all()
    return LibraryListResponse(
        items=[
            LibraryItem(
                id=row.id,
                name=row.name,
                root_path=row.root_path,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ],
        meta=_build_page_meta(page, page_size, total),
    )


@app.get("/libraries/{library_id}/tree", response_model=TreeNodeListResponse)
def list_tree_nodes(
    library_id: int,
    parent_id: int | None = Query(default=None),
    include_asset_nodes: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
) -> TreeNodeListResponse:
    offset = (page - 1) * page_size
    with SessionLocal() as session:
        library = session.get(Library, library_id)
        if library is None:
            raise HTTPException(status_code=404, detail="library not found")

        base = select(TreeNode).where(TreeNode.library_id == library_id)
        count_stmt = select(func.count(TreeNode.id)).where(TreeNode.library_id == library_id)

        if parent_id is None:
            base = base.where(TreeNode.parent_id.is_(None))
            count_stmt = count_stmt.where(TreeNode.parent_id.is_(None))
        else:
            base = base.where(TreeNode.parent_id == parent_id)
            count_stmt = count_stmt.where(TreeNode.parent_id == parent_id)

        if not include_asset_nodes:
            asset_node_exists = select(Asset.id).where(Asset.node_id == TreeNode.id).exists()
            child_node = aliased(TreeNode)
            has_child_exists = select(child_node.id).where(child_node.parent_id == TreeNode.id).exists()
            keep_node = or_(~asset_node_exists, has_child_exists)
            base = base.where(keep_node)
            count_stmt = count_stmt.where(keep_node)

        total = session.scalar(count_stmt) or 0
        rows = session.scalars(base.order_by(TreeNode.name.asc()).offset(offset).limit(page_size)).all()

    return TreeNodeListResponse(
        items=[
            TreeNodeItem(
                id=row.id,
                library_id=row.library_id,
                parent_id=row.parent_id,
                name=row.name,
                path=row.path,
                depth=row.depth,
            )
            for row in rows
        ],
        meta=_build_page_meta(page, page_size, total),
    )


@app.get("/libraries/{library_id}/assets", response_model=AssetListResponse)
def list_assets(
    library_id: int,
    node_id: int | None = Query(default=None),
    include_descendants: bool = Query(default=True),
    scope: Literal["descendants", "self", "direct_children_assets"] = Query(default="descendants"),
    q: str | None = Query(default=None),
    sort_by: Literal["name", "created_at"] = Query(default="name"),
    sort_dir: Literal["asc", "desc"] = Query(default="asc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
) -> AssetListResponse:
    offset = (page - 1) * page_size
    with SessionLocal() as session:
        library = session.get(Library, library_id)
        if library is None:
            raise HTTPException(status_code=404, detail="library not found")

        filters = [Asset.library_id == library_id]
        if node_id is not None:
            node = session.get(TreeNode, node_id)
            if node is None or node.library_id != library_id:
                raise HTTPException(status_code=404, detail="tree node not found")
            effective_scope = scope
            if scope == "descendants" and not include_descendants:
                effective_scope = "self"

            if effective_scope == "descendants":
                prefix = f"{node.path}/%"
                descendant_node_ids = select(TreeNode.id).where(
                    TreeNode.library_id == library_id,
                    or_(TreeNode.id == node_id, TreeNode.path.like(prefix)),
                )
                filters.append(Asset.node_id.in_(descendant_node_ids))
            elif effective_scope == "self":
                filters.append(Asset.node_id == node_id)
            elif effective_scope == "direct_children_assets":
                child_node_ids = select(TreeNode.id).where(
                    TreeNode.library_id == library_id,
                    TreeNode.parent_id == node_id,
                )
                filters.append(Asset.node_id.in_(child_node_ids))
        if q:
            pattern = f"%{q}%"
            filters.append(or_(Asset.name.ilike(pattern), Asset.display_name.ilike(pattern)))

        count_stmt = select(func.count(Asset.id)).where(*filters)
        total = session.scalar(count_stmt) or 0

        sort_column = Asset.name if sort_by == "name" else Asset.created_at
        order_by = asc(sort_column) if sort_dir == "asc" else desc(sort_column)
        rows = session.scalars(select(Asset).where(*filters).order_by(order_by).offset(offset).limit(page_size)).all()
        asset_ids = [item.id for item in rows]
        thumbnail_map = _build_thumbnail_map(session, asset_ids)
        file_format_map = _build_file_format_map(session, asset_ids)
        node_path_map = _build_node_path_map(session, [item.node_id for item in rows if item.node_id is not None])

    return AssetListResponse(
        items=[
            AssetItem(
                id=row.id,
                library_id=row.library_id,
                node_id=row.node_id,
                node_path=node_path_map.get(row.node_id) if row.node_id is not None else None,
                name=row.name,
                display_name=row.display_name,
                status=row.status,
                thumbnail_relative_path=thumbnail_map.get(row.id),
                file_format=file_format_map.get(row.id),
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ],
        meta=_build_page_meta(page, page_size, total),
    )


@app.get("/assets/{asset_id}", response_model=AssetDetailResponse)
def get_asset_detail(asset_id: int) -> AssetDetailResponse:
    with SessionLocal() as session:
        row = session.scalar(select(Asset).where(Asset.id == asset_id).options(selectinload(Asset.file_refs)))
        if row is None:
            raise HTTPException(status_code=404, detail="asset not found")

        return AssetDetailResponse(
            id=row.id,
            library_id=row.library_id,
            node_id=row.node_id,
            name=row.name,
            display_name=row.display_name,
            status=row.status,
            created_at=row.created_at,
            updated_at=row.updated_at,
            files=[
                FileRefItem(
                    id=file_ref.id,
                    file_role=file_ref.file_role,
                    relative_path=file_ref.relative_path,
                    size=file_ref.size,
                    mtime=file_ref.mtime,
                    hash=file_ref.hash,
                )
                for file_ref in sorted(row.file_refs, key=lambda x: x.relative_path)
            ],
        )


@app.get("/search", response_model=AssetListResponse)
def search_assets(
    query: str = Query(min_length=1),
    library_id: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
) -> AssetListResponse:
    offset = (page - 1) * page_size
    pattern = f"%{query}%"

    with SessionLocal() as session:
        filters = [or_(Asset.name.ilike(pattern), Asset.display_name.ilike(pattern))]
        if library_id is not None:
            filters.append(Asset.library_id == library_id)

        total = session.scalar(select(func.count(Asset.id)).where(*filters)) or 0
        rows = session.scalars(
            select(Asset).where(*filters).order_by(Asset.updated_at.desc()).offset(offset).limit(page_size)
        ).all()
        asset_ids = [item.id for item in rows]
        thumbnail_map = _build_thumbnail_map(session, asset_ids)
        file_format_map = _build_file_format_map(session, asset_ids)
        node_path_map = _build_node_path_map(session, [item.node_id for item in rows if item.node_id is not None])

    return AssetListResponse(
        items=[
            AssetItem(
                id=row.id,
                library_id=row.library_id,
                node_id=row.node_id,
                node_path=node_path_map.get(row.node_id) if row.node_id is not None else None,
                name=row.name,
                display_name=row.display_name,
                status=row.status,
                thumbnail_relative_path=thumbnail_map.get(row.id),
                file_format=file_format_map.get(row.id),
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ],
        meta=_build_page_meta(page, page_size, total),
    )


@app.get("/media/{library_id}/{relative_path:path}")
def get_media_file(
    library_id: int,
    relative_path: str,
    _: None = Depends(_verify_media_token),
) -> FileResponse:
    safe_relative_path = _sanitize_relative_path(relative_path)

    with SessionLocal() as session:
        library = session.get(Library, library_id)
        if library is None:
            raise HTTPException(status_code=404, detail="library not found")

        file_ref = session.scalar(
            select(FileRef)
            .join(Asset, FileRef.asset_id == Asset.id)
            .where(Asset.library_id == library_id, FileRef.relative_path == safe_relative_path)
        )
        if file_ref is None:
            raise HTTPException(status_code=404, detail="media file not indexed")

        root = Path(library.root_path).resolve()
        resolved_file = (root / safe_relative_path).resolve()
        if root not in resolved_file.parents and resolved_file != root:
            raise HTTPException(status_code=400, detail="invalid relative path")
        if not resolved_file.is_file():
            raise HTTPException(status_code=404, detail="media file missing")

        return FileResponse(path=str(resolved_file), filename=resolved_file.name)


@app.post("/manage/nodes", response_model=CreateNodeResponse)
def create_node(payload: CreateNodeRequest) -> CreateNodeResponse:
    clean_name = payload.name.strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="node name is required")
    if "/" in clean_name or "\\" in clean_name:
        raise HTTPException(status_code=400, detail="node name contains invalid characters")

    with SessionLocal() as session:
        library = session.get(Library, payload.library_id)
        if library is None:
            raise HTTPException(status_code=404, detail="library not found")

        parent: TreeNode | None = None
        if payload.parent_id is not None:
            parent = session.get(TreeNode, payload.parent_id)
            if parent is None or parent.library_id != payload.library_id:
                raise HTTPException(status_code=404, detail="parent node not found")
        elif payload.parent_path:
            parent = _get_or_create_node_chain(session, payload.library_id, payload.parent_path)

        if parent is not None:
            node_path = f"{parent.path}/{clean_name}"
            depth = parent.depth + 1
        else:
            node_path = clean_name
            depth = 1

        target_dir = _safe_library_join(library.root_path, node_path)
        target_dir.mkdir(parents=True, exist_ok=True)

        node = TreeNode(
            library_id=payload.library_id,
            parent_id=payload.parent_id,
            name=clean_name,
            path=node_path,
            depth=depth,
            sort_order=0,
        )
        session.add(node)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=409, detail="node already exists")
        session.refresh(node)

        return CreateNodeResponse(
            id=node.id,
            library_id=node.library_id,
            parent_id=node.parent_id,
            name=node.name,
            path=node.path,
            depth=node.depth,
        )


@app.delete("/manage/nodes/{node_id}")
def delete_node(node_id: int) -> dict:
    with SessionLocal() as session:
        node = session.get(TreeNode, node_id)
        if node is None:
            raise HTTPException(status_code=404, detail="tree node not found")
        library = session.get(Library, node.library_id)
        if library is None:
            raise HTTPException(status_code=404, detail="library not found")

        node_path = node.path
        dir_path = _safe_library_join(library.root_path, node_path)

        descendants = session.scalars(
            select(TreeNode.id).where(
                TreeNode.library_id == node.library_id,
                or_(TreeNode.id == node.id, TreeNode.path.like(f"{node.path}/%")),
            )
        ).all()
        session.query(Asset).filter(Asset.node_id.in_(descendants)).delete(synchronize_session=False)
        session.query(TreeNode).filter(TreeNode.id.in_(descendants)).delete(synchronize_session=False)
        session.commit()

        if dir_path.exists():
            shutil.rmtree(dir_path, ignore_errors=True)

        return {"ok": True, "deleted_node_id": node_id}


@app.post("/manage/assets", response_model=CreateAssetResponse)
def create_asset(
    library_id: int = Form(...),
    node_id: int = Form(...),
    name: str = Form(...),
    thumbnail: UploadFile | None = File(default=None),
    asset_file: UploadFile | None = File(default=None),
) -> CreateAssetResponse:
    clean_name = name.strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="asset name is required")
    if "/" in clean_name or "\\" in clean_name:
        raise HTTPException(status_code=400, detail="asset name contains invalid characters")

    with SessionLocal() as session:
        library = session.get(Library, library_id)
        if library is None:
            raise HTTPException(status_code=404, detail="library not found")
        node = session.get(TreeNode, node_id)
        if node is None or node.library_id != library_id:
            raise HTTPException(status_code=404, detail="tree node not found")

        asset_dir_rel = f"{node.path}/{clean_name}"
        asset_dir = _safe_library_join(library.root_path, asset_dir_rel)
        asset_dir.mkdir(parents=True, exist_ok=True)

        asset = Asset(
            library_id=library_id,
            node_id=node_id,
            name=clean_name,
            display_name=clean_name,
            status="active",
        )
        session.add(asset)
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=409, detail="asset already exists")

        file_refs: list[FileRef] = []
        for upload, role in ((thumbnail, "thumbnail"), (asset_file, "primary")):
            if upload is None or not upload.filename:
                continue
            original_name = Path(upload.filename).name
            if role == "thumbnail":
                suffix = Path(original_name).suffix.lower() or ".jpg"
                file_name = f"{clean_name}{suffix}"
            else:
                file_name = original_name
            file_path = asset_dir / file_name
            with file_path.open("wb") as f:
                shutil.copyfileobj(upload.file, f)
            stat = file_path.stat()
            rel = f"{asset_dir_rel}/{file_name}".replace("\\", "/")
            file_ref = FileRef(
                asset_id=asset.id,
                file_role=role,
                relative_path=rel,
                size=stat.st_size,
                mtime=datetime.fromtimestamp(stat.st_mtime),
                hash=None,
            )
            session.add(file_ref)
            file_refs.append(file_ref)

        session.commit()
        session.refresh(asset)
        for ref in file_refs:
            session.refresh(ref)

        return CreateAssetResponse(
            id=asset.id,
            library_id=asset.library_id,
            node_id=asset.node_id or node_id,
            name=asset.name,
            files=[
                FileRefItem(
                    id=ref.id,
                    file_role=ref.file_role,
                    relative_path=ref.relative_path,
                    size=ref.size,
                    mtime=ref.mtime,
                    hash=ref.hash,
                )
                for ref in file_refs
            ],
        )


@app.delete("/manage/assets/{asset_id}")
def delete_asset(asset_id: int) -> dict:
    with SessionLocal() as session:
        asset = session.get(Asset, asset_id)
        if asset is None:
            raise HTTPException(status_code=404, detail="asset not found")
        library = session.get(Library, asset.library_id)
        if library is None:
            raise HTTPException(status_code=404, detail="library not found")

        node = session.get(TreeNode, asset.node_id) if asset.node_id is not None else None
        asset_dir_rel = f"{node.path}/{asset.name}" if node is not None else asset.name
        dir_path = _safe_library_join(library.root_path, asset_dir_rel)
        session.delete(asset)
        session.commit()

        if dir_path.exists():
            shutil.rmtree(dir_path, ignore_errors=True)
        return {"ok": True, "deleted_asset_id": asset_id}
