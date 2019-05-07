import logging

logger = logging.getLogger(__name__)

TITLE_WEIGHT = 4
DESCRIPTION_WEIGHT = 1.2
JOB_SCHOOL_BOOST = 1
ALL_JOB_SCHOOL_BOOST = 0.125


def build_query(qs='*', start=0, size=10, sort=None):
    query = {
        'query': build_query_string(qs),
        'from': start,
        'size': size,
    }

    if sort:
        query['sort'] = [
            {
                sort: 'desc'
            }
        ]
    return query


# Match queryObject in search.js
def build_query_string(qs):
    field_boosts = {
        'title': TITLE_WEIGHT,
        'description': DESCRIPTION_WEIGHT,
        'job': JOB_SCHOOL_BOOST,
        'school': JOB_SCHOOL_BOOST,
        'all_jobs': ALL_JOB_SCHOOL_BOOST,
        'all_schools': ALL_JOB_SCHOOL_BOOST,
        '_all': 1,

    }

    fields = ['{}^{}'.format(k, v) for k, v in field_boosts.iteritems()]
    return {
        'query_string': {
            'default_field': '_all',
            'fields': fields,
            'query': qs,
            'analyze_wildcard': True,
            'lenient': True  # TODO, may not want to do this
        }
    }


def build_fuzzy_query(qs, pid):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": qs,
                            "fields": ["_all"],
                            "fuzziness": "50"
                        }
                    },
                    {
                        "match": {
                            "project": pid
                        }
                    }
                ]
            }
        }
    }
    return query


def clean_splitters(text):
    new_text = text.replace('_', ' ').replace('-', ' ').replace('.', ' ')
    if new_text == text:
        return ''
    return new_text
