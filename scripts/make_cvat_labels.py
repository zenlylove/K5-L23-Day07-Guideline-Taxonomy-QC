"""Sinh JSON để dán vào CVAT (Project -> Labels -> tab Raw) từ submission/taxonomy.json.

    python scripts/make_cvat_labels.py

Ghi ra cvat/labels_generated.json và in ra màn hình. Mỗi lần đổi taxonomy.json thì chạy lại
và dán lại vào CVAT để mọi người dùng đúng cùng một bộ lớp/thuộc tính.
"""
from __future__ import annotations

import argparse
import json

from common import ROOT, final_taxonomy_path, load_taxonomy, rel

COLORS = ["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4", "#46c8c8", "#f032e6", "#9a6324",
          "#808000", "#008080", "#800000", "#000075"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--final", action="store_true", help="Sinh cấu hình cho taxonomy sau calibration.")
    args = parser.parse_args()
    tax = load_taxonomy(final_taxonomy_path()) if args.final else load_taxonomy()
    labels = []
    for i, name in enumerate(tax.classes):
        attrs = []
        if name != tax.ignore:
            for a in tax.attrs.values():
                attrs.append({
                    "name": a["name"],
                    "mutable": False,
                    "input_type": a["type"],
                    "default_value": str(a.get("default", "")),
                    "values": ([str(v) for v in a.get("values", [])]
                               if a["type"] == "select" else ["true", "false"]),
                })
        labels.append({"name": name, "color": "#808080" if name == tax.ignore else COLORS[i % len(COLORS)],
                       "type": "rectangle",
                       "attributes": attrs})
    text = json.dumps(labels, ensure_ascii=False, indent=2)
    out = ROOT / "cvat" / ("labels_final.json" if args.final else "labels_generated.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(text + "\n", encoding="utf8")
    print(text)
    print(f"\n# Đã ghi {rel(out)} (taxonomy {tax.version}). Dán nội dung vào CVAT: Project -> Labels -> Raw -> Done.")


if __name__ == "__main__":
    main()
