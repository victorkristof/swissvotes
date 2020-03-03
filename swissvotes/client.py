import json
import requests

from .config import VOTES_METADATA_URL, LEVELS
from .parser import parse_url, parse_metadata, parse_results


class Client:

    def __init__(self, datadir=None):
        self._datadir = datadir

    def available_dates(self):
        """Get available vote dates from the API.

        Returns a list of dates in YYYY-MM-DD format.
        """
        data = self._get_json(VOTES_METADATA_URL)
        dates = [d['coverage'] for d in data['result']['resources']]
        return list(sorted(dates))

    def get_vote_metadata(self, date=None, url=None):
        """Get vote metadata for a given vote date (in format YYYY-MM-DD).

        You need to give either a date or a URL. If both are given, it will use
        the URL.

        Returns list of dicts.
        """
        if date is None and url is None:
            raise ValueError('You need to give either a date or a URL.')
        # If URL is not given, find it using the date.
        if url is None:
            url = self._get_url(date)
        # Parse vote metadata.
        data = self._get_json(url)
        return parse_metadata(data, url)

    def get_results(self, date=None, url=None, level='municipality'):
        """Get results of each vote on a vote date for a given level.

        You need to give either a date or a URL. If both are given, it will use
        the URL.

        Returns a dicts whose keys are vote OGD id and whose values are lists
        of results.
        """
        if date is None and url is None:
            raise ValueError('You need to give either a date or a URL.')
        if level not in LEVELS:
            raise ValueError(f'Level must be one of {LEVELS}')
        # If URL is not given, find it using the date.
        if url is None:
            url = self._get_url(date)
        # Parse vote results.
        data = self._get_json(url)
        return parse_results(data, level)

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

    def _get_url(self, date):
        """Find URL of given date."""
        data = self._get_json(VOTES_METADATA_URL)
        url = parse_url(data, date)
        # Raise error if URL is not found.
        if url is None:
            raise ValueError(f'Date {date} is not a valid vote date')
        return url
