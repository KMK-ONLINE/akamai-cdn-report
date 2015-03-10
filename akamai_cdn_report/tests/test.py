import datetime
import os
import responses

from json import dumps

from akamai_cdn_report import akamai_cdn_report as akamai

report_source = {
    'id': 'X-123ABC',
    'type': 'contract',
    'name': 'Top-Level Group: X-123ABC',
}


@responses.activate
def test_get_report_sources():
    contents = [report_source]
    responses.add(
        responses.GET,
        os.environ['AK_BASE_URL'] + 'billing-usage/v1/reportSources',
        body= dumps({
            'status': 'ok',
            'contents': contents,
        }),
        content_type="application/json"
    )
    s = akamai.get_session()
    return_value = akamai.get_report_sources(s)

    assert return_value == contents


@responses.activate
def test_get_cpcodes():
    contents =  [
        {
            'code': 123456,
            'description': 'staging.xxx.com',
        },
        {
            'code': 123457,
            'description': 'HD Universal Live',
        },
    ]

    responses.add(
        responses.GET,
        os.environ['AK_BASE_URL'] + 'billing-usage/v1/cpcodes/contract/X-123ABC/3/2015',
        body= dumps({
            'status': 'ok',
            'contents': contents,
        }),
        content_type="application/json"
    )

    s = akamai.get_session()
    return_value = akamai.get_cpcodes(s, report_source, 3, 2015)

    assert return_value == contents


@responses.activate
def test_get_dimensions():
    dimensions = [{'id': 18, 'description': 'content_type', 'name': 'Content Type'}, {'id': 2, 'description': 'cpcode', 'name': 'Cpcode'}]
    responses.add(
        responses.GET,
        os.environ['AK_BASE_URL'] + 'media-reports/v1/download-delivery/dimensions',
        body= dumps(dimensions),
        content_type="application/json"
    )
    s = akamai.get_session()
    return_value = akamai.get_dimensions(s, 'download-delivery')

    assert return_value == dimensions


@responses.activate
def test_get_metrics():
    metrics = [{'unit': None, 'id': 123, 'type': 'count', 'description': 'edge_volume', 'name': 'Edge Volume'}, {'unit': None, 'id': 24, 'type': 'count', 'description': 'hits_3xx', 'name': '3XX Edge Hits'}]
    responses.add(
        responses.GET,
        os.environ['AK_BASE_URL'] + 'media-reports/v1/download-delivery/metrics',
        body= dumps(metrics),
        content_type="application/json"
    )
    s = akamai.get_session()
    return_value = akamai.get_metrics(s, 'download-delivery')

    assert return_value == metrics


@responses.activate
def test_get_data():
    data = [
        ['123456', '1230415.26'],
        ['123457', '10389.74'],
    ]

    responses.add(
        responses.GET,
        os.environ['AK_BASE_URL'] + 'media-reports/v1/download-delivery/data?'
            + 'startDate=03%2F01%2F2015%3A00%3A00'
            + '&endDate=03%2F11%2F2015%3A00%3A00'
            + '&dimensions=2'
            + '&metrics=123',
        body= dumps({'rows': data}),
        content_type="application/json",
        match_querystring=True
    )
    s = akamai.get_session()

    lookups = {
        'cpcode': {
            '123456': 'staging.xxx.com',
            '123457': 'HD Universal Live',
        },
        'dimension': {
            'Cpcode': 2,
        },
        'metric': {
            'Edge Volume': 123,
        }
    }

    return_value = list(akamai.get_data(s, 'download-delivery', datetime.date(2015, 3, 1), datetime.date(2015, 3, 10), lookups))
    assert return_value == [
        ('staging.xxx.com', '1230415.26'),
        ('HD Universal Live', '10389.74'),
    ]
