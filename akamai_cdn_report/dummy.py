import datetime
import time

from json import dumps

from bottle import request, response, route, run, template


@route('/billing-usage/v1/reportSources')
def report_sources():
    return {
        'status': 'ok',
        'contents': [
            {
                'id': 'X-123ABC',
                'type': 'contract',
                'name': 'Top-Level Group: X-123ABC',
            },
        ],
    }


@route('/billing-usage/v1/cpcodes/<type>/<id>/<month>/<year>')
def cpcodes(type, id, month, year):
    return {
        'status': 'ok',
        'contents': [
            {
                'code': 123456,
                'description': 'staging.xxx.com',
            },
            {
                'code': 123457,
                'description': 'HD Universal Live',
            },
            {
                'code': 123458,
                'description': 'HD Universal VOD',
            },
            {
                'code': 123459,
                'description': 'NetStorage for Live',
            },
            {
                'code': 123460,
                'description': 'production.xxx.com',
            },
            {
                'code': 123461,
                'description': 'production.yyy.com',
            },
            {
                'code': 123466,
                'description': 'staging.yyy.com',
            },
        ],
    }


@route('/media-reports/v1/object-delivery/dimensions')
def od_dimensions():
    response.content_type = 'application/json'
    ret = [{'id': 18, 'description': 'content_type', 'name': 'Content Type'}, {'id': 2, 'description': 'cpcode', 'name': 'Cpcode'}, {'id': 19, 'description': 'file_extension', 'name': 'File Extension'}, {'id': 6, 'description': 'File Size Bucket', 'name': 'File Size Bucket'}, {'id': 1, 'description': 'time', 'name': 'Time'}]
    return dumps(ret)


@route('/media-reports/v1/object-delivery/metrics')
def od_metrics():
    response.content_type = 'application/json'
    ret = [{'unit': None, 'id': 21, 'type': 'count', 'description': 'hits_2xx', 'name': '2XX Edge Hits'}, {'unit': None, 'id': 24, 'type': 'count', 'description': 'hits_3xx', 'name': '3XX Edge Hits'}, {'unit': None, 'id': 25, 'type': 'count', 'description': 'hits_404', 'name': '404 Edge Hits'}, {'unit': None, 'id': 28, 'type': 'count', 'description': 'hits_4xx', 'name': '4XX Edge Hits'}, {'unit': None, 'id': 29, 'type': 'count', 'description': 'hits_5xx', 'name': '5XX Edge Hits'}, {'unit': '%', 'id': 112, 'type': 'percent', 'description': 'Cache Efficiency OD', 'name': 'Cache Efficiency'}, {'unit': None, 'id': 102, 'type': 'count', 'description': 'Edge Errors', 'name': 'Edge Errors'}, {'unit': None, 'id': 4, 'type': 'count', 'description': 'egress_hits', 'name': 'Edge Hits'}, {'unit': 'bps', 'id': 109, 'type': 'bandwidth', 'description': 'Edge Throughput - OD', 'name': 'Edge Throughput'}, {'unit': 'MB', 'id': 44, 'type': 'volume', 'description': 'Egress Bytes in MB', 'name': 'Edge Volume'}, {'unit': None, 'id': 46, 'type': 'count', 'description': 'origin_hits', 'name': 'Ingress Hits'}, {'unit': 'bytes', 'id': 43, 'type': 'volume', 'description': 'midgress_bytes', 'name': 'Midgress Bytes'}, {'unit': 'bytes', 'id': 9, 'type': 'volume', 'description': 'midgress_hits', 'name': 'Midgress hits'}, {'unit': 'bytes', 'id': 35, 'type': 'volume', 'description': 'netstorage_bytes', 'name': 'Netstorage Bytes'}, {'unit': None, 'id': 34, 'type': 'count', 'description': 'netstorage_hits', 'name': 'Netstorage Hits'}, {'unit': 'bytes', 'id': 42, 'type': 'volume', 'description': 'origin_bytes', 'name': 'Origin Bytes'}, {'unit': '%', 'id': 111, 'type': 'percent', 'description': 'Origin Offload OD', 'name': 'Origin Offload'}, {'unit': None, 'id': 36, 'type': None, 'description': 'sparemetric_1', 'name': 'sparemetric_1'}, {'unit': None, 'id': 37, 'type': None, 'description': 'sparemetric_2', 'name': 'sparemetric_2'}]
    return dumps(ret)


def parse_dt(s):
    dt_format = '%m/%d/%Y:%H:%M'
    return datetime.datetime.strptime(s, dt_format)


def to_timestamp(dt):
    return int(time.mktime(dt.timetuple()))


@route('/media-reports/v1/object-delivery/data')
def od_data():
    dt_format = '%m/%d/%Y:%H:%M'
    start_date = parse_dt(request.query.startDate)
    end_date = parse_dt(request.query.endDate)

    data = [
        [
            ['123460', '1230415.26'], 
            ['123456', '10389.74'], 
            ['123466', '4016.57'], 
            ['123461', '1.68'], 
        ],
        [
            ['123456', '2152.38'],
        ],
        [
            ['123456', '3858.24'],
            ['123460', '395.39'],
            ['123461', '0.02'],
        ],
    ]

    if end_date.date() == datetime.date(2015, 2, 1):
        d = data[2]
    elif start_date.date() == datetime.date(2015, 1, 1):
        d = data[1]
    else:
        d = data[0]

    return {
        'rows': d,
        'columns': [
            {'index': 0, 'description': 'cpcode', 'type': 'dimension', 'name': 'Cpcode'}, 
            {
                'unit': 'MB',
                'index': 1,
                'peak': str(max(float(x) for x in list(zip(*d))[1])),
                'description': 'Egress Bytes in MB',
                'type': 'metric',
                'aggregate': str(round(sum(float(x) for x in list(zip(*d))[1]), 2)),
                'name': 'Edge Volume',
            }
        ], 
        'metaData': {
            'hasMoreData': False,
            'aggregation': 'day',
            'limit': 300,
            'reportPack': 'PT XYZ DOT COM',
            'offset': 0,
            'startTimeInEpoch': to_timestamp(start_date),
            'endTimeInEpoch': to_timestamp(end_date),
            'timeZone': 'GMT',
        }
    }


@route('/media-reports/v1/adaptive-media-delivery/dimensions')
def od_dimensions():
    response.content_type = 'application/json'
    ret = [{'id': 14, 'description': 'city', 'name': 'City'}, {'id': 24, 'description': 'Country Name', 'name': 'Country Name'}, {'id': 2, 'description': 'cpcode', 'name': 'Cpcode'}, {'id': 7, 'description': 'device/browser', 'name': 'Device'}, {'id': 10, 'description': 'encoded_bitrate', 'name': 'Encoded Bitrate'}, {'id': 6, 'description': 'File Size Bucket', 'name': 'File Size Bucket'}, {'id': 4, 'description': 'hostname', 'name': 'Hostname'}, {'id': 17, 'description': 'as_num', 'name': 'ISP'}, {'id': 9, 'description': 'network_type', 'name': 'Network Type'}, {'id': 8, 'description': 'device_os', 'name': 'OS'}, {'id': 5, 'description': 'stream Id or URL', 'name': 'Stream ID/URL'}, {'id': 1, 'description': 'time', 'name': 'Time'}]
    return dumps(ret)


@route('/media-reports/v1/adaptive-media-delivery/metrics')
def od_metrics():
    response.content_type = 'application/json'
    ret = [{'unit': None, 'id': 18, 'type': 'count', 'description': 'hits_000', 'name': '0XX Edge Hits'}, {'unit': None, 'id': 19, 'type': 'count', 'description': 'hits_200', 'name': '200 Edge Hits'}, {'unit': None, 'id': 20, 'type': 'count', 'description': 'hits_206', 'name': '206 Edge Hits'}, {'unit': None, 'id': 21, 'type': 'count', 'description': 'hits_2xx', 'name': '2XX Edge Hits'}, {'unit': None, 'id': 22, 'type': 'count', 'description': 'hits_302', 'name': '302 Edge Hits'}, {'unit': None, 'id': 23, 'type': 'count', 'description': 'hits_304', 'name': '304 Edge Hits'}, {'unit': None, 'id': 24, 'type': 'count', 'description': 'hits_3xx', 'name': '3XX Edge Hits'}, {'unit': None, 'id': 27, 'type': 'count', 'description': 'hits_403_l', 'name': '403L Edge Hits'}, {'unit': None, 'id': 25, 'type': 'count', 'description': 'hits_404', 'name': '404 Edge Hits'}, {'unit': 'bytes', 'id': 32, 'type': 'volume', 'description': 'err_404_objbytes', 'name': '404 Object Bytes'}, {'unit': 'bytes', 'id': 33, 'type': 'volume', 'description': 'err_404_overbytes', 'name': '404 Overhead Bytes'}, {'unit': None, 'id': 26, 'type': 'count', 'description': 'hits_415', 'name': '415 Edge Hits'}, {'unit': None, 'id': 28, 'type': 'count', 'description': 'hits_4xx', 'name': '4XX Edge Hits'}, {'unit': None, 'id': 29, 'type': 'count', 'description': 'hits_5xx', 'name': '5XX Edge Hits'}, {'unit': None, 'id': 101, 'type': 'count', 'description': 'Avg. Playback sessions in aggregation', 'name': 'Avg. Playback Sessions'}, {'unit': '%', 'id': 104, 'type': 'percent', 'description': 'Cache Efficiency', 'name': 'Cache Efficiency'}, {'unit': None, 'id': 31, 'type': 'count', 'description': 'hits_cad_err', 'name': 'Client Assisted Unicast Error Hits'}, {'unit': None, 'id': 16, 'type': 'count', 'description': 'lastbyte_hits', 'name': 'Download Completed'}, {'unit': None, 'id': 105, 'type': 'count', 'description': 'Edge Attempts', 'name': 'Edge Attempts'}, {'unit': 'bytes', 'id': 7, 'type': 'volume', 'description': 'egress_cached_bytes', 'name': 'Edge Cached Bytes'}, {'unit': None, 'id': 102, 'type': 'count', 'description': 'Edge Errors', 'name': 'Edge Errors'}, {'unit': None, 'id': 4, 'type': 'count', 'description': 'egress_hits', 'name': 'Edge Hits'}, {'unit': None, 'id': 117, 'type': 'count', 'description': 'startup_errors based on error flag for AMD', 'name': 'Edge Manifest Failures'}, {'unit': '%', 'id': 100, 'type': 'percent', 'description': 'Edge Manifest Success (%)', 'name': 'Edge Manifest Success (%)'}, {'unit': 'bytes', 'id': 5, 'type': 'volume', 'description': 'egress_objbytes', 'name': 'Edge Object Bytes'}, {'unit': 'bytes', 'id': 6, 'type': 'volume', 'description': 'egress_overbytes', 'name': 'Edge Overhead Bytes'}, {'unit': None, 'id': 15, 'type': 'count', 'description': 'Edge Play', 'name': 'Edge Plays'}, {'unit': 'bytes', 'id': 8, 'type': 'volume', 'description': 'egress_secure_bytes', 'name': 'Edge Secure Bytes'}, {'unit': 'bps', 'id': 103, 'type': 'bandwidth', 'description': 'Edge Throughput', 'name': 'Edge Throughput'}, {'unit': None, 'id': 38, 'type': 'count', 'description': 'Edge Uniques', 'name': 'Edge Uniques'}, {'unit': 'MB', 'id': 107, 'type': 'volume', 'description': 'Edge Volume', 'name': 'Edge Volume'}, {'unit': None, 'id': 114, 'type': 'count', 'description': 'Mid-Stream Errors', 'name': 'Mid-Stream Errors'}, {'unit': 'bytes', 'id': 116, 'type': 'volume', 'description': 'midgress_bytes', 'name': 'Midgress Bytes'}, {'unit': 'bytes', 'id': 10, 'type': 'volume', 'description': 'midgress_objbytes', 'name': 'Midgress Object Bytes'}, {'unit': 'bytes', 'id': 11, 'type': 'volume', 'description': 'midgress_overbytes', 'name': 'Midgress Overhead Bytes'}, {'unit': 'bytes', 'id': 9, 'type': 'volume', 'description': 'midgress_hits', 'name': 'Midgress hits'}, {'unit': 'bytes', 'id': 35, 'type': 'volume', 'description': 'netstorage_bytes', 'name': 'Netstorage Bytes'}, {'unit': None, 'id': 34, 'type': 'count', 'description': 'netstorage_hits', 'name': 'Netstorage Hits'}, {'unit': 'bytes', 'id': 115, 'type': 'volume', 'description': 'origin_bytes', 'name': 'Origin Bytes'}, {'unit': None, 'id': 12, 'type': 'count', 'description': 'origin_hits', 'name': 'Origin Hits'}, {'unit': 'bytes', 'id': 13, 'type': 'volume', 'description': 'origin_objbytes', 'name': 'Origin Object Bytes'}, {'unit': '%', 'id': 106, 'type': 'percent', 'description': 'Origin Offload', 'name': 'Origin Offload'}, {'unit': 'bytes', 'id': 14, 'type': 'volume', 'description': 'origin_overbytes', 'name': 'Origin Overhead Bytes'}, {'unit': None, 'id': 30, 'type': 'count', 'description': 'hits_xxx', 'name': 'Other Hits'}, {'unit': 'bytes', 'id': 3, 'type': 'volume', 'description': 'peer_bytes', 'name': 'Peer Bytes'}, {'unit': 'seconds', 'id': 1, 'type': 'time', 'description': 'Play Duration', 'name': 'Play Duration'}, {'unit': 'bytes', 'id': 2, 'type': 'volume', 'description': 'total_bytes', 'name': 'Total Bytes'}, {'unit': None, 'id': 36, 'type': None, 'description': 'sparemetric_1', 'name': 'sparemetric_1'}, {'unit': None, 'id': 37, 'type': None, 'description': 'sparemetric_2', 'name': 'sparemetric_2'}]
    return dumps(ret)


@route('/media-reports/v1/adaptive-media-delivery/data')
def od_data():
    dt_format = '%m/%d/%Y:%H:%M'
    start_date = parse_dt(request.query.startDate)
    end_date = parse_dt(request.query.endDate)

    data = [
        [
            ['123458', '660084.49'],
            ['123457', '66914.79'], 
        ],
        None,
        [
            ['123458', '3053.66'],
        ],
    ]

    if end_date.date() == datetime.date(2015, 2, 1):
        d = data[2]
    elif start_date.date() == datetime.date(2015, 1, 1):
        d = data[1]
    else:
        d = data[0]

    if not d:
        response.status = 204
        return

    return {
        'rows': d,
        'columns': [
            {'index': 0, 'description': 'cpcode', 'type': 'dimension', 'name': 'Cpcode'}, 
            {
                'unit': 'MB',
                'index': 1,
                'peak': str(max(float(x) for x in list(zip(*d))[1])),
                'description': 'Edge Volume',
                'type': 'metric',
                'aggregate': str(round(sum(float(x) for x in list(zip(*d))[1]), 2)),
                'name': 'Edge Volume',
            }
        ], 
        'metaData': {
            'hasMoreData': False,
            'aggregation': 'day',
            'limit': 300,
            'reportPack': 'PT XYZ DOT COM',
            'offset': 0,
            'startTimeInEpoch': to_timestamp(start_date),
            'endTimeInEpoch': to_timestamp(end_date),
            'timeZone': 'GMT',
        },
    }


run(host='localhost', port=8080)
