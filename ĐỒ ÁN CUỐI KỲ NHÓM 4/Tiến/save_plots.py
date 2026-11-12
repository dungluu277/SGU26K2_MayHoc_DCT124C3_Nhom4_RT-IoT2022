from pathlib import Path
import re

import matplotlib.pyplot as plt


OUTPUT_DIR = Path(__file__).resolve().parent / "ket_qua_hinh"


def save_and_show(name: str) -> Path:
    """Save the current plot as a PNG, then display it in the notebook."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = re.sub(r"[^\w.-]+", "_", name.strip(), flags=re.UNICODE).strip("._")
    if not safe_name:
        safe_name = "hinh"

    index = 1
    while any(OUTPUT_DIR.glob(f"{index:03d}_*.png")):
        index += 1

    image_path = OUTPUT_DIR / f"{index:03d}_{safe_name}.png"
    plt.savefig(image_path, dpi=150, bbox_inches="tight")
    plt.show()
    return image_path
