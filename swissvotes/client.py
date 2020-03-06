import json
import requests

from .config import VOTES_METADATA_URL, LEVELS
from .parser import parse_metadata, parse_results


class Client:

    def __init__(self, datadir=None):
        self._datadir = datadir

    def available_votes(self, file=None):
        """Get available votes from the API. Optionally save JSON to file.

        Returns a dict of vote dates to vote URLs.
        """
        data = self._get_json(VOTES_METADATA_URL, file)
        return {d['coverage']: d['download_url']
                for d in data['result']['resources']}

    def get_vote_metadata(self, url, file=None):
        """Get vote metadata from its URL. Optionally save JSON to file.

        Returns list of dicts.
        """
        # Parse vote metadata.
        data = self._get_json(url, file)
        return parse_metadata(data, url)

    def get_results(self, url, level='municipality', file=None):
        """Get results of each items given a vote URL and for a given level.

        Returns a dicts whose keys are vote OGD id and whose values are lists
        of results.
        """
        if level not in LEVELS:
            raise ValueError(f'Level must be one of {LEVELS}')
        # Parse vote results.
        data = self._get_json(url, file)
        return parse_results(data, level)

    def _get_json(self, url, file=None):
        """Get JSON from a URL. Optionally save JSON to file."""
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
