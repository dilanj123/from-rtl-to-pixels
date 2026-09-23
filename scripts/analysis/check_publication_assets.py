import hashlib
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
IMAGE_SIZE = (640, 480)
PUBLIC_IMAGE_SHA256 = (
    "8331a2d0edb64057fdf31b1b1385430c58b2698942ef7d29e00e392b7350d5e4"
)


def verify_assets():
    source_image = ROOT / "tb/images/Tokinokane2005-1-4.jpg"
    gradient_image = ROOT / "tb/images/gradient-grid-640x480.png"
    assert hashlib.sha256(source_image.read_bytes()).hexdigest() == PUBLIC_IMAGE_SHA256
    assert gradient_image.is_file()

    real_outputs = [
        ROOT / "results/processed/arch-b/gate3-real-reference.png",
        ROOT / "results/processed/arch-b/gate3-real-rtl.png",
        ROOT / "results/processed/arch-b/gate3-real-diff.png",
        ROOT / "results/processed/arch-b/arch-a-vs-b-diff.png",
    ]
    gradient_outputs = [
        ROOT / "results/processed/public-gradient-a/gate3-real-reference.png",
        ROOT / "results/processed/public-gradient-a/gate3-real-rtl.png",
        ROOT / "results/processed/public-gradient-a/gate3-real-diff.png",
        ROOT / "results/processed/public-gradient-b/gate3-real-rtl.png",
        ROOT / "results/processed/public-gradient-a-vs-b-diff.png",
    ]

    for path in [source_image, gradient_image, *real_outputs, *gradient_outputs]:
        with Image.open(path) as image:
            assert image.size == IMAGE_SIZE, (path, image.size)

    for path in [real_outputs[2], real_outputs[3], gradient_outputs[2], gradient_outputs[4]]:
        with Image.open(path) as image:
            assert np.asarray(image).max() == 0, path


def verify_markdown_links():
    broken = []
    tracked_markdown = subprocess.check_output(
        ["git", "ls-files", "*.md"], cwd=ROOT, text=True
    ).splitlines()
    markdown_link_pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

    for relative_path in tracked_markdown:
        markdown_path = ROOT / relative_path
        if not markdown_path.exists():
            continue
        for target in markdown_link_pattern.findall(markdown_path.read_text()):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_path = target.split("#", 1)[0]
            if target_path and not (markdown_path.parent / target_path).exists():
                broken.append(f"{markdown_path}:{target_path}")

    assert not broken, "broken repository links: " + ", ".join(broken)


def main():
    verify_assets()
    print("PUBLICATION_ASSETS=PASS")
    verify_markdown_links()
    print("REPOSITORY_MARKDOWN_LINKS=PASS")


if __name__ == "__main__":
    main()
