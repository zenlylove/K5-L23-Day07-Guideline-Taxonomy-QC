"""Tính số QC theo vòng duyệt và gợi ý quyết định bàn giao cho lô thực hành."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json

from common import MEMBER_RE, QC_DIR, digest, read_csv
from review_evidence import LABELS_PATH, MANIFEST_PATH, current_batch, round_dir

VALID = {"khong", "bo_sot", "thua", "sai_lop", "sai_vi_tri_kich_thuoc", "sai_thuoc_tinh"}


def checked_round(directory, number):
    tax, labels = current_batch()
    metadata = json.loads((directory / "review_manifest.json").read_text(encoding="utf-8"))
    sample_path = directory / "qc_sample.csv"
    for key, path, snapshot in (
        ("labels_sha256", LABELS_PATH, directory / "labels_snapshot.json"),
        ("batch_manifest_sha256", MANIFEST_PATH, directory / "batch_manifest_snapshot.json"),
        ("sample_sha256", sample_path, sample_path),
        ("calibration_decisions_sha256", QC_DIR / "calibration_decisions.csv",
         directory / "calibration_decisions_snapshot.csv"),
    ):
        if metadata[key] != digest(path) or metadata[key] != digest(snapshot):
            raise ValueError(f"Vòng duyệt và {path.name} không cùng phiên bản. Mở vòng mới.")
    if metadata["round"] != number or metadata["mode"] not in {"full", "demo"}:
        raise ValueError("Thông tin vòng QC không hợp lệ.")
    sample = read_csv(sample_path)
    sample_images = {row["image"] for row in sample}
    if not sample_images or len(sample_images) != len(sample) or not sample_images <= labels.images.keys():
        raise ValueError("Danh sách ảnh QC rỗng, trùng hoặc ngoài lô.")
    if metadata["mode"] == "full" and sample_images != labels.images.keys():
        raise ValueError("Vòng duyệt toàn bộ còn thiếu ảnh trong lô.")
    return tax, labels, metadata, sample


def parse_review(review, sample_images, objects):
    statuses = defaultdict(list)
    errors = []
    omitted = set()
    seen = set()
    for number, row in enumerate(review, 2):
        image, kind, obj_id, reviewer, rule, region, note = (
            (row.get(key) or "").strip() for key in
            ("image", "error_type", "object_id", "reviewer", "rule_id", "region", "note")
        )
        if not kind and not any((obj_id, reviewer, rule, region, note)):
            continue
        if image not in sample_images or kind not in VALID or not MEMBER_RE.fullmatch(reviewer):
            errors.append(f"Dòng {number}: ảnh, loại lỗi hoặc mã reviewer không hợp lệ.")
            continue
        if kind == "khong":
            if obj_id or rule or region:
                errors.append(f"Dòng {number}: ảnh sạch không cần ID box, luật hoặc vùng.")
                continue
        elif not rule or not note:
            errors.append(f"Dòng {number}: lỗi cần rule_id và ghi chú.")
            continue
        elif kind == "bo_sot":
            if obj_id or not region or (image, region) in omitted:
                errors.append(f"Dòng {number}: bỏ sót cần vùng riêng, để trống object_id.")
                continue
            omitted.add((image, region))
        elif obj_id not in objects[image]:
            errors.append(f"Dòng {number}: object_id {obj_id!r} không có trong ảnh {image}.")
            continue
        key = (image, obj_id, kind, region if kind == "bo_sot" else "")
        if key in seen:
            errors.append(f"Dòng {number}: kết quả duyệt trùng.")
            continue
        seen.add(key)
        statuses[image].append((kind, obj_id))
    for image, results in statuses.items():
        if len(results) > 1 and any(kind == "khong" for kind, _ in results):
            errors.append(f"{image}: vừa ghi sạch vừa ghi lỗi.")
    missing = sorted(sample_images - statuses.keys())
    if missing:
        errors.append("Chưa duyệt: " + ", ".join(missing))
    return statuses, omitted, errors


def fraction(count, total):
    return f"{count}/{total} = {count / total:.1%}" if total else f"{count}/0 (N/A)"


def make_report(directory, args):
    tax, labels, metadata, sample = checked_round(directory, args.round)
    review_path = directory / "qc_review.csv"
    objects = {image: {str(obj.id): obj.cls for obj in entries} for image, entries in labels.objects.items()}
    sample_images = {row["image"] for row in sample}
    review = read_csv(review_path)
    statuses, omitted, problems = parse_review(review, sample_images, objects)
    if metadata["mode"] == "demo":
        problems.append("Vòng lấy mẫu chỉ dùng để minh họa. Cần duyệt toàn bộ lô để bàn giao.")
    if args.guideline_gap or args.data_problem:
        problems.append(f"Guideline còn {args.guideline_gap} ca chưa chốt, {args.data_problem} ảnh có vấn đề.")
    if any(obj.attrs.get("can_review") == "true" for image in sample_images for obj in labels.objects[image]):
        problems.append("Nhãn cuối còn box đánh dấu can_review.")
    reviewed = len(statuses)
    bad_images = {image for image, entries in statuses.items() if any(kind != "khong" for kind, _ in entries)}
    bad_objects = {(image, obj_id) for image, entries in statuses.items() for kind, obj_id in entries
                   if kind not in {"khong", "bo_sot"} and objects[image][obj_id] != tax.ignore}
    types = Counter(kind for entries in statuses.values() for kind, _ in entries if kind != "khong")
    total_objects = sum(obj.cls != tax.ignore for image in statuses for obj in labels.objects[image])
    repeated = types and types.most_common(1)[0][1] >= 3 and types.most_common(1)[0][1] * 2 >= sum(types.values())
    over_limit = reviewed and len(bad_images) / reviewed > tax.rules["error_rate_img_max"]
    decision = "BLOCKED" if problems else "REWORK" if over_limit or repeated else "RELEASE"

    text = [
        f"## Vòng {args.round} — {metadata['mode']}",
        f"- Ảnh đã duyệt {reviewed}/{len(sample)}; cả lô {len(labels.images)} ảnh.",
        f"- Ảnh có lỗi trên ảnh đã duyệt: {fraction(len(bad_images), reviewed)}.",
        f"- Annotation đối tượng hiện có bị lỗi: {fraction(len(bad_objects), total_objects)}.",
        f"- Vật bỏ sót ghi riêng: {len(omitted)}.",
        "- IAA trước calibration dùng để chẩn đoán; đối chiếu iaa_summary.md.",
    ]
    for group in sorted({row["group"] for row in sample}):
        images = {row["image"] for row in sample if row["group"] == group}
        text.append(f"- {group}: đã duyệt {len(images & statuses.keys())}/{len(images)}, "
                    f"ảnh có lỗi {fraction(len(images & bad_images), len(images & statuses.keys()))}.")
    for kind, count in types.most_common(3):
        text.append(f"- {kind}: {count} lỗi.")
    if repeated:
        text.append("- Lỗi cùng loại lặp lại: xem lại guideline hoặc ranh giới áp dụng.")
    if over_limit:
        text.append(f"- Tỉ lệ ảnh có lỗi vượt ngưỡng lớp học {tax.rules['error_rate_img_max']:.0%}.")
    text.extend(f"- {problem}" for problem in problems)
    return decision, text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--round", type=int, default=1)
    parser.add_argument("--guideline-gap", type=int, default=0)
    parser.add_argument("--data-problem", type=int, default=0)
    args = parser.parse_args()
    if args.round < 1 or min(args.guideline_gap, args.data_problem) < 0:
        parser.error("Số vòng phải dương và số ca tồn đọng không âm.")
    directory = round_dir(args.round)
    output = directory / "qc_report_auto.md"
    current = True
    try:
        decision, summary = make_report(directory, args)
    except (OSError, ValueError, KeyError, TypeError, SystemExit) as exc:
        current = False
        decision = "BLOCKED"
        summary = [f"- Bằng chứng QC thiếu, sai hoặc đã thay đổi: {exc}."]
        if output.exists():
            summary.append("- Giữ báo cáo đã lưu của vòng cũ. Mở vòng mới cho lô hiện tại.")
    display_decision = {
        "BLOCKED": "CHƯA ĐỦ ĐIỀU KIỆN",
        "REWORK": "REWORK",
        "RELEASE": "RELEASE",
    }[decision]
    text = "\n".join(["# Báo cáo QC tự động", "", f"**{display_decision}**", "", *summary])
    print(text)
    if directory.is_dir() and (current or not output.exists()):
        output.write_text(text + "\n", encoding="utf-8")
        snapshot = directory / "labels_snapshot.json"
        review = directory / "qc_review.csv"
        result = {
            "round": args.round,
            "reviewer_inputs": {"guideline_gap": args.guideline_gap, "data_problem": args.data_problem},
            "decision": decision,
            "labels_sha256": digest(snapshot) if snapshot.is_file() else None,
            "review_sha256": digest(review) if review.is_file() else None,
        }
        (directory / "qc_result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
