# Load Image with Metadata - 使い方

**日本語** | [English](USAGE.md)

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
