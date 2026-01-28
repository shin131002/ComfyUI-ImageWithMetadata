# Load Image with Metadata - 使い方

**日本語** | [English](USAGE_en.md)

## 推奨パターン: Group Node化して使用

**任意の位置から順番に処理できる統合ノードを作成**

### 手順1: 基本構成を作成

1. **Integerノード**を追加
   - 右クリック → Add Node → utils → Integer
   - value: 0（開始位置）
   - control_before_generate: increment

2. **Load Image with Metadata**を追加
   - mode: single_image
   - path: 画像フォルダのパス
   - pattern: *
   - label: Batch 001

3. **接続**
   - Integer の value → Load Image with Metadata の index


### 手順2: Group Node化

1. **2つのノードを選択**
   - Integer と Load Image with Metadata を両方選択

2. **Group化**
   - 右クリック → Convert to Group

3. **Group名を設定**
   - "Load Image Batch with Index" など

4. **保存**
   - これで統合ノードとして再利用可能

### 完成イメージ

```
┌──────────────────────────────────┐
│ Load Image Batch with Index      │
│                                  │
│  index value: 50                 │
│  生成前の制御: increment          │
│  mode: single_image              │
│  path: C:\output\folder          │
│  pattern: *                      │
│  label: Batch 001                │
│                                  │
│  出力:                            │
│  - image                         │
│  - positive_prompt               │
│  - negative_prompt               │
│  - info                          │
│  - filename_text                 │
│  - seed, steps, cfg              │
└──────────────────────────────────┘
```
![Convert to Group example](./images/load_02.webp)


**動作:**
1. 最初の実行: index=50 → 51枚目を処理
2. 自動でindex=51に増加
3. 次の実行: index=51 → 52枚目を処理
4. 以降、自動で進む

---

## モード説明

### incremental_image モード
**フォルダ内の画像を順番に自動処理**

```
Load Image with Metadata
├─ mode: incremental_image
├─ path: C:\ComfyUI\output\folder
├─ pattern: *
├─ label: Batch 001
└─ index: 0 （このモードでは無視される）
```

**動作:**
- 1回目の実行: 1枚目
- 2回目の実行: 2枚目
- 3回目の実行: 3枚目
- ...と自動で進む

**用途:** フォルダ全体を最初から順番に処理したい場合

**制限:** 途中から開始できない（常に前回の続きから）

---

### single_image モード（推奨）
**指定したindex番号の画像を読み込む**

```
Integer (increment) → Load Image with Metadata
                      ├─ mode: single_image
                      ├─ index: ← (外部から受け取る)
                      └─ path: C:\output\folder
```

**動作:**
- index=0 → 1枚目
- index=5 → 6枚目
- index=50 → 51枚目

**メリット:**
- ✅ 途中から開始できる（50枚目から、など）
- ✅ index値を確認できる
- ✅ 手動でindex値を変更可能
- ✅ 処理の進捗が分かりやすい

---

## パラメータ説明

**mode:**
- `single_image`: index指定
- `incremental_image`: 自動順送り

**path:**
- 画像フォルダのパス
- 空欄の場合: ComfyUIの入力フォルダ

**pattern:**
- `*`: すべての画像
- `*.png`: PNGのみ
- `character_*.jpg`: character_で始まるJPG

**label:**
- バッチを識別する名前
- 異なるフォルダを処理する場合は必ず変更
- 例: "Upscale_Batch_001", "Test_001"

**index:**
- single_imageモード: 読み込む画像番号（0始まり）
- incrementalモード: 無視される

**filename_text_extension:**
- `true`: "image.png" → "image.png"
- `false`: "image.png" → "image"

---

## 出力

1. **image**: 画像テンソル
2. **positive_prompt**: ポジティブプロンプト
3. **negative_prompt**: ネガティブプロンプト
4. **info**: MODEL/VAE/Sampler/Scheduler情報
5. **filename_text**: ファイル名
6. **seed**: シード値
7. **steps**: ステップ数
8. **cfg**: CFG値

---

## よくある質問

**Q: 50枚目から処理を始めたい**
A: single_imageモード + 外部indexノード（value=50）を使用

**Q: フォルダ内の全画像を順番に処理したい**
A: incremental_imageモードを使用

**Q: 複数の異なるフォルダを同時に処理したい**
A: labelを変える（例: "Folder_A", "Folder_B"）

**Q: サブフォルダも含めて検索したい**
A: pattern に `**/*` を使用（recursive検索）

---

## ライセンス

このノードはWAS Node Suite (MIT License) のコードを基にしています。
https://github.com/WASasquatch/was-node-suite-comfyui

---

# Random Checkpoint Loader with Names - 使い方

## 概要

複数のチェックポイントを順番に、またはランダムに切り替えながら画像生成を行うノードです。

## ⚠️ 重要：path指定を推奨

**BaseModel（SD1.5/SDXL/Illustrious/SD3.5など）が異なるチェックポイントが混在している場合、意図しないモデルが読み込まれてエラーの原因になります。**

### ✅ 推奨設定
```
path: F:\models\SDXL
sub_folders: true
pattern: *
```

### ⚠️ 非推奨設定
```
path: （空欄）
→ 全checkpointsフォルダから選択（SD1.5/SDXL/SD3混在の危険）
```

---

## パラメータ詳細

### mode
- `single`: 外部indexで順次切り替え（推奨）
  - Integerノード（increment）と接続して使用
  - バッチ処理に最適
- `random`: seedベースのランダム選択
  - 毎回異なるモデルで生成
  - seedが同じなら再現可能

### seed
- ランダムモード用のseed値
- singleモードでは無視される
- 同じseedなら同じモデルが選ばれる

### path（重要）
- **空欄**: 全checkpointsフォルダから選択（非推奨）
- **絶対パス指定**: 指定フォルダ以下から選択（推奨）
- 例: `C:\models\SDXL`, `F:\checkpoints\Illustrious`
- フォルダが存在しない場合は自動でcheckpointsフォルダにフォールバック

### sub_folders
- `false`: 指定フォルダ直下のみ
- `true`: サブフォルダ含む（再帰検索）

### pattern
- `*`: すべてのファイル
- `anime_*`: anime_で始まるファイル
- `*.safetensors`: safetensorsのみ
- `character_*`: character_で始まるファイル

### label
- 複数のノードを使う場合の識別子
- 異なるフォルダを処理する場合は別のlabelを使用
- 例: "SDXL_Batch", "Illustrious_Test"

### index
- singleモード用
- 外部Integerノード（increment）から接続
- リスト数を超えると先頭に戻る（ループ）

### vae_name
- `Baked VAE`: チェックポイント内蔵VAE
- その他: 外部VAEを選択

---

## 使用例

### 例1: illustriousモデルで順次バッチ生成

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
  └─ index: ← Integer接続
    ↓
  checkpoint_name → Save Image with Metadata
  MODEL, CLIP, VAE → KSampler
```

**動作:**
1. 1回目: F:\models\SDXL内の1番目のモデル
2. 2回目: 2番目のモデル
3. 3回目: 3番目のモデル
4. ...自動で順次切り替え

---

### 例2: ランダムモデル選択

```
Random Checkpoint Loader with Names
  ├─ mode: random
  ├─ seed: 12345
  ├─ path: F:\models\Illustrious
  └─ pattern: *.safetensors
    ↓
  毎回ランダムなモデルで生成
```

---

### 例3: 特定の名前のモデルのみ

![Random Checkpoint Loader - Single Mode](./images/random_cp_single02.webp)

```
Random Checkpoint Loader with Names
  ├─ mode: single
  ├─ path: F:\models\characters
  ├─ sub_folders: false
  ├─ pattern: wai*
  └─ label: wai_CP
```

F:\models\characters直下の`wai`で始まるモデルのみ対象

---

## FAQ

**Q: 複数のBaseModelフォルダを切り替えたい**
A: 複数のノードを配置し、labelを変えて使用
```
ノード1: path=F:\SDXL, label=SDXL_Batch
ノード2: path=F:\SD15, label=SD15_Batch
```

**Q: index=100で10個しかモデルがない場合は？**
A: 自動でループ（100 % 10 = 0 → 1番目のモデル）

**Q: pathを空欄にするとどうなる？**
A: 全checkpointsフォルダから選択されるが、BaseModelが混在するため非推奨

**Q: エラー "Model not found" が出る**
A: 
1. pathが正しいか確認
2. sub_foldersの設定を確認
3. patternが正しいか確認
4. extra_model_paths.yamlの設定を確認

---

## ライセンス

このノードはWAS Node Suite (MIT License)のコードを基にしています。
https://github.com/WASasquatch/was-node-suite-comfyui
