# Load Image with Metadata - Usage Guide

**English** | [日本語版](USAGE_ja.md)

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
![Convert to Group example](./images/load_02.webp)

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

---

## License

This node is based on code from WAS Node Suite (MIT License).
https://github.com/WASasquatch/was-node-suite-comfyui

---

# Random Checkpoint Loader with Names - Usage Guide

## Overview

Node for generating images while switching between multiple checkpoints sequentially or randomly.

## ⚠️ Important: Path Specification Recommended

**If checkpoints with different BaseModels (SD1.5/SDXL/Illustrious/SD3.5, etc.) are mixed, unintended models may be loaded, causing errors.**

### ✅ Recommended Settings
```
path: F:\models\SDXL
sub_folders: true
pattern: *
```

### ⚠️ Not Recommended
```
path: (empty)
→ Selects from all checkpoints folders (risk of SD1.5/SDXL/SD3 mixing)
```

---

## Parameter Details

### mode
- `single`: Sequential switching with external index (recommended)
  - Use with Integer node (increment)
  - Optimal for batch processing
- `random`: Seed-based random selection
  - Different model each time
  - Reproducible with same seed

### seed
- Seed value for random mode
- Ignored in single mode
- Same seed = same model selection

### path (Important)
- **Empty**: Select from all checkpoints folders (not recommended)
- **Absolute path**: Select from specified folder (recommended)
- Examples: `C:\models\SDXL`, `F:\checkpoints\Illustrious`
- Falls back to checkpoints folder if path doesn't exist

### sub_folders
- `false`: Specified folder only
- `true`: Include subfolders (recursive search)

### pattern
- `*`: All files
- `anime_*`: Files starting with "anime_"
- `*.safetensors`: safetensors only
- `character_*`: Files starting with "character_"

### label
- Identifier when using multiple nodes
- Use different labels for different folders
- Examples: "SDXL_Batch", "Illustrious_Test"

### index
- For single mode
- Connect from external Integer node (increment)
- Loops back to start when exceeding list length

### vae_name
- `Baked VAE`: Checkpoint's baked VAE
- Others: Select external VAE

---

## Usage Examples

### Example 1: Sequential Batch Generation with Illustrious Models

![Random Checkpoint Loader - Single Mode](./images/random_cp_single01.webp)

```
Integer (increment, value=0)
  ↓
Random Checkpoint Loader with Names
  ├─ mode: single
  ├─ path: F:\models\SDXL
  ├─ sub_folders: true
  ├─ pattern: *
  ├─ label: SDXL_Batch
  └─ index: ← Integer connection
    ↓
  checkpoint_name → Save Image with Metadata
  MODEL, CLIP, VAE → KSampler
```

**Operation:**
1. 1st time: 1st model in F:\models\SDXL
2. 2nd time: 2nd model
3. 3rd time: 3rd model
4. ...automatically switches sequentially

---

### Example 2: Random Model Selection

```
Random Checkpoint Loader with Names
  ├─ mode: random
  ├─ seed: 12345
  ├─ path: F:\models\Illustrious
  └─ pattern: *.safetensors
    ↓
  Generates with random model each time
```

---

### Example 3: Specific Named Models Only

![Random Checkpoint Loader - Single Mode](./images/random_cp_single02.webp)

```
Random Checkpoint Loader with Names
  ├─ mode: single
  ├─ path: F:\models\characters
  ├─ sub_folders: false
  ├─ pattern: wai*
  └─ label: wai_CP
```

Only models starting with `wai` directly under F:\models\characters

---

## FAQ

**Q: Want to switch between multiple BaseModel folders**
A: Use multiple nodes with different labels
```
Node 1: path=F:\SDXL, label=SDXL_Batch
Node 2: path=F:\SD15, label=SD15_Batch
```

**Q: What happens with index=100 when only 10 models exist?**
A: Automatically loops (100 % 10 = 0 → 1st model)

**Q: What happens if path is empty?**
A: Selects from all checkpoints folders, but not recommended due to BaseModel mixing

**Q: Getting "Model not found" error**
A: 
1. Verify path is correct
2. Check sub_folders setting
3. Verify pattern is correct
4. Check extra_model_paths.yaml configuration

---

## License

This node is based on code from WAS Node Suite (MIT License).
https://github.com/WASasquatch/was-node-suite-comfyui
