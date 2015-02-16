import argparse
import calendar
import datetime
import decimal
import os

from urllib.parse import urljoin

import requests

from akamai.edgegrid import EdgeGridAuth

try:
    import simplejson as json
except:
    import json


base_url = os.environ['AK_BASE_URL']


def parse_args():
    parser = argparse.ArgumentParser(description='CDN usage report for Akamai')
    parser.add_argument(
        '-d', '--reporting-date',
        default=datetime.date.today() - datetime.timedelta(days=1),
        help='The date to use for calculation. Note that reporting data may '
             'lag behind. [default: %(default)s]',
    )
    return parser.parse_args()


def get_session():
    s = requests.Session()
    s.auth = EdgeGridAuth(
        client_token=os.environ['AK_CLIENT_TOKEN'],
        client_secret=os.environ['AK_CLIENT_SECRET'],
        access_token=os.environ['AK_ACCESS_TOKEN'],
    )
    return s


def create_lookup(list_of_dicts, key_func, value_func):
    ret = {}
    for item in list_of_dicts:
        ret[key_func(item)] = value_func(item)
    return ret


def get_report_sources(s):
    path = '/billing-usage/v1/reportSources'
    response = s.get(urljoin(base_url, path))
    if response.status_code != 200:
        raise Exception('Cannot get report sources')

    result = json.loads(response.text)
    assert result['status'] == 'ok'
    return result['contents']


def get_products(s, report_sources, date):
    path = '/billing-usage/v1/products'
    date_json = json.dumps({'month': date.month, 'year': date.year})
    data = {
        'reportSources': json.dumps(report_sources),
        'startDate': date_json,
        'endDate': date_json,
    }
    response = s.post(urljoin(base_url, path), data=data)
    if response.status_code != 200:
        raise Exception('Cannot get products')

    result = json.loads(response.text)
    assert result['status'] == 'ok'
    return result['contents']


def get_csv(s, report_sources, products, date):
    path = '/billing-usage/v1/contractUsageData/csv'
    date_json = json.dumps({'month': date.month, 'year': date.year})
    data = {
        'reportSources': json.dumps(report_sources),
        'products': json.dumps(products),
        'startDate': date_json,
        'endDate': date_json,
    }
    response = s.post(urljoin(base_url, path), data=data)
    if response.status_code != 200:
        raise Exception('Cannot get csv')

    return response.text


def get_cpcodes(s, report_source, month, year):
    path = '/billing-usage/v1/cpcodes/%(type)s/%(id)s' % report_source
    path += '/%d/%d' % (month, year)
    response = s.get(urljoin(base_url, path))
    if response.status_code != 200:
        raise Exception('Cannot get cpcodes')

    result = json.loads(response.text)
    assert result['status'] == 'ok'
    return result['contents']


def get_dimensions(s, type):
    path = '/media-reports/v1/%s/dimensions' % type
    response = s.get(urljoin(base_url, path))
    if response.status_code != 200:
        raise Exception('Cannot get object delivery dimensions')

    return json.loads(response.text)


def get_metrics(s, type):
    path = '/media-reports/v1/%s/metrics' % type
    response = s.get(urljoin(base_url, path))
    if response.status_code != 200:
        raise Exception('Cannot get object delivery metrics')

    return json.loads(response.text)


def get_data(s, type, start_date, end_date, lookups):
    dimension_names = ['Cpcode']
    metric_names = ['Edge Volume', 'Edge Hits']

    path = '/media-reports/v1/%s/data' % type

    # Endpoint expects a datetime, need to plus 1 to endDate to get midnight
    dt_format = '%m/%d/%Y:%H:%M'
    params = {
        'startDate': start_date.strftime(dt_format),
        'endDate': (end_date + datetime.timedelta(days=1)).strftime(dt_format),
        'dimensions': ','.join(
            str(lookups['dimension'][x])
            for x in dimension_names
        ),
        'metrics': ','.join(
            str(lookups['metric'][x])
            for x in metric_names
        ),
    }
    response = s.get(urljoin(base_url, path), params=params)

    print('== From %s to %s ==' % (start_date, end_date))

    if response.status_code == 204:
        print("No data")
        return

    if response.status_code != 200:
        print(response.status_code, response.text)
        raise Exception('Cannot get data for %s' % type)

    result = json.loads(response.text)
    for i, metric_name in enumerate(metric_names, 1):
        print('>>> %s:' % metric_name)
        unit = result['columns'][i]['unit'] or ''
        total = 0
        for row in result['rows']:
            total += decimal.Decimal(row[i])
            print('%s: %s %s' % (lookups['cpcode'][row[0]], row[i], unit))
        print('Total: %s %s' % (total, unit))


def main():
    args = parse_args()

    if isinstance(args.reporting_date, str):
        reporting_date = datetime.datetime.strptime(
            args.reporting_date, '%Y-%m-%d').date()
    else:
        reporting_date = args.reporting_date

    start_date = reporting_date.replace(day=1)
    last_day = calendar.monthrange(start_date.year, start_date.month)[1]
    end_date = start_date.replace(day=last_day)

    lm_end_date = start_date - datetime.timedelta(days=1)
    lm_start_date = lm_end_date.replace(day=1)
    lm_reporting_date = lm_start_date.replace(
        day=min(reporting_date.day, lm_end_date.day))

    s = get_session()

    report_sources = get_report_sources(s)

#    products = get_products(s, report_sources, args.reporting_date)
#    csv = get_csv(s, report_sources, products, args.reporting_date)
#    print(csv)
#    import sys; sys.exit(0)

    lookups = {}

    cpcodes = []
    today = datetime.date.today()
    for report_source in report_sources:
        cpcodes += get_cpcodes(s, report_source, today.month, today.year)
    lookups['cpcode'] = create_lookup(
        cpcodes,
        lambda x: str(x['code']),
        lambda x: x['description'])

    for type in ('object-delivery', 'adaptive-media-delivery'):
        dimensions = get_dimensions(s, type)
        lookups['dimension'] = create_lookup(
            dimensions,
            lambda x: x['name'],
            lambda x: x['id'])

        metrics = get_metrics(s, type)
        lookups['metric'] = create_lookup(
            metrics,
            lambda x: x['name'],
            lambda x: x['id'])

        for start, end in (
            (lm_start_date, lm_reporting_date),
            (lm_start_date, lm_end_date),
            (start_date, reporting_date),
            (start_date, end_date),
        ):
            get_data(s, type, start, end, lookups)


if __name__ == '__main__':
    main()
