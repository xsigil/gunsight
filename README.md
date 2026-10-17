# gunsight

> Robust, scale-invariant GUI target locator powered by SIFT and Homography.

`gunsight` is a lightweight, single-purpose CLI utility designed for desktop automation. It detects target visual elements within a full desktop screenshot and outputs the exact click coordinates to `stdout`.

Unlike fragile template-matching libraries (`cv2.matchTemplate`, PyAutoGUI, Sikuli) that fail when sub-pixel antialiasing, DPI scaling, or display resolutions shift, `gunsight` computes scale-invariant keypoints (SIFT) and a perspective transformation matrix (RANSAC Homography) to achieve deterministic target acquisition.

## Features

- **Scale & Resolution Invariant**: SIFT features stay consistent across DPI scaling and minor UI dimension shifts.
- **Outlier Rejection (RANSAC)**: Robust against noisy backgrounds and complex desktop clutter.
- **UNIX Pipeline Ready**: Emits clean CLI coordinate flags directly to `stdout`.
- **Zero Heavy Frameworks**: No heavy browser drivers or monolithic RPA suites.

## Quick Start

### Installation

```bash
pip install .

```

Or via Nix Flakes:

```bash
nix run github:<your-username>/gunsight -- --help

```

### Automation Examples

#### macOS with `cliclick`

```bash
screencapture -x /tmp/screen.png
gunsight /tmp/screen.png ./assets/submit_button.png | xargs cliclick c:

```

#### Linux with `xdotool`

```bash
maim /tmp/screen.png
COORDS=$(gunsight --raw /tmp/screen.png ./assets/submit_button.png)
if [ $? -eq 0 ]; then
    xdotool mousemove $COORDS click 1
fi

```

## CLI Options

```text
Usage: gunsight [OPTIONS] DESKTOP_IMAGE TARGET_IMAGE

Arguments:
  DESKTOP_IMAGE  Path to full desktop screenshot.  [required]
  TARGET_IMAGE   Path to visual target image.      [required]

Options:
  --min-matches INTEGER  Minimum feature matches required. [default: 30]
  --raw                  Output only "X Y" coordinate pair instead of click flags.
  --help                 Show this message and exit.

```


---

### 7. `.github/workflows/release.yml`（単一バイナリの自動ビルド配布）

GitHubでタグ（例: `v0.1.0`）を打って push すると、GitHub Actions が自動で Linux用・macOS用のスタンドアロン・モノリシックバイナリを PyInstaller でビルドし、Release ページにアップロードしてくれるCI設定です。

```yaml
name: Release Standalone Binaries

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            artifact_name: gunsight-linux-x86_64
          - os: macos-latest
            artifact_name: gunsight-macos-x86_64

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install opencv-python-headless numpy click pyinstaller

      - name: Build Standalone Binary
        run: |
          pyinstaller --onefile --name gunsight gunsight.py

      - name: Rename Artifact
        run: |
          mv dist/gunsight dist/${{ matrix.artifact_name }}

      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.artifact_name }}
          path: dist/${{ matrix.artifact_name }}

  release:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
      - name: Create Release
        uses: softprops/action-gh-release@v2
        with:
          files: gunsight-*/*

```

