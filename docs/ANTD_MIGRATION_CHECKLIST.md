# AntD Migration Checklist

This checklist tracks parity between the legacy `/web/index.html` page and the new `/antd` page.

## Core Browsing

- [x] Module select + tree rendering (module shown as top level)
- [x] Tree node click loads descendant assets
- [x] Asset card list with thumbnail and file format
- [x] Card size slider
- [x] Real-time search filter
- [x] Detail panel preview and metadata
- [x] Breadcrumb refresh on tree selection
- [x] Asset card click syncs tree path and breadcrumb

## Layout Interactions

- [x] Three-column layout
- [x] Left/right panel drag resize
- [x] Wider drag range tuned (min/max expanded)
- [x] Left/right panel collapse & expand
- [x] Divider hover toggle visibility

## Management Panel

- [x] Create module
- [x] Create type directory
- [x] Create asset with optional subdir
- [x] Upload thumbnail and source file
- [x] Delete node by module filter
- [x] Delete asset by module/path filter
- [x] Refresh tree/assets/options after create/delete

## API / Routing

- [x] AntD app served at `/antd`
- [x] Vite base path set to `/antd/` for static assets
- [x] Legacy page kept at `/web/index.html`
- [ ] Switch default `/` route to `/antd` (wait for final sign-off)

## Open Follow-up

- [ ] Optional performance split for large AntD bundle (code splitting)
- [ ] Optional parity for operation log display in AntD modal
