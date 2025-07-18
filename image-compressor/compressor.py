import os
import time
from pathlib import Path
from PIL import Image, ImageFile
from io import BytesIO

ImageFile.LOAD_TRUNCATED_IMAGES = True

SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".webp")

ASCII_BANNER = r"""
 ▄▄·       • ▌ ▄ ·.  ▄▄▄·▄▄▄  ▄▄▄ ..▄▄ · .▄▄ ·       ▄▄▄  
▐█ ▌▪▪     ·██ ▐███▪▐█ ▄█▀▄ █·▀▄.▀·▐█ ▀. ▐█ ▀. ▪     ▀▄ █·
██ ▄▄ ▄█▀▄ ▐█ ▌▐▌▐█· ██▀·▐▀▀▄ ▐▀▀▪▄▄▀▀▀█▄▄▀▀▀█▄ ▄█▀▄ ▐▀▀▄ 
▐███▌▐█▌.▐▌██ ██▌▐█▌▐█▪·•▐█•█▌▐█▄▄▌▐█▄▪▐█▐█▄▪▐█▐█▌.▐▌▐█•█▌
·▀▀▀  ▀█▄▀▪▀▀  █▪▀▀▀.▀   .▀  ▀ ▀▀▀  ▀▀▀▀  ▀▀▀▀  ▀█▄▀▪.▀  ▀
"""

def get_total_folder_size_mb(folder):
    total_size = 0
    file_count = 0
    for dirpath, _, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
                file_count += 1
    return file_count, total_size / (1024 * 1024)

def compress_image(input_path, output_path, target_percent=None, target_size_mb=None, min_quality=10, max_quality=95):
    try:
        image = Image.open(input_path)
        image_format = image.format
        original_size = os.path.getsize(input_path)

        if target_percent:
            target_size = original_size * (target_percent / 100)
        else:
            target_size = target_size_mb * 1024 * 1024
        if original_size <= target_size:
            print(f"\033[93m[!] {input_path.name} is already under target size. Skipping.\033[0m")
            return False

        # Force convert PNGs (even with transparency) to JPEG
        if image_format.lower() == "png":
            if image.mode in ("RGBA", "LA"):
                print(f"\033[93m[!] {input_path.name} has transparency. Flattening and converting to JPEG.\033[0m")
                image = image.convert("RGB")
            else:
                image = image.convert("RGB")
            image_format = "JPEG"
            output_path = output_path.with_suffix(".jpg")

        best_output = None
        low, high = min_quality, max_quality
        best_quality = min_quality

        while low <= high:
            mid = (low + high) // 2
            buffer = BytesIO()
            image.save(buffer, format=image_format, quality=mid, optimize=True, progressive=True)
            size = buffer.tell()
            if size <= target_size:
                best_output = buffer.getvalue()
                best_quality = mid
                low = mid + 1
            else:
                high = mid - 1

        if best_output:
            os.makedirs(output_path.parent, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(best_output)
            final_size = len(best_output) / 1024 / 1024
            if final_size <= target_size / 1024 / 1024:
                print(f"\033[92m[✔] {input_path.name} → {output_path.name} ({final_size:.2f}MB @ quality {best_quality})\033[0m")
            else:
                print(f"\033[93m[⚠] {input_path.name} compressed to {final_size:.2f}MB but not under target. Saved anyway.\033[0m")
            return True
        else:
            print(f"\033[91m[✘] Could not compress {input_path.name} to target size.\033[0m")
            return False

    except Exception as e:
        print(f"\033[91m[✘] Error processing {input_path.name}: {e}\033[0m")
        return False

def compress_folder(input_dir, output_dir, target_percent=None, target_size_mb=None, preserve_structure=True):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    total_files = 0
    success_count = 0
    fail_count = 0

    print(f"\n📁 Scanning folder: {input_dir.resolve()}")
    for root, _, files in os.walk(input_dir):
        for file in files:
            if not file.lower().endswith(SUPPORTED_FORMATS):
                print(f"\033[90m[-] Skipping unsupported file: {file}\033[0m")
                continue

            input_path = Path(root) / file
            if preserve_structure:
                relative_path = input_path.relative_to(input_dir)
                output_path = output_dir / relative_path
            else:
                output_path = output_dir / file

            print(f"⏳ Compressing: {input_path}")
            result = compress_image(input_path, output_path, target_percent, target_size_mb)

            total_files += 1
            if result:
                success_count += 1
            else:
                fail_count += 1

    print(f"\n📊 Compression summary: {success_count}/{total_files} succeeded, {fail_count} failed.\n")

def main():
    print(ASCII_BANNER)
    print("🖼️  Bulk Image Compressor\n")

    input_path = input("📂 Enter input file or folder path: ").strip()
    while not os.path.exists(input_path):
        input_path = input("❗ Path not found. Try again: ").strip()

    output_path = input("💾 Enter output folder path: ").strip()
    os.makedirs(output_path, exist_ok=True)

    mode = ""
    while mode not in ["1", "2"]:
        print("\nChoose compression method:")
        print("1. Compress by percent of original size")
        print("2. Compress to target file size (in MB)")
        mode = input("Your choice (1 or 2): ").strip()

    target_percent = target_size_mb = None
    if mode == "1":
        target_percent = float(input("Enter target percent (e.g., 50 for 50%): ").strip())
    else:
        target_size_mb = float(input("Enter target size in MB (e.g., 1.5): ").strip())

    preserve_structure = "y"
    if os.path.isdir(input_path):
        while preserve_structure.lower() not in ["y", "n"]:
            preserve_structure = input("Preserve folder structure? (y/n): ").strip().lower()

    start = time.time()
    print("\n🔧 Starting compression...\n")

    if os.path.isfile(input_path):
        output_file = os.path.join(output_path, os.path.basename(input_path))
        compress_image(Path(input_path), Path(output_file), target_percent, target_size_mb)
    elif os.path.isdir(input_path):
        compress_folder(
            Path(input_path),
            Path(output_path),
            target_percent,
            target_size_mb,
            preserve_structure=(preserve_structure == "y")
        )

    elapsed = time.time() - start
    file_count, total_mb = get_total_folder_size_mb(output_path)
    print(f"\n📦 Output folder contains {file_count} file(s), totaling {total_mb:.2f} MB.")
    print(f"⏱️ Finished in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()# This will be replaced in post step
