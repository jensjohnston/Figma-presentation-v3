# Sync Brand Assets

Scan the "Brand Assets" page in Figma and update the local asset library.

## Usage
```
/sync-assets
```

## What it does

1. Reads `assets/library.json` to get the Brand Assets page ID
2. Uses `get_metadata` to scan all frames/rectangles on that page
3. For each named node that has an image fill, adds it to the library
4. Asks the user to add tags for any NEW assets (assets already in the library keep their existing tags)
5. Writes the updated `assets/library.json`

## Process

### Step 1: Read current library

Read `assets/library.json` from the project root. Note the `assetPageId` and any existing assets (so we don't overwrite their tags).

### Step 2: Scan the Brand Assets page

Use `get_metadata` with the `assetPageId` and `fileKey` from `templates/registry.json` to list all children on the Brand Assets page.

Collect every frame or rectangle that is a direct child of the page (skip the instruction text node). Record:
- `name` (the layer name the user gave it)
- `nodeId`

### Step 3: Detect new vs existing assets

Compare the scanned nodes against existing assets in `library.json`:
- **Existing**: Keep current tags and description
- **New**: Ask the user to provide tags and a short description using AskUserQuestion

For new assets, suggest tags based on the name. For example:
- `cafe-station-1-hero` → suggest tags: `["product", "cafe-station", "hero"]`
- `office-lifestyle-1` → suggest tags: `["lifestyle", "office"]`

### Step 4: Update library.json

Write the updated `assets/library.json` with all assets (existing + new).

Format:
```json
{
  "assetPageId": "PAGE_ID",
  "assetPageName": "Brand Assets",
  "assets": {
    "asset-name": {
      "nodeId": "12345:678",
      "tags": ["product", "hero"],
      "description": "Short description of the image"
    }
  }
}
```

### Step 5: Report

Show the user what was synced:
```
Asset library synced!

Existing: 3 assets (unchanged)
New: 2 assets added
  - cafe-station-1-angle: ["product", "cafe-station", "angle"]
  - sustainability-ocean: ["sustainability", "environmental", "ocean"]

Total: 5 assets in library
```
