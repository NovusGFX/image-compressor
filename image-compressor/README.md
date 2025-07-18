# 🖼️ Bulk Image Compressor (Terminal-based)

A Python script to compress images in bulk by target **percentage** or **file size**, with logging, ascii banners, and support for PNG transparency using `pngquant`.

## 🚀 Features

- Bulk compress entire folders
- Compression by % of original size or to target MB
- Preserve folder structure (optional)
- PNG transparency preserved using `pngquant`
- JPEG/WebP compressed using Pillow
- Interactive terminal prompts and CLI installable

## 🧪 Requirements

### Python

```bash
pip install -r requirements.txt
```

### System Dependency (for PNG support)

You must install `pngquant`:

- Windows: [https://pngquant.org](https://pngquant.org)
- macOS: `brew install pngquant`
- Linux: `sudo apt install pngquant`

## 📂 Usage

```bash
python compressor.py
```

or, after install:

```bash
image-compressor
```

## 📄 License

MIT