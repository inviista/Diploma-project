from urllib.parse import urlencode, urlparse, parse_qs, urlunparse


def add_query_param_to_url(url, param):
    url_parts = urlparse(url)
    query = parse_qs(url_parts.query)
    query.update(param)
    new_query = urlencode(query, doseq=True)
    return urlunparse((
        url_parts.scheme,
        url_parts.netloc,
        url_parts.path,
        url_parts.params,
        new_query,
        url_parts.fragment
    ))