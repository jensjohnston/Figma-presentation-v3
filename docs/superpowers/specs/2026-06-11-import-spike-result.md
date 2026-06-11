# Spike result — SharePoint → Figma image round trip (2026-06-11)

**Verdict: Path B (synced OneDrive folder) for binaries; MS365 MCP for discovery only.**

## What was tested

One image (`Cleone-Main-Image.jpg`, 2000×2000 JPEG, 736 KB) end-to-end: locate in SharePoint → fetch binary → upload into the Bluewater 2026 Figma file (`GkUiwJTK5Xi65AKw4MOjTL`) → verify placement → delete.

## Findings

### MS365 MCP (Path A) — cannot deliver image binaries
- `sharepoint_search` does **not index image files**: queries that match known image filenames (`Cleone-Main-Image`, `Cleone` + `fileType: jpg`, `Bluewater` + `fileType: png`) all return zero results. Only document types (docx/pdf/folders) surface.
- `sharepoint_folder_search` **works** for finding folders (e.g. `Distributor Folder/Content (Images, Videos and Renders)/Amazon content/Cleone`).
- `read_resource` on a folder URI returns a **bare name listing** (no per-file URIs, no itemIds, no download URLs) — so there is no way to construct the `file:///{driveId}/{itemId}` URI for an image and fetch its bytes.
- Conclusion: MCP is useful for **discovering folder paths** but structurally cannot fetch image binaries.

### Synced OneDrive folder (Path B) — works
- The full Marketing SharePoint library is synced locally at:
  `~/Library/CloudStorage/OneDrive-SharedLibraries-BluewaterGroup/Marketing - Documents/`
- It mirrors the exact tree the MCP sees (`.../Marketing - Documents/Distributor Folder/Content (Images, Videos and Renders)/...` ↔ SharePoint `sites/Marketing2024/Shared Documents/Distributor Folder/...`).
- Plain `cp` of a cloud-only file triggers the on-demand download transparently; `file` confirms a valid JPEG.
- `source.type` for imports via this path: `"onedrive-sync"`; `source.path` records the path relative to `Marketing - Documents/`.

### Figma `upload_assets` behavior
- `upload_assets(count: 1)` returns a single-use `submitUrl` (10-minute expiry).
- `curl -X POST -F "file=@<path>;type=image/jpeg" "<submitUrl>"` works; multipart is preferred because **the filename becomes the Figma layer name**.
- Response: `{ success, imageHash, sizeBytes, contentType, placedOnNodeId }`.
- The asset lands as a **400×300 FRAME with an IMAGE fill (FILL scale mode) on the file's CURRENT page** — in the spike it landed on page "—————BRAND———————" (`56400:9207`), NOT the Brand Assets page.
- Therefore the `/import-assets` command MUST, after upload: move the node to the Brand Assets page (`51124:14`), resize it to the image's native aspect, and rename it to the asset key.
- Max 5 upload URLs per `upload_assets` call (`count: 1–5`); batch in fives for larger imports.

## Implications for `/import-assets`

1. Discovery: `sharepoint_folder_search` (MCP) or `find`/`mdfind` over the synced tree — both see the same folders; local `find` also sees the image FILES, which the MCP cannot.
2. Fetch: copy from the synced tree to a temp dir (`cp` handles cloud-only files).
3. Upload: `upload_assets` in batches of ≤5, multipart POST with the intended asset-key filename.
4. Post-upload (one `use_figma` pass): move each `placedOnNodeId` to Brand Assets (`51124:14`), resize to native aspect, arrange the Import inbox grid.
