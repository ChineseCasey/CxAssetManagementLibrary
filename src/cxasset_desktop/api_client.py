from __future__ import annotations

from pathlib import Path
from typing import Any

import requests


class ApiClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", media_token: str = "dev-token") -> None:
        self.base_url = base_url.rstrip("/")
        self.media_token = media_token
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def set_media_token(self, token: str) -> None:
        self.media_token = token.strip()

    def _url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def request(self, method: str, path: str, **kwargs) -> Any:
        resp = self.session.request(method=method, url=self._url(path), timeout=30, **kwargs)
        resp.raise_for_status()
        if not resp.text:
            return {}
        return resp.json()

    def get_libraries(self) -> list[dict[str, Any]]:
        return self.request("GET", "/libraries?page=1&page_size=20").get("items", [])

    def get_tree(self, library_id: int, parent_id: int | None = None) -> list[dict[str, Any]]:
        query = f"/libraries/{library_id}/tree?include_asset_nodes=true&page=1&page_size=200"
        if parent_id is not None:
            query += f"&parent_id={parent_id}"
        return self.request("GET", query).get("items", [])

    def get_assets(self, library_id: int, node_id: int | None = None) -> list[dict[str, Any]]:
        query = f"/libraries/{library_id}/assets?page=1&page_size=200"
        if node_id is not None:
            query += f"&node_id={node_id}&scope=descendants"
        return self.request("GET", query).get("items", [])

    def get_asset_detail(self, asset_id: int) -> dict[str, Any]:
        return self.request("GET", f"/assets/{asset_id}")

    def create_node(self, library_id: int, parent_id: int | None, name: str) -> dict[str, Any]:
        payload = {"library_id": library_id, "name": name}
        if parent_id is not None:
            payload["parent_id"] = parent_id
        return self.request("POST", "/manage/nodes", json=payload)

    def delete_node(self, node_id: int) -> dict[str, Any]:
        return self.request("DELETE", f"/manage/nodes/{node_id}")

    def delete_asset(self, asset_id: int) -> dict[str, Any]:
        return self.request("DELETE", f"/manage/assets/{asset_id}")

    def create_asset(
        self,
        library_id: int,
        node_id: int,
        name: str,
        thumbnail_path: str | None = None,
        asset_file_path: str | None = None,
    ) -> dict[str, Any]:
        data = {"library_id": str(library_id), "node_id": str(node_id), "name": name}
        files: dict[str, tuple[str, Any, str]] = {}
        handles = []
        try:
            if thumbnail_path:
                p = Path(thumbnail_path)
                fp = p.open("rb")
                handles.append(fp)
                files["thumbnail"] = (p.name, fp, "application/octet-stream")
            if asset_file_path:
                p = Path(asset_file_path)
                fp = p.open("rb")
                handles.append(fp)
                files["asset_file"] = (p.name, fp, "application/octet-stream")
            return self.request("POST", "/manage/assets", data=data, files=files)
        finally:
            for h in handles:
                h.close()

    def get_media_bytes(self, library_id: int, relative_path: str) -> bytes:
        encoded = "/".join(requests.utils.quote(x, safe="") for x in relative_path.split("/"))
        resp = self.session.get(
            self._url(f"/media/{library_id}/{encoded}"),
            headers={"Authorization": f"Bearer {self.media_token}"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.content

    def get_favorite_ids(self, library_id: int | None = None) -> list[int]:
        path = "/favorites"
        if library_id is not None:
            path = f"/favorites?library_id={int(library_id)}"
        data = self.request("GET", path)
        return [int(x) for x in data.get("asset_ids", [])]

    def add_favorite(self, asset_id: int) -> None:
        self.request("POST", f"/favorites/{int(asset_id)}")

    def remove_favorite(self, asset_id: int) -> None:
        self.request("DELETE", f"/favorites/{int(asset_id)}")

