"""
Unit tests for Dataset Manifest and SHA-256 integrity verification.
"""

import os
import tempfile
import pytest

from ml.data.manifests.manifest import DatasetManifest, generate_manifest_for_file


def test_manifest_generation_and_integrity():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "sample.dat")
        with open(test_file, "w") as f:
            f.write("CycloneGuard Scientific Dataset Payload 2026")

        manifest = generate_manifest_for_file(
            source_id="noaa_ibtracs",
            dataset_name="Test Manifest Dataset",
            version="v01",
            file_path=test_file,
            record_count=1,
        )

        assert manifest.file_size_bytes == os.path.getsize(test_file)
        assert len(manifest.checksum_sha256) == 64
        assert manifest.verify_integrity() is True

        manifest_file = os.path.join(tmpdir, "sample.manifest.json")
        saved_path = manifest.save(manifest_file)
        assert os.path.exists(saved_path)

        loaded_manifest = DatasetManifest.load(saved_path)
        assert loaded_manifest.checksum_sha256 == manifest.checksum_sha256
        assert loaded_manifest.verify_integrity() is True

        # Tamper with file
        with open(test_file, "a") as f:
            f.write(" - Tampered Bytes!")
        assert loaded_manifest.verify_integrity() is False
