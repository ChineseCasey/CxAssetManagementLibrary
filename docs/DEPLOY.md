# CxAsset 部署与运维说明（S6）

## 1. 环境准备

- Python 3.10+
- 建议在虚拟环境中运行

```bash
pip install -e .
alembic upgrade head
```

## 2. 启动与同步

```bash
cxasset-sync
python -m uvicorn cxasset_api.main:app --app-dir src --host 127.0.0.1 --port 8000
```

访问地址：
- Web: `http://127.0.0.1:8000/`
- OpenAPI: `http://127.0.0.1:8000/openapi.json`

## 3. 关键配置

- `CXASSET_DATABASE_URL`：数据库连接，默认 `sqlite:///./cxasset.db`
- `CXASSET_LIBRARY_ROOTS`：库根路径，支持多个（`;` 分隔）
- `CXASSET_MEDIA_TOKEN`：媒体访问 token，默认 `dev-token`

## 4. 观测与排障

### 4.1 健康与指标

- `GET /health`：存活 + 数据库连通
- `GET /version`：版本信息
- `GET /metrics`：基础计数指标（libraries/assets/file_refs）

### 4.2 请求日志与追踪

- 每个请求生成 `request_id`，并回传在响应头 `X-Request-ID`
- 服务日志记录字段：`request_id`、method、path、status、elapsed_ms
- 问题排查建议：优先用 `X-Request-ID` 在日志定位单次请求

### 4.3 统一错误响应

统一格式：

```json
{
  "error": {
    "code": "HTTP_ERROR",
    "message": "library not found",
    "request_id": "..."
  }
}
```

常见错误码：
- `HTTP_ERROR`：业务/参数/鉴权等显式错误
- `INTERNAL_ERROR`：未处理异常

## 5. 验证清单（冷启动 → 同步 → 浏览）

1. `alembic upgrade head` 成功
2. `cxasset-sync` 成功且 `errors=0`（或可解释）
3. `/health` 返回 `{"status":"ok","database":"ok"}`
4. Web 页面可完成：目录浏览 -> 资产列表 -> 详情
5. `/media/...` 携带 token 可访问，缺 token 返回 401
