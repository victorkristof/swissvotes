import re
from collections import defaultdict


def parse_result(datum):
    """Parse result as a dict."""
    res = datum['resultat']
    return {
        'num_yes':       res['jaStimmenAbsolut'],
        'num_no':        res['neinStimmenAbsolut'],
        'num_valid':     res['gueltigeStimmen'],
        'num_total':     res['eingelegteStimmzettel'],
        'num_eligible':  res['anzahlStimmberechtigte'],
        'yes_percent':   res['jaStimmenInProzent'],
        'turnout':       res['stimmbeteiligungInProzent'],
        'counted':       res['gebietAusgezaehlt']
    }


def parse_metadata(data, url):
    """Parse vote metadata."""
    def parse_titles(datum):
        titles = dict()
        for title in datum['vorlagenTitel']:
            titles['title_' + title['langKey']] = title['text']
        return titles

    def parse_canton_counts(datum):
        """Parse number of whole and half cantons voting yes and no."""
        count = datum['staende']
        return {
            'num_yes_whole':  count['jaStaendeGanz'],
            'num_no_whole':   count['neinStaendeGanz'],
            'num_whole':      count['anzahlStaendeGanz'],
            'num_yes_half':   count['jaStaendeHalb'],
            'num_no_half':    count['neinStaendeHalb'],
            'num_half':       count['anzahlStaendeHalb'],
        }

    # Parse common metadata.
    last_modified = data['timestamp']
    vote_day = re.sub(r'(\d{4})(\d\d)(\d\d)', r'\1-\2-\3', data['abstimmtag'])
    # Parse each vote specific metadata.
    metadata = list()
    for datum in data['schweiz']['vorlagen']:
        d = {
            'ogd_id':           int(datum['vorlagenId']),
            'vote_day':         vote_day,
            'last_modified':    last_modified,
            'url':              url,
            'accepted':         datum['vorlageAngenommen'],
            'double_majority':  datum['doppeltesMehr'],
            'is_final':         datum['vorlageBeendet'],
            'canton_counts':    parse_canton_counts(datum)
        }
        # Add rest of metadata.
        d.update(parse_titles(datum))
        d.update(parse_result(datum))
        metadata.append(d)
    return metadata


def parse_results(data, level):
    """Parse results at a given geographical level."""
    def parse_datum(datum, canton=None):
        d = parse_result(datum)
        d['ogd_id'] = int(datum['geoLevelnummer'])
        d['name'] = datum['geoLevelname']
        d['timestamp'] = timestamp
        if canton:
            d['canton'] = canton['geoLevelname']
        return d

    # Case canton.
    if level == 'canton':
        key = 'canton'
    # Case districts.
    elif level == 'district':
        key = 'bezirke'
    # Case Zurich's counting districts.
    elif level == 'zhdistrict':
        key = 'zaehlkreise'
    # Case municipalities.
    elif level == 'municipality':
        key = 'gemeinden'
    elif level == 'municipality+zhdistrict':
        key = ['gemeinden', 'zaehlkreise']

    timestamp = data['timestamp'].replace('T', ' ')  # Parse timestamp.
    # Parse results for corresponding geographical level.
    results = defaultdict(list)
    for vote in data['schweiz']['vorlagen']:
        ogd = vote['vorlagenId']
        for canton in vote['kantone']:
            # If the level is canton.
            if key == 'canton':
                res = parse_datum(canton)
                results[ogd].append(res)
            # If the level is municipality AND counting districts.
            elif type(key) is list:
                for k in key:
                    for datum in canton.get(k, []):
                        res = parse_datum(datum, canton)
                        results[ogd].append(res)
            # If the level is (counting) district or municipality.
            else:
                for datum in canton.get(key, []):
                    res = parse_datum(datum, canton)
                    results[ogd].append(res)
    return dict(results)
