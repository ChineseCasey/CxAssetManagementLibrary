import { useEffect, useMemo, useRef, useState } from "react";
import {
  Button,
  Card,
  ConfigProvider,
  Descriptions,
  Empty,
  Form,
  Image,
  Input,
  Layout,
  Modal,
  Popconfirm,
  Segmented,
  Select,
  Slider,
  Spin,
  Switch,
  Tabs,
  Tree,
  Typography,
  Upload,
  message,
} from "antd";
import { StarFilled, StarOutlined, UploadOutlined } from "@ant-design/icons";
import useGlassTheme from "./glassTheme";

const { Header, Content } = Layout;
const { Text } = Typography;
const FAVORITES_KEY = "cxasset-favorites";

async function api(path, options = {}) {
  const resp = await fetch(path, options);
  if (!resp.ok) throw new Error(`${resp.status} ${path}`);
  const text = await resp.text();
  return text ? JSON.parse(text) : {};
}

function safeJsonParse(text, fallback) {
  try {
    return JSON.parse(text);
  } catch {
    return fallback;
  }
}

function App() {
  const [msgApi, contextHolder] = message.useMessage();
  const [dark, setDark] = useState(true);
  const [token, setToken] = useState("dev-token");
  const [loading, setLoading] = useState(false);
  const [libraryId, setLibraryId] = useState(null);
  const [modules, setModules] = useState([]);
  const [activeModuleId, setActiveModuleId] = useState(null);
  const [moduleNodeMap, setModuleNodeMap] = useState({});
  const [treeData, setTreeData] = useState([]);
  const [expandedKeys, setExpandedKeys] = useState([]);
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [assets, setAssets] = useState([]);
  const [allAssets, setAllAssets] = useState([]);
  const [search, setSearch] = useState("");
  const [cardSize, setCardSize] = useState(180);
  const [viewMode, setViewMode] = useState("card");
  const [activeAsset, setActiveAsset] = useState(null);
  const [activeAssetItem, setActiveAssetItem] = useState(null);
  const [thumbMap, setThumbMap] = useState({});
  const [breadcrumb, setBreadcrumb] = useState("-");
  const [treeWidth, setTreeWidth] = useState(280);
  const [detailWidth, setDetailWidth] = useState(340);
  const [treeCollapsed, setTreeCollapsed] = useState(false);
  const [detailCollapsed, setDetailCollapsed] = useState(false);
  const [pendingSelectPath, setPendingSelectPath] = useState(null);
  const [manageOpen, setManageOpen] = useState(false);
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
  const [favoriteIds, setFavoriteIds] = useState(() => new Set(safeJsonParse(localStorage.getItem(FAVORITES_KEY) || "[]", [])));

  const [createModuleName, setCreateModuleName] = useState("");
  const [createTypeModuleId, setCreateTypeModuleId] = useState(null);
  const [createTypeName, setCreateTypeName] = useState("");
  const [assetModuleId, setAssetModuleId] = useState(null);
  const [assetParentId, setAssetParentId] = useState(null);
  const [assetSubdirName, setAssetSubdirName] = useState("");
  const [assetName, setAssetName] = useState("");
  const [thumbFileList, setThumbFileList] = useState([]);
  const [assetFileList, setAssetFileList] = useState([]);
  const [deleteNodeModuleId, setDeleteNodeModuleId] = useState(null);
  const [deleteNodeId, setDeleteNodeId] = useState(null);
  const [deleteAssetModuleId, setDeleteAssetModuleId] = useState(null);
  const [deleteAssetNodePath, setDeleteAssetNodePath] = useState("");
  const [deleteAssetId, setDeleteAssetId] = useState(null);
  const listPanelRef = useRef(null);

  const configProps = useGlassTheme(dark);

  useEffect(() => {
    document.body.dataset.uiTheme = dark ? "dark" : "light";
  }, [dark]);

  const moduleOptions = useMemo(
    () => modules.map((m) => ({ label: m.name, value: m.id })),
    [modules]
  );
  const nodeOptionsByModule = useMemo(() => {
    const map = {};
    for (const [mid, nodes] of Object.entries(moduleNodeMap)) {
      map[mid] = nodes.map((n) => ({ label: n.path, value: n.id }));
    }
    return map;
  }, [moduleNodeMap]);
  const deleteNodeOptions = useMemo(() => {
    if (!deleteNodeModuleId) return [];
    const module = modules.find((m) => m.id === deleteNodeModuleId);
    const moduleNodes = moduleNodeMap[String(deleteNodeModuleId)] || [];
    const all = module ? [module, ...moduleNodes] : moduleNodes;
    return all.map((n) => ({ label: n.path, value: n.id }));
  }, [deleteNodeModuleId, modules, moduleNodeMap]);
  const deleteAssetNodePathOptions = useMemo(() => {
    if (!deleteAssetModuleId) return [];
    const module = modules.find((m) => m.id === deleteAssetModuleId);
    const moduleNodes = moduleNodeMap[String(deleteAssetModuleId)] || [];
    const list = [];
    list.push({ label: "全部目录", value: "" });
    if (module) list.push({ label: module.path, value: module.path });
    moduleNodes.forEach((n) => list.push({ label: n.path, value: n.path }));
    return list;
  }, [deleteAssetModuleId, modules, moduleNodeMap]);

  useEffect(() => {
    localStorage.setItem(FAVORITES_KEY, JSON.stringify(Array.from(favoriteIds)));
  }, [favoriteIds]);

  function toggleFavorite(assetId) {
    setFavoriteIds((prev) => {
      const next = new Set(prev);
      if (next.has(assetId)) next.delete(assetId);
      else next.add(assetId);
      return next;
    });
  }

  function startResize(side, event) {
    event.preventDefault();
    const startX = event.clientX;
    const startTree = treeWidth;
    const startDetail = detailWidth;
    const maxTree = Math.max(420, Math.floor(window.innerWidth * 0.62));
    const maxDetail = Math.max(420, Math.floor(window.innerWidth * 0.62));
    const onMove = (e) => {
      if (side === "left") {
        const next = Math.max(120, Math.min(maxTree, startTree + (e.clientX - startX)));
        setTreeWidth(next);
      } else {
        const next = Math.max(180, Math.min(maxDetail, startDetail - (e.clientX - startX)));
        setDetailWidth(next);
      }
    };
    const onUp = () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  }

  function syncTreeByPath(pathText, currentModuleId = activeModuleId) {
    if (!pathText || !currentModuleId) return;
    const moduleNodes = moduleNodeMap[String(currentModuleId)] || [];
    const moduleRoot = modules.find((m) => m.id === currentModuleId);
    const all = [...moduleNodes, ...(moduleRoot ? [moduleRoot] : [])];
    const target = all.find((n) => n.path === pathText);
    if (target) setSelectedNodeId(target.id);
    const segs = pathText.split("/").filter(Boolean);
    const keys = [];
    let cur = "";
    for (const s of segs) {
      cur = cur ? `${cur}/${s}` : s;
      const hit = all.find((n) => n.path === cur);
      if (hit) keys.push(String(hit.id));
    }
    if (keys.length) setExpandedKeys(Array.from(new Set(keys)));
    setBreadcrumb(pathText);
    setTreeCollapsed(false);
  }

  function locateAssetInTree(nodePath) {
    if (!nodePath) return;
    const moduleName = nodePath.split("/")[0];
    const module = modules.find((m) => m.name === moduleName);
    setTreeCollapsed(false);
    if (module && module.id !== activeModuleId) {
      setActiveModuleId(module.id);
      setPendingSelectPath(nodePath);
      return;
    }
    syncTreeByPath(nodePath);
  }

  async function loadThumb(library, relativePath) {
    const key = `${library}::${relativePath}`;
    if (thumbMap[key]) return thumbMap[key];
    const encodedPath = relativePath.split("/").map(encodeURIComponent).join("/");
    const resp = await fetch(`/media/${library}/${encodedPath}`, { headers: { Authorization: `Bearer ${token}` } });
    if (!resp.ok) return null;
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    setThumbMap((prev) => ({ ...prev, [key]: url }));
    return url;
  }

  async function buildTree(libId, parentId, depth = 1) {
    if (depth > 4) return [];
    const data = await api(`/libraries/${libId}/tree?parent_id=${parentId}&include_asset_nodes=true&page=1&page_size=200`);
    const children = [];
    for (const n of data.items) {
      const sub = await buildTree(libId, n.id, depth + 1);
      children.push({ key: String(n.id), title: n.name, path: n.path, nodeId: n.id, children: sub });
    }
    return children;
  }

  async function collectModuleNodes(moduleId, libId = libraryId) {
    if (!libId || !moduleId) return [];
    const collected = [];
    async function walk(parentId, depth = 1) {
      if (depth > 4) return;
      const data = await api(`/libraries/${libId}/tree?parent_id=${parentId}&include_asset_nodes=true&page=1&page_size=200`);
      for (const n of data.items || []) {
        collected.push(n);
        await walk(n.id, depth + 1);
      }
    }
    await walk(moduleId, 1);
    return collected;
  }

  async function loadAllAssets(libId = libraryId) {
    if (!libId) return [];
    let page = 1;
    const pageSize = 200;
    const all = [];
    while (true) {
      const data = await api(`/libraries/${libId}/assets?page=${page}&page_size=${pageSize}`);
      all.push(...(data.items || []));
      if (!data.meta || page >= data.meta.total_pages) break;
      page += 1;
    }
    return all;
  }

  async function loadAssetsForNode(nodeId, pathText) {
    const data = await api(`/libraries/${libraryId}/assets?node_id=${nodeId}&scope=descendants&page=1&page_size=200`);
    setAssets(data.items || []);
    setBreadcrumb(pathText || "-");
    setActiveAsset(null);
    if (listPanelRef.current) listPanelRef.current.scrollTop = 0;
  }

  async function refreshModuleNodeMap(nextModules = modules, libId = libraryId) {
    const newMap = {};
    for (const m of nextModules) {
      newMap[String(m.id)] = await collectModuleNodes(m.id, libId);
    }
    setModuleNodeMap(newMap);
    return newMap;
  }

  async function refreshEverything(keepNode = null) {
    if (!libraryId) return;
    const root = await api(`/libraries/${libraryId}/tree?page=1&page_size=200`);
    const modItems = root.items || [];
    setModules(modItems);
    const newNodeMap = await refreshModuleNodeMap(modItems);
    const targetModuleId = modItems.some((m) => m.id === activeModuleId) ? activeModuleId : modItems[0]?.id;
    setActiveModuleId(targetModuleId || null);
    if (targetModuleId) {
      const module = modItems.find((m) => m.id === targetModuleId);
      const children = await buildTree(libraryId, targetModuleId, 2);
      setTreeData([{ key: String(targetModuleId), title: module?.name || "模块", path: module?.path || "", nodeId: targetModuleId, children }]);
      setExpandedKeys([String(targetModuleId)]);
      const useNode = keepNode || targetModuleId;
      setSelectedNodeId(useNode);
      const pathText = (newNodeMap[String(targetModuleId)] || []).find((n) => n.id === useNode)?.path || module?.path || "-";
      await loadAssetsForNode(useNode, pathText);
    } else {
      setTreeData([]);
      setAssets([]);
      setActiveAsset(null);
      setBreadcrumb("-");
    }
  }

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const libs = await api("/libraries?page=1&page_size=20");
        const lib = libs.items?.[0];
        if (!lib) return;
        setLibraryId(lib.id);
        const root = await api(`/libraries/${lib.id}/tree?page=1&page_size=200`);
        const rootItems = root.items || [];
        setModules(rootItems);
        await refreshModuleNodeMap(rootItems, lib.id);
        setAllAssets(await loadAllAssets(lib.id));
        if (root.items?.[0]) {
          setActiveModuleId(root.items[0].id);
          setCreateTypeModuleId(root.items[0].id);
          setAssetModuleId(root.items[0].id);
          setDeleteNodeModuleId(root.items[0].id);
          setDeleteAssetModuleId(root.items[0].id);
        }
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  useEffect(() => {
    if (!libraryId || !activeModuleId) return;
    (async () => {
      setLoading(true);
      try {
        const module = modules.find((m) => m.id === activeModuleId);
        const activeNodes = await collectModuleNodes(activeModuleId);
        setModuleNodeMap((prev) => ({ ...prev, [String(activeModuleId)]: activeNodes }));
        const children = await buildTree(libraryId, activeModuleId, 2);
        const rootNode = { key: String(activeModuleId), title: module?.name || "模块", path: module?.path || "", nodeId: activeModuleId, children };
        setTreeData([rootNode]);
        setExpandedKeys([String(activeModuleId)]);
        setSelectedNodeId(activeModuleId);
        await loadAssetsForNode(activeModuleId, module?.path || "-");
      } finally {
        setLoading(false);
      }
    })();
  }, [libraryId, activeModuleId, modules]);

  const filteredAssets = useMemo(() => {
    if (!search.trim()) return assets;
    const q = search.toLowerCase();
    return assets.filter((a) => (a.display_name || a.name || "").toLowerCase().includes(q));
  }, [assets, search]);

  const detailPreview = useMemo(() => {
    if (!activeAsset?.files?.length) return null;
    return activeAsset.files.find((f) => [".jpg", ".jpeg", ".png", ".webp"].some((ext) => f.relative_path.toLowerCase().endsWith(ext)));
  }, [activeAsset]);

  useEffect(() => {
    filteredAssets.forEach((a) => {
      if (!a.thumbnail_relative_path) return;
      const key = `${a.library_id}::${a.thumbnail_relative_path}`;
      if (!thumbMap[key]) {
        loadThumb(a.library_id, a.thumbnail_relative_path).catch(() => {});
      }
    });
  }, [filteredAssets, thumbMap, token]);

  useEffect(() => {
    if (!detailPreview || !activeAsset) return;
    const key = `${activeAsset.library_id}::${detailPreview.relative_path}`;
    if (!thumbMap[key]) {
      loadThumb(activeAsset.library_id, detailPreview.relative_path).catch(() => {});
    }
  }, [detailPreview, activeAsset, thumbMap, token]);

  useEffect(() => {
    if (!pendingSelectPath) return;
    const moduleName = pendingSelectPath.split("/")[0];
    const module = modules.find((m) => m.name === moduleName);
    if (!module) {
      setPendingSelectPath(null);
      return;
    }
    if (module.id !== activeModuleId) {
      setActiveModuleId(module.id);
      return;
    }
    syncTreeByPath(pendingSelectPath, module.id);
    setPendingSelectPath(null);
  }, [pendingSelectPath, modules, activeModuleId, moduleNodeMap]);

  function formatBytes(size) {
    if (size == null || Number.isNaN(size)) return "-";
    if (size < 1024) return `${size} B`;
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
    if (size < 1024 * 1024 * 1024) return `${(size / (1024 * 1024)).toFixed(1)} MB`;
    return `${(size / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  }

  const detailInfo = useMemo(() => {
    if (!activeAsset) return null;
    const files = activeAsset.files || [];
    const primary = files.find((f) => f.file_role === "primary") || files[0] || null;
    const ext = primary?.relative_path ? primary.relative_path.split(".").pop()?.toUpperCase() : null;
    const totalSize = files.reduce((sum, f) => sum + (f.size || 0), 0);
    const setDate = primary?.mtime || activeAsset.updated_at || activeAsset.created_at;
    const typeText = activeAssetItem?.node_path ? activeAssetItem.node_path.split("/").slice(1).join(" / ") || activeAsset.status : activeAsset.status;
    return {
      name: activeAsset.display_name || activeAsset.name,
      type: typeText || "-",
      fileType: ext || activeAssetItem?.file_format || "-",
      fileSize: formatBytes(totalSize || primary?.size),
      setDate: setDate ? new Date(setDate).toLocaleString() : "-",
      status: activeAsset.status || "-",
      files,
    };
  }, [activeAsset, activeAssetItem]);

  const favoriteAssets = useMemo(() => allAssets.filter((a) => favoriteIds.has(a.id)), [allAssets, favoriteIds]);
  const displayedAssets = useMemo(() => (showFavoritesOnly ? favoriteAssets : filteredAssets), [showFavoritesOnly, favoriteAssets, filteredAssets]);
  const cardThumbSize = useMemo(() => Math.max(100, Math.round(cardSize * 0.9)), [cardSize]);
  const listThumbSize = useMemo(() => Math.max(28, Math.round(cardSize * 0.25)), [cardSize]);

  useEffect(() => {
    if (!manageOpen) return;
    (async () => {
      const all = await loadAllAssets();
      setAssets(all);
      setAllAssets(all);
      await refreshModuleNodeMap(modules);
      if (!createTypeModuleId && modules[0]) setCreateTypeModuleId(modules[0].id);
      if (!assetModuleId && modules[0]) setAssetModuleId(modules[0].id);
      if (!deleteNodeModuleId && modules[0]) setDeleteNodeModuleId(modules[0].id);
      if (!deleteAssetModuleId && modules[0]) setDeleteAssetModuleId(modules[0].id);
    })();
  }, [manageOpen, modules]);

  const deleteAssetOptions = useMemo(() => {
    let list = assets;
    if (deleteAssetModuleId) {
      const module = modules.find((m) => m.id === deleteAssetModuleId);
      if (module) {
        const prefix = `${module.path}/`;
        list = list.filter((a) => a.node_path === module.path || (a.node_path || "").startsWith(prefix));
      }
    }
    if (deleteAssetNodePath) {
      const prefix = `${deleteAssetNodePath}/`;
      list = list.filter((a) => a.node_path === deleteAssetNodePath || (a.node_path || "").startsWith(prefix));
    }
    return list.map((a) => ({ label: `${a.node_path || "-"} / ${a.name}`, value: a.id }));
  }, [assets, deleteAssetModuleId, deleteAssetNodePath, modules]);

  async function handleCreateModule() {
    if (!createModuleName.trim() || !libraryId) return;
    await api("/manage/nodes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ library_id: libraryId, parent_id: null, name: createModuleName.trim() }),
    });
    setCreateModuleName("");
    await refreshEverything(selectedNodeId);
    msgApi.success("模块创建成功");
  }

  async function handleCreateType() {
    if (!createTypeModuleId || !createTypeName.trim() || !libraryId) return;
    await api("/manage/nodes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ library_id: libraryId, parent_id: createTypeModuleId, name: createTypeName.trim() }),
    });
    setCreateTypeName("");
    await refreshEverything(selectedNodeId);
    msgApi.success("类型目录创建成功");
  }

  async function handleCreateAsset() {
    if (!libraryId || !assetModuleId || !assetParentId || !assetName.trim()) return;
    let targetNodeId = assetParentId;
    if (assetSubdirName.trim()) {
      const node = await api("/manage/nodes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ library_id: libraryId, parent_id: assetParentId, name: assetSubdirName.trim() }),
      });
      targetNodeId = node.id;
    }
    const fd = new FormData();
    fd.append("library_id", String(libraryId));
    fd.append("node_id", String(targetNodeId));
    fd.append("name", assetName.trim());
    if (thumbFileList[0]?.originFileObj) fd.append("thumbnail", thumbFileList[0].originFileObj);
    if (assetFileList[0]?.originFileObj) fd.append("asset_file", assetFileList[0].originFileObj);
    await api("/manage/assets", { method: "POST", body: fd });
    setAssetName("");
    setAssetSubdirName("");
    setThumbFileList([]);
    setAssetFileList([]);
    await refreshEverything(targetNodeId);
    msgApi.success("资产创建成功");
  }

  async function handleDeleteNode() {
    if (!deleteNodeId) return;
    await api(`/manage/nodes/${deleteNodeId}`, { method: "DELETE" });
    setDeleteNodeId(null);
    await refreshEverything(null);
    msgApi.success("目录删除成功");
  }

  async function handleDeleteAsset() {
    if (!deleteAssetId) return;
    await api(`/manage/assets/${deleteAssetId}`, { method: "DELETE" });
    setDeleteAssetId(null);
    const allAssets = await loadAllAssets();
    setAssets(allAssets);
    setAllAssets(allAssets);
    msgApi.success("资产删除成功");
  }

  return (
    <ConfigProvider {...configProps}>
      {contextHolder}
      <Layout style={{ minHeight: "100vh" }}>
        <Header className="app-header">
          <div className="app-title-wrap">
            <img src="/antd/title_icon.png" alt="CxAsset icon" className="app-brand-icon" />
            <Text strong className="app-title">CxAsset</Text>
          </div>
          <div className="app-actions">
            <Input placeholder="搜索资产名称..." value={search} onChange={(e) => setSearch(e.target.value)} style={{ width: 220 }} />
            <Input placeholder="Media Token" value={token} onChange={(e) => setToken(e.target.value)} style={{ width: 150 }} />
            <Button type={showFavoritesOnly ? "primary" : "default"} onClick={() => setShowFavoritesOnly((v) => !v)}>
              {showFavoritesOnly ? "显示全部" : "仅看收藏"} ({favoriteIds.size})
            </Button>
            <Button onClick={() => setManageOpen(true)}>管理面板</Button>
            <Text type="secondary">Dark</Text>
            <Switch checked={dark} onChange={setDark} />
          </div>
        </Header>
        <Content className="app-content">
          {loading ? (
            <div className="center-spin"><Spin /></div>
          ) : (
            <div
              className={`workspace-grid${treeCollapsed ? " tree-collapsed" : ""}${detailCollapsed ? " detail-collapsed" : ""}`}
              style={{ "--tree-width": `${treeWidth}px`, "--detail-width": `${detailWidth}px` }}
            >
              <div className="panel tree-wrap">
                <Text type="secondary">模块</Text>
                <Select
                  value={activeModuleId}
                  options={moduleOptions}
                  onChange={setActiveModuleId}
                  style={{ width: "100%", margin: "6px 0 10px" }}
                />
                <Tree
                  treeData={treeData}
                  blockNode
                  expandedKeys={expandedKeys}
                  selectedKeys={selectedNodeId ? [String(selectedNodeId)] : []}
                  onExpand={(keys) => setExpandedKeys(keys)}
                  onSelect={async (keys, info) => {
                    if (!info?.node) return;
                    const nodeId = Number(info.node.nodeId || keys[0]);
                    if (!nodeId) return;
                    setSelectedNodeId(nodeId);
                    setPendingSelectPath(null);
                    const nodePath =
                      info.node.path ||
                      (moduleNodeMap[String(activeModuleId)] || []).find((n) => n.id === nodeId)?.path ||
                      breadcrumb;
                    await loadAssetsForNode(nodeId, nodePath);
                  }}
                />
              </div>
              <div className="pane-divider" onMouseDown={(e) => startResize("left", e)}>
                <button
                  className="pane-toggle"
                  onClick={(e) => {
                    e.stopPropagation();
                    setTreeCollapsed((v) => !v);
                  }}
                  title="折叠/展开目录树"
                >
                  {treeCollapsed ? ">" : "<"}
                </button>
              </div>
              <div className="panel list-panel" ref={listPanelRef}>
                <div className="list-head">
                  <Text strong>资产列表</Text>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <Segmented
                      size="small"
                      value={viewMode}
                      onChange={setViewMode}
                      options={[
                        { label: "卡片", value: "card" },
                        { label: "列表", value: "list" },
                      ]}
                    />
                    <Text type="secondary">共 {displayedAssets.length} 条</Text>
                  </div>
                </div>
                <div className="crumb">当前路径：{breadcrumb}</div>
                <div className="slider-row">
                  <Text type="secondary">卡片大小</Text>
                  <Slider min={120} max={280} value={cardSize} onChange={setCardSize} style={{ width: 180 }} />
                </div>
                {!displayedAssets.length ? (
                  <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={showFavoritesOnly ? "暂无收藏资产" : "当前筛选下没有资产"} />
                ) : viewMode === "card" ? (
                  <div className="card-grid" style={{ gridTemplateColumns: `repeat(auto-fill, minmax(${cardSize}px, 1fr))` }}>
                    {displayedAssets.map((a) => (
                      <Card
                        key={a.id}
                        className="asset-card"
                        hoverable
                        onClick={async () => {
                          const detail = await api(`/assets/${a.id}`);
                          setActiveAsset(detail);
                          setActiveAssetItem(a);
                          setBreadcrumb(a.node_path || breadcrumb);
                          locateAssetInTree(a.node_path || null);
                        }}
                      >
                        <Button
                          type="text"
                          className="favorite-btn"
                          icon={favoriteIds.has(a.id) ? <StarFilled /> : <StarOutlined />}
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleFavorite(a.id);
                          }}
                        />
                        <div className="thumb-wrap" style={{ height: `${cardThumbSize}px` }}>
                          {a.thumbnail_relative_path ? (
                            <Image
                              src={thumbMap[`${a.library_id}::${a.thumbnail_relative_path}`]}
                              preview={false}
                              fallback=""
                              alt={a.name}
                              onLoad={() => {}}
                              placeholder
                              style={{ width: "100%", height: `${cardThumbSize}px`, objectFit: "cover" }}
                              rootClassName="thumb-image"
                              onError={() => {}}
                            />
                          ) : (
                            <div className="thumb-empty">无缩略图</div>
                          )}
                        </div>
                        <div className="asset-name">{a.display_name || a.name}</div>
                        <Text type="secondary" className="asset-meta">{a.status}{a.file_format ? ` · ${a.file_format}` : ""}</Text>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="list-mode-wrap">
                    {displayedAssets.map((a) => (
                      <div
                        key={a.id}
                        className="list-row"
                        style={{ gridTemplateColumns: `${listThumbSize}px minmax(140px, 1fr) minmax(180px, 1.2fr) auto` }}
                        onClick={async () => {
                          const detail = await api(`/assets/${a.id}`);
                          setActiveAsset(detail);
                          setActiveAssetItem(a);
                          locateAssetInTree(a.node_path || null);
                        }}
                      >
                        <div className="list-row-thumb" style={{ width: `${listThumbSize}px`, height: `${listThumbSize}px` }}>
                          {a.thumbnail_relative_path && thumbMap[`${a.library_id}::${a.thumbnail_relative_path}`] ? (
                            <img src={thumbMap[`${a.library_id}::${a.thumbnail_relative_path}`]} alt={a.name} />
                          ) : (
                            <div className="list-row-thumb-empty">-</div>
                          )}
                        </div>
                        <div className="list-row-title">{a.display_name || a.name}</div>
                        <Text type="secondary">{a.node_path || "-"}</Text>
                        <Button
                          type="text"
                          icon={favoriteIds.has(a.id) ? <StarFilled /> : <StarOutlined />}
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleFavorite(a.id);
                          }}
                        />
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <div className="pane-divider" onMouseDown={(e) => startResize("right", e)}>
                <button
                  className="pane-toggle"
                  onClick={(e) => {
                    e.stopPropagation();
                    setDetailCollapsed((v) => !v);
                  }}
                  title="折叠/展开详情"
                >
                  {detailCollapsed ? "<" : ">"}
                </button>
              </div>
              <div className="panel detail-panel">
                <Text strong>资产详情</Text>
                {!activeAsset ? (
                  <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="点击资产查看详情" style={{ marginTop: 30 }} />
                ) : (
                  <div style={{ marginTop: 10 }}>
                    {detailPreview ? (
                      <Image
                        src={thumbMap[`${activeAsset.library_id}::${detailPreview.relative_path}`]}
                        alt="preview"
                        style={{ width: "100%", borderRadius: 8 }}
                        preview={false}
                        placeholder
                      />
                    ) : (
                      <div className="thumb-empty">无可预览图片</div>
                    )}
                    <div style={{ marginTop: 10 }}>
                      <Descriptions
                        column={1}
                        size="small"
                        items={[
                          { key: "name", label: "Name", children: detailInfo?.name || "-" },
                          { key: "type", label: "Type", children: detailInfo?.type || "-" },
                          { key: "fileType", label: "FileType", children: detailInfo?.fileType || "-" },
                          { key: "fileSize", label: "FileSize", children: detailInfo?.fileSize || "-" },
                          { key: "setDate", label: "setDate", children: detailInfo?.setDate || "-" },
                          { key: "status", label: "Status", children: detailInfo?.status || "-" },
                        ]}
                      />
                      <div style={{ marginTop: 8 }}>
                        <Text type="secondary">Files</Text>
                        <ul style={{ margin: "6px 0 0", paddingLeft: 18 }}>
                          {(detailInfo?.files || []).map((f) => (
                            <li key={f.id}>
                              {f.relative_path} ({formatBytes(f.size)})
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </Content>
      </Layout>
      <Modal
        title="目录与资产管理"
        open={manageOpen}
        onCancel={() => setManageOpen(false)}
        footer={null}
        width={980}
      >
        <Tabs
          items={[
            {
              key: "create",
              label: "创建",
              children: (
                <div className="manage-grid">
                  <Card size="small" title="1) 新增模块">
                    <Form layout="vertical" onFinish={handleCreateModule}>
                      <Form.Item label="模块名" required>
                        <Input value={createModuleName} onChange={(e) => setCreateModuleName(e.target.value)} placeholder="例如：Lighting" />
                      </Form.Item>
                      <Button type="primary" htmlType="submit" block>新增模块</Button>
                    </Form>
                  </Card>
                  <Card size="small" title="2) 新增类型目录">
                    <Form layout="vertical" onFinish={handleCreateType}>
                      <Form.Item label="属于哪个模块" required>
                        <Select value={createTypeModuleId} options={moduleOptions} onChange={setCreateTypeModuleId} />
                      </Form.Item>
                      <Form.Item label="类型目录名" required>
                        <Input value={createTypeName} onChange={(e) => setCreateTypeName(e.target.value)} placeholder="例如：HDRI" />
                      </Form.Item>
                      <Button type="primary" htmlType="submit" block>新增类型目录</Button>
                    </Form>
                  </Card>
                  <Card size="small" title="3) 上传资产到目标目录" className="manage-wide-card">
                    <Form layout="vertical" onFinish={handleCreateAsset}>
                      <Form.Item label="模块" required>
                        <Select
                          value={assetModuleId}
                          options={moduleOptions}
                          onChange={(v) => {
                            setAssetModuleId(v);
                            setAssetParentId(null);
                          }}
                        />
                      </Form.Item>
                      <Form.Item label="归属目录（类型或子类型）" required>
                        <Select value={assetParentId} options={nodeOptionsByModule[String(assetModuleId)] || []} onChange={setAssetParentId} />
                      </Form.Item>
                      <Form.Item label="先创建子目录（可选）">
                        <Input value={assetSubdirName} onChange={(e) => setAssetSubdirName(e.target.value)} />
                      </Form.Item>
                      <Form.Item label="资产名称" required>
                        <Input value={assetName} onChange={(e) => setAssetName(e.target.value)} placeholder="例如：Micah_Loft" />
                      </Form.Item>
                      <Form.Item label="缩略图（jpg/png）">
                        <Upload beforeUpload={() => false} maxCount={1} fileList={thumbFileList} onChange={({ fileList }) => setThumbFileList(fileList)}>
                          <Button icon={<UploadOutlined />}>选择文件</Button>
                        </Upload>
                      </Form.Item>
                      <Form.Item label="原始资产文件（例如 .exr）">
                        <Upload beforeUpload={() => false} maxCount={1} fileList={assetFileList} onChange={({ fileList }) => setAssetFileList(fileList)}>
                          <Button icon={<UploadOutlined />}>选择文件</Button>
                        </Upload>
                      </Form.Item>
                      <Button type="primary" htmlType="submit" block>新增资产</Button>
                    </Form>
                  </Card>
                </div>
              ),
            },
            {
              key: "delete",
              label: "删除",
              children: (
                <div className="manage-grid">
                  <Card size="small" title="删除目录">
                    <Form layout="vertical">
                      <Form.Item label="模块">
                        <Select value={deleteNodeModuleId} options={moduleOptions} onChange={(v) => { setDeleteNodeModuleId(v); setDeleteNodeId(null); }} />
                      </Form.Item>
                      <Form.Item label="选择要删除的目录">
                        <Select value={deleteNodeId} options={deleteNodeOptions} onChange={setDeleteNodeId} />
                      </Form.Item>
                      <Popconfirm title="确认删除该目录及子层级?" onConfirm={handleDeleteNode}>
                        <Button danger block>删除目录（含子层级）</Button>
                      </Popconfirm>
                    </Form>
                  </Card>
                  <Card size="small" title="删除资产">
                    <Form layout="vertical">
                      <Form.Item label="模块">
                        <Select value={deleteAssetModuleId} options={moduleOptions} onChange={(v) => { setDeleteAssetModuleId(v); setDeleteAssetNodePath(""); setDeleteAssetId(null); }} />
                      </Form.Item>
                      <Form.Item label="资产所在目录（可选）">
                        <Select value={deleteAssetNodePath} options={deleteAssetNodePathOptions} onChange={setDeleteAssetNodePath} />
                      </Form.Item>
                      <Form.Item label="选择要删除的资产">
                        <Select value={deleteAssetId} options={deleteAssetOptions} onChange={setDeleteAssetId} />
                      </Form.Item>
                      <Popconfirm title="确认删除该资产?" onConfirm={handleDeleteAsset}>
                        <Button danger block>删除资产</Button>
                      </Popconfirm>
                    </Form>
                  </Card>
                </div>
              ),
            },
          ]}
        />
      </Modal>
    </ConfigProvider>
  );
}

export default App;
