from datetime import datetime as dt


def parse_result(datum):
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


def parse_url(data, date):
    """Parse vote URL for given date."""
    for datum in data['result']['resources']:
        if datum['coverage'] == date:
            return datum['download_url']
    return None


def parse_metadata(data):
    """Parse vote metadata."""
    def parse_vote_day(data):
        return dt.strptime(data['abstimmtag'], '%Y%m%d')

    def parse_vote_last_modified(data):
        return dt.strptime(data['timestamp'], '%Y-%m-%dT%H:%M:%S')

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
    last_modified = parse_vote_last_modified(data)
    vote_day = parse_vote_day(data)
    # Parse each vote specific metadata.
    metadata = list()
    for datum in data['schweiz']['vorlagen']:
        d = {
            'ogd_id':           datum['vorlagenId'],
            'vote_day':         vote_day,
            'last_modified':    last_modified,
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
