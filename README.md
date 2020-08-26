# swissvotes
*Scrape Swiss referendum vote results from [opendata.swiss](https://opendata.swiss/en/)*

## Installation

Clone the repo and install the library:
~~~bash
git clone git@github.com:victorkristof/swissvotes.git
cd swissvotes
pip install -r requirements.txt
pip install .
~~~

## Usage

The library provides a client to [opendata.swiss](https://opendata.swiss/en/):
~~~python
from swissvotes import Client

client = Client()
~~~

The client enables you to query the API.
Usually, you would start by fetching the vote URLs as a dictionary `{date: url}`
~~~python
urls = client.available_votes()
url = urls['2020-02-09']
# url --> https://www.bfs.admin.ch/bfsstatic/dam/assets/11708082/master
~~~

You can retrieve the votes' metadata for a given URL by calling:
~~~python
metadata = client.get_vote_metadata(url)
# metadata --> list of dict
~~~
Each dictionary in `metadata` contains details about the votes (identified uniquely by the `ogd_id` key).

Finally, you can scrape the results at a given URL by doing:
~~~python
results = client.get_results(url, level='municipality')
# results --> dict of list
~~~
The keys of `results` are the vote OGD ids, and the values are a list of results.
Each result is a dictionary with data such as the number of "yes", the number of voters, the name of the municipality, and a timestamp.
The `level` argument of `client.get_results(...)` enables you to choose the level at which you would like to scrape the results.
It accepts the following keys:
- `canton`: results in the 26 cantons (i.e., the Swiss states)
- `district`: results in the Swiss districts ("bezirke")
- `zhdistrict`: results in the counting districts ("zaehlkreise") of Zurich and Winterthur
- `municipality`: results in the ~2200 municipalities
- `municipality+zhdistrict`: results in the municipalities and the counting districts
The last key is useful to have a finer level of granularity of the results in Zurich and Winterthur, two the largest municipalities in Switzerland (the results in the counting districts are released sequentially as soon as they are available, whereas the aggregate results in the whole municipality is released much later).

## Download Raw Data

The two methods `client.get_vote_metadata(...)` and `client.get_results(...)` optionally takes an argument `file='path/to/data.json'`, which enables you to save the raw JSON data to the given path.
