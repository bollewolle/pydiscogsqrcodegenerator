import json

from pydiscogstoqrfactory.models import ProcessedRelease


class TestPreview:
    def test_preview_with_valid_data(self, client, sample_releases):
        response = client.post(
            "/export/preview",
            data={"releases_data": json.dumps(sample_releases)},
        )
        assert response.status_code == 200
        assert b"CSV Preview" in response.data
        assert b"SOHN" in response.data

    def test_preview_without_data_redirects(self, client):
        response = client.post("/export/preview", data={})
        assert response.status_code == 302

    def test_preview_with_invalid_json_redirects(self, client):
        response = client.post(
            "/export/preview",
            data={"releases_data": "not json"},
            follow_redirects=True,
        )
        assert b"Invalid release data" in response.data


class TestDownload:
    def test_download_from_session(self, client, sample_releases):
        # First preview to populate session
        client.post(
            "/export/preview",
            data={"releases_data": json.dumps(sample_releases)},
        )
        # Then download
        response = client.post("/export/download")
        assert response.status_code == 200
        assert response.content_type == "text/csv; charset=utf-8"
        assert "attachment" in response.headers.get("Content-Disposition", "")

    def test_download_with_rows_data(self, client, sample_releases):
        from pydiscogstoqrfactory.csv_service import CSVService
        from pydiscogstoqrfactory.config import TestConfig

        service = CSVService(TestConfig.CSV_TEMPLATE_PATH)
        rows = service.generate_rows(sample_releases)

        response = client.post(
            "/export/download",
            data={"rows_data": json.dumps(rows)},
        )
        assert response.status_code == 200
        assert response.content_type == "text/csv; charset=utf-8"

    def test_download_without_data_redirects(self, client):
        response = client.post("/export/download")
        assert response.status_code == 302


class TestMarkProcessed:
    def test_mark_processed(self, client, db, sample_releases):
        response = client.post(
            "/export/mark-processed",
            data={"releases_data": json.dumps(sample_releases)},
            follow_redirects=True,
        )
        assert b"Marked 3 release(s) as processed" in response.data

        # Verify in database
        count = ProcessedRelease.query.count()
        assert count == 3

    def test_mark_processed_skips_duplicates(self, client, db, sample_releases):
        # First mark
        client.post(
            "/export/mark-processed",
            data={"releases_data": json.dumps(sample_releases)},
        )
        # Second mark (same releases)
        response = client.post(
            "/export/mark-processed",
            data={"releases_data": json.dumps(sample_releases)},
            follow_redirects=True,
        )
        assert b"Marked 0 release(s) as processed" in response.data


class TestClearSession:
    def test_clear_session_preserves_auth(self, client):
        with client.session_transaction() as sess:
            sess["username"] = "testuser"
            sess["access_token"] = "token"
            sess["access_secret"] = "secret"
            sess["preview_rows"] = [{"some": "data"}]

        client.post("/export/clear-session")

        with client.session_transaction() as sess:
            assert sess.get("username") == "testuser"
            assert sess.get("access_token") == "token"
            assert "preview_rows" not in sess
