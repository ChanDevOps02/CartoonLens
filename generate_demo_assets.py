from pathlib import Path

import cv2
import numpy as np

from cartoon_render import cartoonize, write_image


ROOT = Path(__file__).resolve().parent
INPUT_DIR = ROOT / "images" / "input"
OUTPUT_DIR = ROOT / "images" / "output"


def save_image(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not write_image(path, image):
        raise RuntimeError(f"Could not write image: {path}")


def create_good_case() -> np.ndarray:
    image = np.full((480, 640, 3), (245, 235, 210), dtype=np.uint8)

    for y in range(image.shape[0]):
        ratio = y / image.shape[0]
        image[y, :, 1] = np.clip(210 + 25 * ratio, 0, 255)
        image[y, :, 2] = np.clip(180 + 35 * ratio, 0, 255)

    cv2.circle(image, (520, 90), 45, (120, 220, 255), -1)
    cv2.rectangle(image, (0, 320), (640, 480), (70, 170, 90), -1)
    cv2.rectangle(image, (180, 180), (420, 360), (95, 170, 235), -1)
    cv2.rectangle(image, (260, 250), (340, 360), (60, 110, 160), -1)
    cv2.circle(image, (240, 240), 20, (240, 245, 250), -1)
    cv2.circle(image, (360, 240), 20, (240, 245, 250), -1)
    cv2.rectangle(image, (90, 230), (150, 360), (40, 80, 120), -1)
    cv2.rectangle(image, (450, 210), (520, 360), (50, 90, 140), -1)
    cv2.line(image, (0, 320), (640, 320), (50, 120, 70), 4)
    cv2.putText(
        image,
        "GOOD CASE",
        (185, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (50, 50, 50),
        3,
        cv2.LINE_AA,
    )
    return image


def create_bad_case() -> np.ndarray:
    h, w = 480, 640
    x = np.linspace(0, 1, w, dtype=np.float32)
    y = np.linspace(0, 1, h, dtype=np.float32)
    xx, yy = np.meshgrid(x, y)

    base = np.zeros((h, w, 3), dtype=np.float32)
    base[..., 0] = 160 + 60 * np.sin(8 * np.pi * xx)
    base[..., 1] = 120 + 80 * np.cos(7 * np.pi * yy)
    base[..., 2] = 140 + 90 * np.sin(5 * np.pi * (xx + yy))

    noise = np.random.default_rng(7).normal(0, 35, (h, w, 3))
    image = np.clip(base + noise, 0, 255).astype(np.uint8)

    for i in range(12):
        center = (40 + i * 48, 60 + (i % 4) * 95)
        radius = 18 + (i % 3) * 10
        color = (40 + 15 * i, 220 - 12 * i, 80 + 10 * i)
        cv2.circle(image, center, radius, color, -1)

    cv2.putText(
        image,
        "BAD CASE",
        (200, 430),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.3,
        (250, 250, 250),
        2,
        cv2.LINE_AA,
    )
    return image


def build_demo() -> None:
    good_input = create_good_case()
    bad_input = create_bad_case()

    save_image(INPUT_DIR / "good_input.png", good_input)
    save_image(INPUT_DIR / "bad_input.png", bad_input)
    save_image(OUTPUT_DIR / "good_output.png", cartoonize(good_input))
    save_image(OUTPUT_DIR / "bad_output.png", cartoonize(bad_input))


if __name__ == "__main__":
    build_demo()
