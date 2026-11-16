import csv
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


SOURCE = Path(__file__).resolve().parents[1]


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        for name in ("scripts", "schemas"):
            if (SOURCE / name).exists():
                shutil.copytree(SOURCE / name, self.root / name)
        self.sub = self.root / "submission"
        self.qc = self.sub / "qc"
        self.qc.mkdir(parents=True)
        (self.sub / "labels").mkdir()
        (self.sub / "guidelines").mkdir()
        for name in ("guideline_v1.0_agreed.md", "guideline_v1.1_calibrated.md"):
            (self.sub / "guidelines" / name).write_text("R-01", encoding="utf-8")
        self.write_json(self.sub / "guideline_change.json", {"kind": "editorial", "summary": "R-01 giữ nguyên"})
        self.tax = self.sub / "taxonomy.json"
        shutil.copyfile(SOURCE / "submission" / "taxonomy.json", self.tax)
        self.images = self.root / "data" / "images"
        self.images.mkdir(parents=True)
        self.names = ["img_001.jpg", "img_002.jpg"]
        for image in self.names:
            Image.new("RGB", (100, 100)).save(self.images / image)
        self.write_csv(self.root / "data" / "ATTRIBUTION.csv", ["file", "author", "license", "source_url"],
                       [[name, "Fixture", "CC0", "https://example.com/" + name] for name in self.names])

    def run_script(self, name, *args, success=True):
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts" / (name + ".py")), *args],
            cwd=self.root, capture_output=True, text=True, encoding="utf-8",
        )
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode == 0, success, output)
        return output

    def write_json(self, path, data):
        path.write_text(json.dumps(data), encoding="utf-8")

    def write_csv(self, path, header, rows):
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows(rows)

    def coco(self, path, names=None, label="car", additional=None, bbox=None):
        names = self.names if names is None else names
        data = {
            "images": [{"id": i, "file_name": name, "height": 100, "width": 100}
                       for i, name in enumerate(names, 1)],
            "categories": [{"id": 1, "name": label}, {"id": 2, "name": "ignore_region"}],
            "annotations": [
                {"id": i, "image_id": i, "category_id": 1, "bbox": bbox or [1, 1, 20, 60],
                 "attributes": {"occluded_level": "0", "truncated": "no", "can_review": False}}
                for i in range(1, len(names) + 1)
            ],
        }
        data["annotations"].extend(additional or [])
        self.write_json(path, data)

    def assignments(self, members="101|102"):
        self.write_csv(self.qc / "assignment.csv", ["image", "annotators", "n_annotators"],
                       [[name, members, len(members.split("|"))] for name in self.names])

    def compare(self):
        self.assignments()
        for member in ("101", "102"):
            self.coco(self.sub / "labels" / f"{member}.json")
        self.run_script("qc_compare")

    def test_make_cvat_labels_emits_valid_rectangle_and_checkbox_fields(self):
        self.run_script("make_cvat_labels")
        labels = json.loads((self.root / "cvat" / "labels_generated.json").read_text(encoding="utf-8"))
        self.assertTrue(all(label["type"] == "rectangle" for label in labels))
        for label in labels:
            if label["name"] == "ignore_region":
                self.assertEqual(label["attributes"], [])
                continue
            attributes = {attribute["name"]: attribute for attribute in label["attributes"]}
            self.assertEqual(set(attributes), {"occluded_level", "truncated", "can_review"})
            self.assertEqual(attributes["can_review"]["values"], ["true", "false"])

    def clean_lot(self):
        self.compare()
        self.run_script("build_final")

    def review(self, round_number=1, errors=None):
        review = self.qc / "reviews" / f"round-{round_number:02d}" / "qc_review.csv"
        rows = [[name, "", "khong", "103", "", "", ""] for name in self.names]
        if errors:
            rows = [rows[1], *errors]
        self.write_csv(review, ["image", "object_id", "error_type", "reviewer", "rule_id", "region", "note"], rows)

    def test_compare_rejects_missing_assigned_image_and_annotator(self):
        self.assignments("101|102|103")
        for member in ("101", "102"):
            self.coco(self.sub / "labels" / f"{member}.json", names=self.names[:1])
        output = self.run_script("qc_compare", success=False)
        self.assertIn("103", output)
        self.assertIn("img_002.jpg", output)
        self.assertFalse((self.qc / "iaa_summary.json").exists())

    def test_ignore_disagreement_is_actionable(self):
        self.assignments()
        self.coco(self.sub / "labels" / "101.json", additional=[
            {"id": 3, "image_id": 1, "category_id": 1, "bbox": [50, 0, 20, 60],
             "attributes": {"occluded_level": "0", "truncated": "no", "can_review": False}},
        ])
        self.coco(self.sub / "labels" / "102.json", additional=[
            {"id": 3, "image_id": 1, "category_id": 2, "bbox": [45, 0, 45, 80]},
        ])
        self.run_script("qc_compare")
        summary = json.loads((self.qc / "iaa_summary.json").read_text())
        self.assertEqual(summary["overall"]["n_skipped_in_ignore"], 0)
        self.assertIn("bat_dong_ignore", summary["issues_by_type"])
        self.assertEqual((self.qc / "flagged_images.txt").read_text().splitlines(), self.names[:1])

    def test_matched_ignore_regions_do_not_hide_asymmetric_coverage(self):
        self.assignments()
        obj = {"id": 3, "image_id": 1, "category_id": 1, "bbox": [25, 35, 10, 20],
               "attributes": {"occluded_level": "0", "truncated": "no", "can_review": False}}
        region = {"id": 4, "image_id": 1, "category_id": 2, "bbox": [28, 15, 65, 75]}
        self.coco(self.sub / "labels" / "101.json", additional=[
            obj, {**region, "bbox": [38, 15, 60, 75]},
        ])
        self.coco(self.sub / "labels" / "102.json", additional=[region])
        self.run_script("qc_compare")
        summary = json.loads((self.qc / "iaa_summary.json").read_text())
        self.assertEqual(summary["overall"]["n_skipped_in_ignore"], 0)
        self.assertEqual(summary["overall"]["n_unmatched_a"], 1)
        self.assertIn("bat_dong_ignore", summary["issues_by_type"])
        self.assertEqual((self.qc / "flagged_images.txt").read_text().splitlines(), self.names[:1])
        draft = json.loads((self.qc / "consensus_draft.json").read_text())
        self.assertIn(obj["bbox"], [box["bbox"] for box in draft["annotations"]])

    def test_review_rejects_changed_calibration_snapshot(self):
        self.clean_lot()
        self.run_script("qc_sample")
        self.review()
        snapshot = self.qc / "reviews" / "round-01" / "calibration_decisions_snapshot.csv"
        snapshot.write_text("invalid\n")
        self.assertIn("**HOLD**", self.run_script("qc_report"))

    def test_build_rejects_final_output_as_corrected_input(self):
        self.clean_lot()
        self.write_json(self.sub / "guideline_change.json", {"kind": "semantic", "summary": "R-01 đổi box"})
        decision = ["Q01", self.names[0], "Rà cả lô", "R-01", "v1.1", "103", "CVAT #2", "đã xác nhận", "lo"]
        self.write_csv(self.qc / "calibration_decisions.csv", self.decision_fields(), [decision])
        labels = self.qc / "labels_calibrated.json"
        old_labels = labels.read_bytes()
        self.run_script("build_final", "--calibrated", str(labels), success=False)
        self.assertEqual(labels.read_bytes(), old_labels)

    def test_calibration_cannot_drop_legacy_class(self):
        self.compare()
        new_schema = json.loads(self.tax.read_text())
        new_schema["version"] = "v1.1"
        new_schema["classes"][0]["name"] = "passenger_car"
        self.write_json(self.sub / "taxonomy_v1.1.json", new_schema)
        self.run_script("build_final", success=False)
        self.assertFalse((self.qc / "labels_calibrated.json").exists())

    def test_zero_candidates_supports_handoff_and_unreviewed_is_hold(self):
        self.clean_lot()
        self.assertTrue((self.qc / "calibration_decisions.csv").exists())
        self.run_script("qc_sample")
        self.assertIn("**HOLD**", self.run_script("qc_report"))
        self.review()
        self.assertIn("**RELEASE**", self.run_script("qc_report"))
        (self.qc / "iaa_summary.json").unlink()
        self.assertIn("**HOLD**", self.run_script("qc_report"))

    def test_omissions_are_counted_separately_and_review_rounds_preserved(self):
        self.clean_lot()
        self.run_script("qc_sample")
        self.review(errors=[
            [self.names[0], "", "bo_sot", "103", "R-01", "trái", "vật A"],
            [self.names[0], "", "bo_sot", "103", "R-01", "phải", "vật B"],
            [self.names[0], "", "bo_sot", "103", "R-01", "giữa", "vật C"],
        ])
        output = self.run_script("qc_report")
        self.assertIn("**REWORK**", output)
        self.assertIn("0/2 = 0.0%", output)
        self.assertNotIn("150.0%", output)
        first_review = self.qc / "reviews" / "round-01" / "qc_review.csv"
        artifact = first_review.read_bytes()
        self.run_script("qc_sample", "--round", "2")
        self.assertEqual(first_review.read_bytes(), artifact)

    def test_semantic_guideline_change_requires_all_images(self):
        self.compare()
        self.write_json(self.sub / "guideline_change.json", {"kind": "semantic", "summary": "R-01 đổi phạm vi box"})
        self.run_script("build_final", success=False)
        decision = ["Q01", self.names[0], "Rà cả lô", "R-01", "v1.1", "103", "CVAT #2", "đã xác nhận", "lo"]
        self.write_csv(self.qc / "calibration_decisions.csv", self.decision_fields(), [decision])
        target = self.prepare_export()
        self.coco(target, names=self.names[:1])
        self.run_script("build_final", success=False)
        self.coco(target)
        self.run_script("build_final")

    def prepare_export(self):
        output = self.run_script("prepare_calibration")
        prefix = "COCO sau sửa: "
        return self.root / next(line[len(prefix):] for line in output.splitlines() if line.startswith(prefix))

    def decision_fields(self):
        return ["case_id", "image", "quyet_dinh", "quy_tac_ghi_vao_guideline", "phien_ban_guideline",
                "nguoi_chot", "phieu_sua", "kiem_lai", "pham_vi"]

    def test_unflagged_qc_correction_rebuilds_both_formats(self):
        self.clean_lot()
        self.run_script("qc_sample")
        self.review(errors=[[self.names[0], "", "bo_sot", "103", "R-01", "trái", "vật A"]])
        self.assertIn("**REWORK**", self.run_script("qc_report"))
        first = self.qc / "reviews" / "round-01"
        original_result = (first / "qc_result.json").read_bytes()
        decision = ["Q01", self.names[0], "Thêm box", "R-01", "v1.1", "103", "vòng 1", "đã xác nhận", "anh"]
        self.write_csv(self.qc / "calibration_decisions.csv", self.decision_fields(), [decision])
        self.coco(self.prepare_export(), names=self.names[:1], bbox=[2, 1, 20, 60])
        self.run_script("build_final")
        final = json.loads((self.qc / "labels_calibrated.json").read_text())
        self.assertEqual(final["annotations"][0]["bbox"][0], 2)
        self.assertIn("2.0,1.0,20.0,60.0", (self.qc / "labels_calibrated.csv").read_text())
        self.assertIn("**HOLD**", self.run_script("qc_report"))
        self.assertEqual((first / "qc_result.json").read_bytes(), original_result)
        self.run_script("qc_sample", "--round", "2")
        self.review(round_number=2)
        self.assertIn("**RELEASE**", self.run_script("qc_report", "--round", "2"))

    def test_assignment_rejects_unsafe_member_and_symlink_destination(self):
        self.run_script("split_assign", "--members", "../data,102", "--copy-images", success=False)
        output = self.root / "work"
        output.mkdir()
        (output / "101").symlink_to(self.root / "data", target_is_directory=True)
        self.run_script("split_assign", "--members", "101,102", "--copy-images", success=False)
        self.assertEqual(sorted(path.name for path in self.images.iterdir()), self.names)

    def test_full_cli_handoff_checks_final_decision_and_rejects_tampering(self):
        (self.root / "guideline").mkdir()
        (self.root / "guideline" / "guideline_v0_starter.md").write_text("v0", encoding="utf-8")
        (self.root / "TEAM.md").write_text("101, 102", encoding="utf-8")
        (self.sub / "guidelines" / "individual").mkdir()
        (self.sub / "individual_notes").mkdir()
        self.run_script("split_assign", "--members", "101,102", "--copy-images")
        self.run_script("make_cvat_labels")
        for member in ("101", "102"):
            self.coco(self.sub / "labels" / f"{member}.json")
            (self.sub / "guidelines" / "individual" / f"guideline_{member}.md").write_text("R-01", encoding="utf-8")
            (self.sub / "individual_notes" / f"{member}.md").write_text("R-01", encoding="utf-8")
        self.run_script("validate_labels", "--all")
        self.run_script("qc_compare")
        self.run_script("viz_disagreement", "--images", "flagged")
        self.run_script("build_final")
        self.run_script("qc_sample")
        self.review()
        self.assertIn("**RELEASE**", self.run_script("qc_report"))
        report = self.qc / "QC_REPORT.md"
        report.write_text("- Vòng QC: 1\n- Quyết định: Release\n", encoding="utf-8")
        self.run_script("check_submission", success=False)
        template = (SOURCE / "docs" / "QC_REPORT_TEMPLATE.md").read_text(encoding="utf-8")
        complete = re.sub(r"<<[^>]*>>", "Bằng chứng thử nghiệm", template.replace(
            "<<số nguyên, ví dụ 1>>", "1").replace("<<Release hoặc Hold hoặc Rework>>", "Release"))
        report.write_text(complete, encoding="utf-8")
        self.run_script("check_submission")
        report.write_text(complete.replace("- Quyết định: Release", "- Quyết định: Hold"), encoding="utf-8")
        self.run_script("check_submission", success=False)

    def test_revised_decision_rejects_previous_export_for_same_scope(self):
        self.clean_lot()
        decision = ["Q01", self.names[0], "x=2", "R-01", "v1.1", "103", "CVAT #2", "đã xác nhận", "anh"]
        table = self.qc / "calibration_decisions.csv"
        self.write_csv(table, self.decision_fields(), [decision])
        old = self.prepare_export()
        self.coco(old, names=self.names[:1], bbox=[2, 1, 20, 60])
        self.run_script("build_final")
        decision[2] = "x=10"
        self.write_csv(table, self.decision_fields(), [decision])
        current = self.prepare_export()
        self.assertNotEqual(old, current)
        self.run_script("build_final", success=False)
        self.run_script("build_final", "--calibrated", str(old), success=False)
        current.write_bytes(old.read_bytes())
        self.run_script("build_final")
        (self.sub / "guidelines" / "guideline_v1.1_calibrated.md").write_text("R-01 updated", encoding="utf-8")
        self.assertNotEqual(current, self.prepare_export())
        self.run_script("build_final", success=False)

    def test_qc_rejects_corrupt_image_without_leaving_round(self):
        self.clean_lot()
        image = self.images / self.names[0]
        original = image.read_bytes()
        image.write_bytes(original[:-25])
        self.run_script("qc_compare", success=False)
        self.run_script("qc_sample", success=False)
        self.assertFalse((self.qc / "reviews" / "round-01").exists())
        image.write_bytes(original)
        self.run_script("qc_sample")
        self.assertTrue((self.qc / "reviews" / "round-01" / "review_manifest.json").exists())

    def test_qc_overlay_failure_can_retry_same_round(self):
        self.clean_lot()
        blocked = self.root / "work" / "review" / "round-01"
        blocked.mkdir(parents=True)
        overlay = blocked / f"{self.names[0]}.png"
        overlay.mkdir()
        self.run_script("qc_sample", success=False)
        self.assertFalse((self.qc / "reviews" / "round-01").exists())
        overlay.rmdir()
        self.run_script("qc_sample")
        self.assertTrue(overlay.is_file())

    def test_changed_iaa_cannot_reuse_old_calibration_decisions(self):
        self.compare()
        self.run_script("build_final")
        for member in ("101", "102"):
            self.coco(self.sub / "labels" / f"{member}.json", bbox=[4, 1, 20, 60])
        self.run_script("qc_compare")
        self.run_script("build_final", success=False)

    def test_sample_demo_cannot_release(self):
        self.clean_lot()
        self.run_script("qc_sample", "--n", "2")
        self.review()
        self.assertIn("**HOLD**", self.run_script("qc_report"))

    def test_schema_rejects_invalid_default_and_changed_threshold(self):
        data = json.loads(self.tax.read_text())
        old_default = data["attributes"][0]["default"]
        data["attributes"][0]["default"] = "invalid"
        self.write_json(self.tax, data)
        self.run_script("make_cvat_labels", success=False)
        data["attributes"][0]["default"] = old_default
        data["rules"]["error_rate_img_max"] = 0.50
        self.write_json(self.tax, data)
        self.run_script("make_cvat_labels", success=False)

    def test_empty_images_are_valid_with_no_box_agreement_value(self):
        self.assignments()
        for member in ("101", "102"):
            path = self.sub / "labels" / f"{member}.json"
            self.coco(path)
            data = json.loads(path.read_text())
            data["annotations"] = []
            self.write_json(path, data)
        self.run_script("qc_compare")
        iaa = json.loads((self.qc / "iaa_summary.json").read_text())
        self.assertIsNone(iaa["overall"]["pass"])
        self.assertEqual(iaa["coverage"], {"completed": 4, "assigned": 4})

    def test_review_is_bound_to_the_final_labels(self):
        self.clean_lot()
        self.run_script("qc_sample")
        self.review()
        labels = self.qc / "labels_calibrated.json"
        data = json.loads(labels.read_text())
        data["annotations"][0]["bbox"][0] += 1
        self.write_json(labels, data)
        self.assertIn("**HOLD**", self.run_script("qc_report"))
        self.run_script("qc_sample", success=False)


if __name__ == "__main__":
    unittest.main()
