import re
from datetime import date

import discogs_client


class DiscogsService:
    """Wrapper around the python3-discogs-client library."""

    def __init__(self, consumer_key: str, consumer_secret: str, user_agent: str):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.user_agent = user_agent
        self.client = discogs_client.Client(user_agent)
        self._identity = None

    def get_authorize_url(self, callback_url: str) -> tuple[str, str, str]:
        """Start OAuth flow. Returns (request_token, request_secret, authorize_url)."""
        self.client.set_consumer_key(self.consumer_key, self.consumer_secret)
        request_token, request_secret, authorize_url = (
            self.client.get_authorize_url(callback_url=callback_url)
        )
        return request_token, request_secret, authorize_url

    def get_access_token(
        self, request_token: str, request_secret: str, verifier: str
    ) -> tuple[str, str]:
        """Exchange verifier for access tokens. Returns (access_token, access_secret)."""
        self.client.set_consumer_key(self.consumer_key, self.consumer_secret)
        self.client.set_token(request_token, request_secret)
        access_token, access_secret = self.client.get_access_token(verifier)
        return access_token, access_secret

    def authenticate(self, access_token: str, access_secret: str) -> None:
        """Authenticate with existing tokens."""
        self.client.set_consumer_key(self.consumer_key, self.consumer_secret)
        self.client.set_token(access_token, access_secret)

    def get_identity(self) -> dict:
        """Get the authenticated user's identity."""
        if self._identity is None:
            identity = self.client.identity()
            self._identity = {
                "username": identity.username,
                "id": identity.id,
            }
        return self._identity

    def get_folders(self, username: str) -> list[dict]:
        """Get all collection folders for a user."""
        user = self.client.user(username)
        folders = []
        for folder in user.collection_folders:
            folders.append(
                {
                    "id": folder.id,
                    "name": folder.name,
                    "count": folder.count,
                }
            )
        return folders

    def get_folder_releases(
        self,
        username: str,
        folder_id: int,
        sort: str = "artist",
        order: str = "asc",
    ) -> list[dict]:
        """Get all releases in a folder, normalized."""
        user = self.client.user(username)
        folder = self._find_folder(user, folder_id)
        folder_name = folder.name

        releases = []
        sort_key = self._map_sort_key(sort)
        sort_order = "desc" if order == "desc" else "asc"

        for item in folder.releases.sort(sort_key, sort_order):
            releases.append(self._normalize_release(item, folder_name))

        return releases

    def get_releases_since(
        self, username: str, since_date: date
    ) -> list[dict]:
        """Get releases added to collection since a given date (across all folders)."""
        user = self.client.user(username)
        all_folder = self._find_folder(user, 0)  # Folder 0 = "All"

        releases = []
        for item in all_folder.releases.sort("added", "desc"):
            date_added = self._parse_date_added(item)
            if date_added and date_added < since_date:
                break
            release_data = self._normalize_release(item, self._get_item_folder_name(item))
            releases.append(release_data)

        return releases

    def _normalize_release(self, item, folder_name: str) -> dict:
        """Normalize a collection item into a flat dict."""
        release = item.release
        artist = self._format_artists(release.artists)
        date_added = getattr(item, "date_added", "")
        if hasattr(date_added, "isoformat"):
            date_added = date_added.isoformat()
        return {
            "id": release.id,
            "artist": artist,
            "title": release.title,
            "year": release.year or 0,
            "discogs_folder": folder_name,
            "url": f"https://www.discogs.com/release/{release.id}",
            "date_added": str(date_added) if date_added else "",
        }

    @staticmethod
    def _find_folder(user, folder_id: int):
        """Find a collection folder by its ID (not list index)."""
        for folder in user.collection_folders:
            if folder.id == folder_id:
                return folder
        raise ValueError(f"Folder with ID {folder_id} not found")

    @staticmethod
    def _format_artists(artists) -> str:
        """Join multiple artists into a single string."""
        if not artists:
            return "Unknown Artist"
        return ", ".join(
            DiscogsService._strip_disambiguation(a.name) for a in artists
        )

    @staticmethod
    def _strip_disambiguation(name: str) -> str:
        """Remove Discogs disambiguation suffix like ' (2)' or ' (13)' from artist names."""
        return re.sub(r"\s+\(\d+\)$", "", name)

    @staticmethod
    def _map_sort_key(sort: str) -> str:
        """Map our sort names to Discogs API sort keys."""
        mapping = {
            "artist": "artist",
            "year": "year",
            "date_added": "added",
        }
        return mapping.get(sort, "artist")

    @staticmethod
    def _parse_date_added(item) -> date | None:
        """Parse the date_added field from a collection item."""
        from datetime import datetime

        date_val = getattr(item, "date_added", None)
        if not date_val:
            return None
        # Handle datetime objects directly
        if isinstance(date_val, datetime):
            return date_val.date()
        if isinstance(date_val, date):
            return date_val
        # Handle string format
        try:
            return date.fromisoformat(str(date_val)[:10])
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _get_item_folder_name(item) -> str:
        """Get folder name from a collection item, with fallback."""
        folder = getattr(item, "folder", None)
        if folder:
            return getattr(folder, "name", "Unknown Folder")
        return "All"
