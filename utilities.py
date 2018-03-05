#!/usr/bin/env python3

import json

from geoip2.database import Reader
from os import listdir
from os.path import isfile, join

reader = Reader('GeoLite2-City_20180206/GeoLite2-City.mmdb')

def get_config_files_from_dir(directory):
    return [f for f in listdir(directory) if isfile(join(directory, f)) and f.endswith('.udp1194.ovpn')]

def is_valid_ip(ip):
    allowed_chars = '0123456789.'
    for x in ip:
        if x not in allowed_chars:
            return False
    return True

def is_valid_name(name):
    allowed_chars = 'abcdefghijklmnopqrstuvwxyz01234567890.'
    for x in name:
        if x not in allowed_chars:
            return False
    return True

def get_ip_from_file(filename):
    with open(filename, 'r') as fd:
        for line in fd:
            if line.startswith('remote '):
                return line.split(' ')[1]
    return None

def get_lat_long(ip):
    city = reader.city(ip)
    data = {}
    data['lat'] = city.location.latitude if city.location.latitude else 0
    data['lng'] = city.location.longitude if city.location.longitude else 0
    data['city'] = city.city.names['en'] if 'en' in city.city.names else 'Unkown'
    data['country'] = city.country.names['en'] if 'en' in city.country.names else 'Unknown'
    return data

def gen_json(directory):
    data = []
    configs = get_config_files_from_dir(directory)
    for config in configs:
        ip = get_ip_from_file('%s/%s' % (directory, config))
        lat_lng = get_lat_long(ip)
        if lat_lng['lat'] == 0 and lat_lng['lng'] == 0:
            continue
        data.append(lat_lng)
        data[-1]['title'] = ip
        data[-1]['config'] = config
        data[-1]['infobox'] = "<strong>IP:</strong> %s<br />" % ip
        data[-1]['infobox'] += "%s, %s<br />" % (lat_lng['city'], lat_lng['country'])
        data[-1]['infobox'] += "<button onclick=\"connect('%s');\">Connect</button>&nbsp;" % config
        data[-1]['infobox'] += "<button onclick=\"ping('%s');\">Ping</button>" % ip
    return json.dumps(data)

def gen_data_file(directory, out):
    data = gen_json(directory)
    with open(out, 'w') as fd:
        fd.write(data)

def load_data_file(filename):
    with open(filename, 'r') as fd:
        return json.loads(fd.read())
