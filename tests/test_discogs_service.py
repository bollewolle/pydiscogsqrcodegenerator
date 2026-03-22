import pytest
from unittest.mock import MagicMock, patch

from pydiscogstoqrfactory.discogs_service import DiscogsService


class TestNormalizeRelease:
    def setup_method(self):
        self.service = DiscogsService("key", "secret", "agent/1.0")

    def _make_item(self, release_id=1, title="Test", artists=None, year=2020, date_added=""):
        """Create a mock collection item."""
        item = MagicMock()
        release = MagicMock()
        release.id = release_id
        release.title = title
        release.year = year

        if artists is None:
            artist = MagicMock()
            artist.name = "Test Artist"
            release.artists = [artist]
        else:
            release.artists = artists

        item.release = release
        item.date_added = date_added
        return item

    def test_basic_normalization(self):
        item = self._make_item(release_id=123, title="Album", year=2023)
        result = self.service._normalize_release(item, "My Folder")

        assert result["id"] == 123
        assert result["title"] == "Album"
        assert result["year"] == 2023
        assert result["artist"] == "Test Artist"
        assert result["discogs_folder"] == "My Folder"
        assert result["url"] == "https://www.discogs.com/release/123"

    def test_multiple_artists(self):
        a1 = MagicMock()
        a1.name = "Artist One"
        a2 = MagicMock()
        a2.name = "Artist Two"
        item = self._make_item(artists=[a1, a2])
        result = self.service._normalize_release(item, "Folder")
        assert result["artist"] == "Artist One, Artist Two"

    def test_no_artists(self):
        item = self._make_item(artists=[])
        result = self.service._normalize_release(item, "Folder")
        assert result["artist"] == "Unknown Artist"

    def test_missing_year(self):
        item = self._make_item(year=None)
        result = self.service._normalize_release(item, "Folder")
        assert result["year"] == 0

    def test_date_added_preserved(self):
        item = self._make_item(date_added="2025-01-15T10:00:00-08:00")
        result = self.service._normalize_release(item, "Folder")
        assert result["date_added"] == "2025-01-15T10:00:00-08:00"


class TestFormatArtists:
    def test_single_artist(self):
        artist = MagicMock()
        artist.name = "SOHN"
        assert DiscogsService._format_artists([artist]) == "SOHN"

    def test_multiple_artists(self):
        a1, a2 = MagicMock(), MagicMock()
        a1.name = "A"
        a2.name = "B"
        assert DiscogsService._format_artists([a1, a2]) == "A, B"

    def test_empty_list(self):
        assert DiscogsService._format_artists([]) == "Unknown Artist"

    def test_none(self):
        assert DiscogsService._format_artists(None) == "Unknown Artist"

    def test_strips_disambiguation_number(self):
        artist = MagicMock()
        artist.name = "Adja (3)"
        assert DiscogsService._format_artists([artist]) == "Adja"

    def test_strips_disambiguation_multiple_artists(self):
        a1, a2 = MagicMock(), MagicMock()
        a1.name = "Nordmann (2)"
        a2.name = "Regular Artist"
        assert DiscogsService._format_artists([a1, a2]) == "Nordmann, Regular Artist"

    def test_preserves_non_disambiguation_parentheses(self):
        artist = MagicMock()
        artist.name = "Sunn O)))"
        assert DiscogsService._format_artists([artist]) == "Sunn O)))"

    def test_preserves_parentheses_with_text(self):
        artist = MagicMock()
        artist.name = "The Artist (UK)"
        assert DiscogsService._format_artists([artist]) == "The Artist (UK)"


class TestStripDisambiguation:
    def test_single_digit(self):
        assert DiscogsService._strip_disambiguation("Adja (3)") == "Adja"

    def test_multi_digit(self):
        assert DiscogsService._strip_disambiguation("Nordmann (12)") == "Nordmann"

    def test_no_suffix(self):
        assert DiscogsService._strip_disambiguation("SOHN") == "SOHN"

    def test_text_in_parentheses_preserved(self):
        assert DiscogsService._strip_disambiguation("The Artist (UK)") == "The Artist (UK)"

    def test_parentheses_not_at_end_preserved(self):
        assert DiscogsService._strip_disambiguation("Artist (2) Extra") == "Artist (2) Extra"

    def test_empty_string(self):
        assert DiscogsService._strip_disambiguation("") == ""


class TestFindFolder:
    def test_finds_folder_by_id(self):
        user = MagicMock()
        f0 = MagicMock()
        f0.id = 0
        f0.name = "All"
        f1 = MagicMock()
        f1.id = 1
        f1.name = "Uncategorized"
        f5 = MagicMock()
        f5.id = 5
        f5.name = "Vinyl"
        user.collection_folders = [f0, f1, f5]

        assert DiscogsService._find_folder(user, 0).name == "All"
        assert DiscogsService._find_folder(user, 5).name == "Vinyl"

    def test_raises_for_missing_folder(self):
        user = MagicMock()
        f0 = MagicMock()
        f0.id = 0
        user.collection_folders = [f0]

        with pytest.raises(ValueError, match="Folder with ID 99 not found"):
            DiscogsService._find_folder(user, 99)


class TestMapSortKey:
    def test_artist(self):
        assert DiscogsService._map_sort_key("artist") == "artist"

    def test_year(self):
        assert DiscogsService._map_sort_key("year") == "year"

    def test_date_added(self):
        assert DiscogsService._map_sort_key("date_added") == "added"

    def test_unknown_defaults_to_artist(self):
        assert DiscogsService._map_sort_key("unknown") == "artist"


class TestParseDateAdded:
    def test_valid_date_string(self):
        item = MagicMock()
        item.date_added = "2025-01-15T10:00:00-08:00"
        from datetime import date
        result = DiscogsService._parse_date_added(item)
        assert result == date(2025, 1, 15)

    def test_datetime_object(self):
        from datetime import date, datetime, timezone
        item = MagicMock()
        item.date_added = datetime(2025, 3, 10, 14, 30, 0, tzinfo=timezone.utc)
        result = DiscogsService._parse_date_added(item)
        assert result == date(2025, 3, 10)

    def test_date_object(self):
        from datetime import date
        item = MagicMock()
        item.date_added = date(2025, 6, 1)
        result = DiscogsService._parse_date_added(item)
        assert result == date(2025, 6, 1)

    def test_none_date(self):
        item = MagicMock()
        item.date_added = None
        assert DiscogsService._parse_date_added(item) is None

    def test_invalid_date(self):
        item = MagicMock()
        item.date_added = "not-a-date"
        assert DiscogsService._parse_date_added(item) is None
