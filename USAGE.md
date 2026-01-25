# Load Image with Metadata - Usage Guide

[日本語版](USAGE_ja.md) | **English**

## Recommended Pattern: Group Node Integration

**Create a unified node that can process images sequentially from any starting position**

### Step 1: Create Basic Setup

1. **Add Integer node**
   - Right-click → Add Node → utils → Integer
   - value: 0 (starting position)
   - control_before_generate: increment

2. **Add Load Image with Metadata**
   - mode: single_image
   - path: your image folder path
   - pattern: *
   - label: Batch 001

3. **Connect**
   - Integer's value → Load Image with Metadata's index

### Step 2: Convert to Group Node

1. **Select both nodes**
   - Select both Integer and Load Image with Metadata

2. **Group them**
   - Right-click → Convert to Group

3. **Set Group name**
   - e.g., "Load Image Batch with Index"

4. **Save**
   - Now reusable as a unified node

### Completed Image

```
┌──────────────────────────────────┐
│ Load Image Batch with Index      │
│                                  │
│  index value: 50                 │
│  control_before_generate: incr.  │
│  mode: single_image              │
│  path: C:\output\folder          │
│  pattern: *                      │
│  label: Batch 001                │
│                                  │
│  Outputs:                        │
│  - image                         │
│  - positive_prompt               │
│  - negative_prompt               │
│  - info                          │
│  - filename_text                 │
│  - seed, steps, cfg              │
└──────────────────────────────────┘
```

**How it works:**
1. First execution: index=50 → loads 51st image
2. Automatically increments to index=51
3. Next execution: index=51 → loads 52nd image
4. Continues automatically

---

## Mode Explanation

### incremental_image Mode
**Process images in folder sequentially**

```
Load Image with Metadata
├─ mode: incremental_image
├─ path: C:\ComfyUI\output\folder
├─ pattern: *
├─ label: Batch 001
└─ index: 0 (ignored in this mode)
```

**Behavior:**
- 1st execution: 1st image
- 2nd execution: 2nd image
- 3rd execution: 3rd image
- ...continues automatically

**Use case:** Process entire folder sequentially from start

**Limitation:** Cannot start from middle (always continues from last position)

---

### single_image Mode (Recommended)
**Load image at specified index**

```
Integer (increment) → Load Image with Metadata
                      ├─ mode: single_image
                      ├─ index: ← (from external)
                      └─ path: C:\output\folder
```

**Behavior:**
- index=0 → 1st image
- index=5 → 6th image
- index=50 → 51st image

**Benefits:**
- ✅ Start from any position (e.g., from 50th image)
- ✅ See current index value
- ✅ Manually adjust index if needed
- ✅ Clear progress tracking

---

## Parameter Details

### mode
- `single_image`: Load image at specified index (recommended with external counter)
- `incremental_image`: Auto-advance through folder

### path
- Image folder path
- Empty = ComfyUI input folder

### pattern
- `*`: All images
- `*.png`: PNG only
- `character_*.jpg`: JPG files starting with "character_"

### label
- Batch identifier
- **Important:** Change label when processing different folders
- Examples: "Upscale_Batch_001", "Test_001"

### index
- Image number to load (0-based)
- single_image mode: Used
- incremental_image mode: Ignored

### filename_text_extension
- `true`: "image.png" → "image.png"
- `false`: "image.png" → "image"

---

## Outputs

1. **image**: Image tensor
2. **positive_prompt**: Positive prompt text
3. **negative_prompt**: Negative prompt text
4. **info**: MODEL/VAE/Sampler/Scheduler information
5. **filename_text**: Filename
6. **seed**: Seed value
7. **steps**: Step count
8. **cfg**: CFG scale

---

## FAQ

**Q: Want to start processing from 50th image**
A: Use single_image mode + external Integer node (value=50)

**Q: Want to process all images in folder sequentially**
A: Use incremental_image mode

**Q: Want to process multiple different folders simultaneously**
A: Change label for each (e.g., "Folder_A", "Folder_B")

**Q: Want to search including subfolders**
A: Use `**/*` in pattern (recursive search)

**Q: What happens after reaching the last image?**
A: Automatically loops back to the first image

---

## License

This node is based on code from WAS Node Suite (MIT License).
https://github.com/WASasquatch/was-node-suite-comfyui
