import argparse
import datetime
import math
import os

from collections import OrderedDict
from decimal import Decimal
from urllib.parse import urljoin

import requests

from akamai.edgegrid import EdgeGridAuth
from terminaltables import AsciiTable

try:
    import simplejson as json
except:
    import json


base_url = os.environ['AK_BASE_URL']

TB_IN_MBYTES = 10**6
GB_IN_MBYTES = 10**3
#TB_IN_MBYTES = int(math.pow(2, 20))
#GB_IN_MBYTES = int(math.pow(2, 10))


def f(n_mbytes): 
    if (n_mbytes / TB_IN_MBYTES > 1):
      return '%.2f TB' % (n_mbytes / TB_IN_MBYTES)
    elif (n_mbytes / GB_IN_MBYTES > 1):
      return '%.2f GB' % (n_mbytes / GB_IN_MBYTES)
    else:
      return '%.2f MB' % n_mbytes


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
        raise Exception('Cannot get download delivery dimensions')

    return json.loads(response.text)


def get_metrics(s, type):
    path = '/media-reports/v1/%s/metrics' % type
    response = s.get(urljoin(base_url, path))
    if response.status_code != 200:
        raise Exception('Cannot get download delivery metrics')

    return json.loads(response.text)


def get_data(s, type, start_date, end_date, lookups):
    path = '/media-reports/v1/%s/data' % type

    # Endpoint expects a datetime, need to plus 1 to endDate to get midnight
    dt_format = '%m/%d/%Y:%H:%M'
    params = {
        'startDate': start_date.strftime(dt_format),
        'endDate': (end_date + datetime.timedelta(days=1)).strftime(dt_format),
        'dimensions': lookups['dimension']['Cpcode'],
        'metrics': lookups['metric']['Edge Volume'],
    }
    response = s.get(urljoin(base_url, path), params=params)

    if response.status_code == 204:
        return

    if response.status_code != 200:
        print(response.status_code, response.text)
        raise Exception('Cannot get data: %s' % response.url)

    result = json.loads(response.text)
    for row in result['rows']:
        yield (lookups['cpcode'][row[0]], row[1])


def print_table(data, columns):
    d = OrderedDict()
    headers = [''] + columns
    rows = [headers]

    for type, period_idx, cpcode, value in data:
        if type not in d:
            d[type] = OrderedDict()
        if cpcode not in d[type]:
            d[type][cpcode] = [Decimal('0.00')] * len(columns)
        d[type][cpcode][period_idx] = Decimal(value)

    def to_title(s):
        return s.replace('-', ' ').title()

    total_values_list = []
    for type, data_by_cpcode in d.items():
        type_values_list = []

        for cpcode, values in data_by_cpcode.items():
            # call str as terminaltables can only print strings
            rows.append([cpcode] + [f(x) for x in values])
            type_values_list.append(values)

        type_values = [sum(x) for x in zip(*type_values_list)]
        rows.append([])
        rows.append([to_title(type)] + [f(x) for x in type_values])
        rows.append([])
        total_values_list.append(type_values)

    total_values = [sum(x) for x in zip(*total_values_list)]
    rows.append(['Total'] + [f(x) for x in total_values])

    table = AsciiTable(rows)
    table.justify_columns = dict((i + 1, 'right') for i in range(len(columns)))
    print(table.table)


def main():
    args = parse_args()

    if isinstance(args.reporting_date, str):
        reporting_date = datetime.datetime.strptime(
            args.reporting_date, '%Y-%m-%d').date()
    else:
        reporting_date = args.reporting_date

    start_date = reporting_date.replace(day=1)

    lm_end_date = start_date - datetime.timedelta(days=1)
    lm_start_date = lm_end_date.replace(day=1)
    lm_reporting_date = lm_start_date.replace(
        day=min(reporting_date.day, lm_end_date.day))

    s = get_session()

    report_sources = get_report_sources(s)

    lookups = {}

    cpcodes = []
    today = datetime.date.today()
    for report_source in report_sources:
        cpcodes += get_cpcodes(s, report_source, today.month, today.year)
    lookups['cpcode'] = create_lookup(
        cpcodes,
        lambda x: str(x['code']),
        lambda x: x['description'])

    data = []

    periods = OrderedDict([
        ('Cur MTD', (start_date, reporting_date)),
        ('Last MTD', (lm_start_date, lm_reporting_date)),
        ('Last Total', (lm_start_date, lm_end_date)),
    ])

    for type in ('download-delivery', 'adaptive-media-delivery'):
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

        for period_idx, (start, end) in enumerate(periods.values()):
            try:
              for cpcode, value in get_data(s, type, start, end, lookups):
                  data.append([type, period_idx, cpcode, value])
            except Exception as ex:
              print(ex)
              continue

    print_table(data, list(periods.keys()))


if __name__ == '__main__':
    main()
