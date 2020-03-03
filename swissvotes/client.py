import json
import requests

from .config import VOTES_METADATA_URL
from .parser import parse_url, parse_metadata


class Client:

    def __init__(self, datadir=None):
        self._datadir = datadir

    def available_dates(self):
        """Get available vote dates from the API.

        Returns list of dates in YYYY-MM-DD format.
        """
        data = self._get_json(VOTES_METADATA_URL)
        dates = [d['coverage'] for d in data['result']['resources']]
        return list(sorted(dates))

    def get_vote_metadata(self, date):
        """Get vote metadata for a given vote date (in format YYYY-MM-DD).

        Returns list of dicts.
        """
        # Find URL of given date.
        data = self._get_json(VOTES_METADATA_URL)
        url = parse_url(data, date)
        # Raise error if URL is not found.
        if url is None:
            raise ValueError(f'Date {date} is not a valid vote date')
        # Parse vote metadata.
        data = self._get_json(url)
        return parse_metadata(data)

    def _get_json(self, url, file=None):
        """Get JSON from a URL. Optionally save the data on disk."""
        r = requests.get(url)
        # If status is not OK, raise error.
        if not r.ok:
            r.raise_for_status()
        # Otherwise load JSON.
        data = json.loads(r.text)
        # Optionally save JSON to disk.
        if file is not None:
            with open(file, 'w') as f:
                json.dump(data, f)
        return data
