import argparse
from pathlib import Path

import cv2
import numpy as np


def read_image(path: Path) -> np.ndarray | None:
    data = np.fromfile(path, dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def write_image(path: Path, image: np.ndarray) -> bool:
    suffix = path.suffix if path.suffix else ".png"
    ok, encoded = cv2.imencode(suffix, image)
    if not ok:
        return False
    encoded.tofile(path)
    return True


def build_comparison_image(
    input_image: np.ndarray, output_image: np.ndarray
) -> np.ndarray:
    if input_image.shape[:2] != output_image.shape[:2]:
        output_image = cv2.resize(
            output_image,
            (input_image.shape[1], input_image.shape[0]),
            interpolation=cv2.INTER_LINEAR,
        )

    label_height = 50
    left_label = np.full((label_height, input_image.shape[1], 3), 255, dtype=np.uint8)
    right_label = np.full((label_height, output_image.shape[1], 3), 255, dtype=np.uint8)

    cv2.putText(
        left_label,
        "Original",
        (20, 33),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (30, 30, 30),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        right_label,
        "Cartoon",
        (20, 33),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (30, 30, 30),
        2,
        cv2.LINE_AA,
    )

    left_panel = np.vstack((left_label, input_image))
    right_panel = np.vstack((right_label, output_image))
    divider = np.full((left_panel.shape[0], 12, 3), 220, dtype=np.uint8)
    return np.hstack((left_panel, divider, right_panel))


def show_result(input_image: np.ndarray, output_image: np.ndarray) -> None:
    comparison = build_comparison_image(input_image, output_image)
    cv2.namedWindow("Cartoon Comparison", cv2.WINDOW_NORMAL)
    cv2.imshow("Cartoon Comparison", comparison)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def cartoonize(image: np.ndarray) -> np.ndarray:
    """Convert an image into a cartoon-like rendering."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 7)

    edges = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        9,
        7,
    )

    # Smooth colors while keeping object regions relatively flat.
    color = cv2.bilateralFilter(image, d=9, sigmaColor=150, sigmaSpace=150)
    color = cv2.bilateralFilter(color, d=7, sigmaColor=120, sigmaSpace=120)

    # Reduce the number of colors to emphasize a cartoon palette.
    data = np.float32(color.reshape((-1, 3)))
    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        20,
        1.0,
    )
    _, labels, centers = cv2.kmeans(
        data,
        8,
        None,
        criteria,
        5,
        cv2.KMEANS_PP_CENTERS,
    )
    quantized = centers[labels.flatten()].reshape(color.shape).astype(np.uint8)

    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    return cv2.bitwise_and(quantized, edges_bgr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render an input image in a cartoon style using OpenCV."
    )
    parser.add_argument("input", type=Path, help="Path to the input image")
    parser.add_argument("output", type=Path, help="Path to the output image")
    parser.add_argument(
        "--no-ui",
        action="store_true",
        help="Do not open OpenCV windows. Useful for automated runs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    image = read_image(args.input)
    if image is None:
        raise FileNotFoundError(f"Could not read input image: {args.input}")

    if args.output.exists():
        output = read_image(args.output)
        if output is None:
            raise RuntimeError(
                f"Output file exists but could not be read: {args.output}"
            )
        print(f"Output already exists. Reusing saved image: {args.output}")
    else:
        output = cartoonize(image)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if not write_image(args.output, output):
            raise RuntimeError(f"Could not write output image: {args.output}")
        print(f"Saved cartoon image: {args.output}")

    if not args.no_ui:
        show_result(image, output)


if __name__ == "__main__":
    main()
