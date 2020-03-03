import json
import os
import requests

from datetime import datetime as dt


class Client:

    def __init__(self, datadir=None):
        self._base = 'https://opendata.swiss/'
        self._datadir = None

    def available_dates(self):
        """Get available vote dates from the API."""
        url = self._base
        data = self._get_json(url)

    def _get_json(self, url, datadir=None):
        """Get JSON from a URL. Optionally save the data on disk."""
        r = requests.get(url)
        data = json.loads(r.text)
        if datadir is not None:
            path = os.path.abspath(datadir)
            now = dt.now().strftime("%Y-%m-%d-%H-%M-%S")
            name = now
            # Save json file.
            file = os.path.join(path, name.format(now=now, ext='json'))
            with open(file, 'w') as f:
                json.dump(data, f)
        return data
