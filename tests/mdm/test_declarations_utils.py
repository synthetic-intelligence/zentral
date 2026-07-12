import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from django.test import TestCase

from zentral.contrib.mdm.declarations import (
    artifact_pk_from_identifier_and_model,
    get_artifact_identifier,
    get_artifact_version_server_token,
)
from zentral.contrib.mdm.declarations.status_report import get_status_report_target_artifacts_info
from zentral.contrib.mdm.models import Artifact, Declaration, TargetArtifact
from zentral.utils.payloads import get_payload_identifier


class MDMDeclarationUtilsTestCase(TestCase):
    def test_get_artifact_identifier_not_a_declaration(self):
        with self.assertRaises(ValueError) as cm:
            get_artifact_identifier({"type": Artifact.Type.ENTERPRISE_APP})
        self.assertEqual(cm.exception.args[0], "Artifact is not a declaration")

    def test_artifact_pk_from_identifier_and_model_unknown_path(self):
        with self.assertRaises(ValueError) as cm:
            artifact_pk_from_identifier_and_model("zentral.yolo.00000000-0000-0000-0000-000000000000", Declaration)
        self.assertEqual(cm.exception.args[0], "Unknown artifact identifier path")

    def test_artifact_pk_from_identifier_and_model_invalid_model(self):
        with self.assertRaises(ValueError) as cm:
            artifact_pk_from_identifier_and_model("zentral.data-asset.00000000-0000-0000-0000-000000000000",
                                                  Declaration)
        self.assertEqual(cm.exception.args[0], "Invalid artifact identifier model")

    def test_get_artifact_version_server_token_reinstall_major(self):
        target = Mock()
        target.comparable_os_version = (15, 2, 1)
        av_pk = str(uuid.uuid4())
        server_token = get_artifact_version_server_token(
            target,
            {"reinstall_on_os_update": str(Artifact.ReinstallOnOSUpdate.MAJOR),
             "reinstall_interval": 0},
            {"pk": av_pk},
            0
        )
        self.assertEqual(server_token, f"{av_pk}.ov-15")

    def test_get_artifact_version_server_token_reinstall_minor_one_retry_count(self):
        target = Mock()
        target.comparable_os_version = (15, 2, 1)
        av_pk = str(uuid.uuid4())
        server_token = get_artifact_version_server_token(
            target,
            {"reinstall_on_os_update": str(Artifact.ReinstallOnOSUpdate.MINOR),
             "reinstall_interval": 0},
            {"pk": av_pk},
            1
        )
        self.assertEqual(server_token, f"{av_pk}.ov-15.2.rc-1")

    def test_get_artifact_version_server_token_reinstall_patch(self):
        target = Mock()
        target.comparable_os_version = (15, 2, 1)
        av_pk = str(uuid.uuid4())
        server_token = get_artifact_version_server_token(
            target,
            {"reinstall_on_os_update": str(Artifact.ReinstallOnOSUpdate.PATCH),
             "reinstall_interval": 0},
            {"pk": av_pk},
            0
        )
        self.assertEqual(server_token, f"{av_pk}.ov-15.2.1")

    @patch("zentral.contrib.mdm.declarations.utils.naive_utcnow")
    def test_get_artifact_version_server_token_reinstall_interval(self, patched_naive_utcnow):
        now = datetime(2025, 1, 1, 0, 0, 0)
        patched_naive_utcnow.return_value = now
        target = Mock()
        target.comparable_os_version = (15, 2, 1)
        target.target.created_at = now - timedelta(days=91)
        av_pk = str(uuid.uuid4())
        server_token = get_artifact_version_server_token(
            target,
            {"reinstall_on_os_update": str(Artifact.ReinstallOnOSUpdate.NO),
             "reinstall_interval": 90},
            {"pk": av_pk},
            0
        )
        self.assertEqual(server_token, f"{av_pk}.ri-1")


class MDMStatusReportTargetArtifactsInfoTestCase(TestCase):
    @staticmethod
    def _report(items):
        return {"StatusItems": {"management": {"declarations": {
            "activations": [], "assets": [], "configurations": items, "management": [],
        }}}}

    @staticmethod
    def _item(artifact_pk, server_token, active, valid):
        return {"identifier": get_payload_identifier("declaration", str(artifact_pk)),
                "server-token": server_token, "active": active, "valid": valid}

    def test_dedup_same_version_keeps_most_present(self):
        # same artifact version reported under two server-tokens (a re-push) -> one entry
        artifact_pk, av_pk = uuid.uuid4(), uuid.uuid4()
        report = self._report([
            self._item(artifact_pk, str(av_pk), True, "unknown"),     # AwaitingConfirmation
            self._item(artifact_pk, f"{av_pk}.rc-1", True, "valid"),  # Installed
        ])
        with self.assertLogs("zentral.contrib.mdm.declarations.status_report", level="WARNING") as cm:
            info = get_status_report_target_artifacts_info(report)
        self.assertEqual(len(info), 1)
        self.assertEqual(info[0][1], str(av_pk))
        self.assertEqual(info[0][2], TargetArtifact.Status.INSTALLED)
        self.assertTrue(any(f"Duplicate artifact version {av_pk}" in m
                            and f"server tokens {av_pk} and {av_pk}.rc-1" in m for m in cm.output))

    def test_dedup_most_present_is_order_independent(self):
        artifact_pk, av_pk = uuid.uuid4(), uuid.uuid4()
        info = get_status_report_target_artifacts_info(self._report([
            self._item(artifact_pk, str(av_pk), True, "valid"),        # Installed
            self._item(artifact_pk, f"{av_pk}.rc-1", True, "unknown"),  # AwaitingConfirmation
        ]))
        self.assertEqual(len(info), 1)
        self.assertEqual(info[0][2], TargetArtifact.Status.INSTALLED)

    def test_dedup_three_occurrences_keeps_most_present(self):
        # same version reported 3x, most present (Installed) in the middle -> one entry, most present
        artifact_pk, av_pk = uuid.uuid4(), uuid.uuid4()
        with self.assertLogs("zentral.contrib.mdm.declarations.status_report", level="WARNING") as cm:
            info = get_status_report_target_artifacts_info(self._report([
                self._item(artifact_pk, str(av_pk), False, "unknown"),      # Uninstalled
                self._item(artifact_pk, f"{av_pk}.rc-1", True, "valid"),    # Installed
                self._item(artifact_pk, f"{av_pk}.rc-2", True, "unknown"),  # AwaitingConfirmation
            ]))
        self.assertEqual(len(info), 1)
        self.assertEqual(info[0][1], str(av_pk))
        self.assertEqual(info[0][2], TargetArtifact.Status.INSTALLED)
        self.assertEqual(len(cm.output), 2)  # one warning per duplicate after the first

    def test_distinct_versions_not_deduped(self):
        artifact_pk = uuid.uuid4()
        info = get_status_report_target_artifacts_info(self._report([
            self._item(artifact_pk, str(uuid.uuid4()), True, "valid"),
            self._item(artifact_pk, str(uuid.uuid4()), True, "valid"),
        ]))
        self.assertEqual(len(info), 2)

    def test_status_presence_rank_ordering(self):
        Status = TargetArtifact.Status
        self.assertGreater(Status.INSTALLED.presence_rank, Status.AWAITING_CONFIRMATION.presence_rank)
        self.assertGreater(Status.AWAITING_CONFIRMATION.presence_rank, Status.UNINSTALLED.presence_rank)
        self.assertGreater(Status.UNINSTALLED.presence_rank, Status.FAILED.presence_rank)
        # every present status outranks every non-present one
        self.assertGreater(min(s.presence_rank for s in Status if s.present),
                           max(s.presence_rank for s in Status if not s.present))
