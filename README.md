# CxAssetManagementLibrary
管理CG资产的工具
当前仅为未完成版本
![image](https://github.com/ChineseCasey/CxAssetManagementLibrary/blob/master/xiaoguo.png)

## S1 Web API Baseline

### 环境要求
- Python 3.10+

### 初始化
```bash
pip install -e .
alembic upgrade head
```

### 一条命令启动 API
```bash
uvicorn cxasset_api.main:app --app-dir src --reload
```

启动后访问：
- Web UI: `http://127.0.0.1:8000/`
- OpenAPI: `http://127.0.0.1:8000/openapi.json`
- Deploy/运维说明：`docs/DEPLOY.md`

### 验证
- `GET /health`
- `GET /version`
- `GET /metrics`

### S3 只读 API（均为分页接口）
- `GET /libraries`
- `GET /libraries/{library_id}/tree`
- `GET /libraries/{library_id}/assets`
- `GET /assets/{asset_id}`
- `GET /search`

通用分页参数：
- `page`（默认 1）
- `page_size`（默认 20，最大 200）

### S4 媒体与权限
- 媒体接口：`GET /media/{library_id}/{relative_path}`
- 鉴权方式：
  - `Authorization: Bearer <token>` 或
  - `X-API-Token: <token>`
- 默认 token 来自环境变量 `CXASSET_MEDIA_TOKEN`（未设置时默认 `dev-token`）

### 运行 S2 同步（只读）
默认扫描 `CXA_Library`，可通过环境变量覆盖多个根目录（`;` 分隔）：

```bash
set CXASSET_LIBRARY_ROOTS=C:\path\to\LibraryA;D:\LibraryB
cxasset-sync
```

也可以命令行显式传入：

```bash
cxasset-sync --roots C:\path\to\LibraryA D:\LibraryB
```
