import socket
import json

from flask import g, Flask, render_template, redirect, jsonify
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from time import sleep

from utilities import load_data_file, gen_data_file, get_lat_long, is_valid_ip, is_valid_name
from subprocess import Popen, PIPE

app = Flask(__name__, template_folder="templates")
GoogleMaps(app)

config = load_data_file('config.json')
gen_data_file(config['config_path'], 'nordvpn.json')
data = load_data_file('nordvpn.json')

def update_config(key, value):
    global config
    config[key] = value
    with open('config.json', 'w') as fd:
        fd.write(json.dumps(config))

@app.route("/")
def mapview():
    # creating a map in the view
    last_ip = config['last_connected']
    last = [ip for ip in data if ip['config'] == last_ip][0]

    sndmap = Map(
        identifier="NordVPN",
        lat=last['lat'],
        lng=last['lng'],
        style="height:1024px;width:1024px;margin:0;",
        zoom=5,
        markers=data
    )
    return render_template('main.html', sndmap=sndmap)

@app.route("/api/current_ip")
def get_current_ip():
    from urllib.request import urlopen
    req = urlopen("https://api.ipify.org?format=json")
    data = req.read()
    encoding = req.info().get_content_charset('utf-8')
    return jsonify(json.loads(data.decode(encoding)))

@app.route("/api/location_data/<ip>")
def get_location_data(ip):
    if not is_valid_ip(ip):
        return redirect('/')
    return jsonify(get_lat_long(ip))

@app.route("/ping/<ip>")
def ping_node(ip):
    if not is_valid_ip(ip):
        return redirect('/')
    pid = Popen(['ping', ip, '-c 1'], stdout=PIPE)
    data = str(pid.stdout.read())
    idx = data.find('time=') + 5
    ms = data[idx:].split(' ')[0]
    return jsonify({'result': '%s ms' % ms})

def connect(name):
    Popen(['sudo', 'killall', '-9', 'openvpn'])
    sleep(0.5)
    sock_path = config['sock_path'] 
    if config['tcp'] == 1:
        name = name.replace('udp1194', 'tcp443')
    options = ["sudo", "openvpn" ]
    options.extend(["--management", sock_path, "unix", "--config", 
            "%s/%s" % (config['config_path'], name),
            "--management-query-passwords"])
    options.append("2>&1 > openvpn.out")
    ps = Popen(" ".join(options), shell=True, stdout=PIPE, bufsize=1)
    mgmt = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sleep(1)
    connect_try = 1
    
    while connect_try < 5:
        try:
            connect_try += 1
            mgmt.connect(sock_path)
            mgmt.sendall("username 'Auth' '{}'\r\n".format(config['user']).encode())
            mgmt.sendall("password 'Auth' '{}'\r\n".format(config['password']).encode())
            mgmt.sendall("quit\r\n".encode())
            break
        except socket.error as e:
            if e.errno in [111]:
                sleep(5)
    return connect_try

@app.route("/connect/<name>")
def connect_node(name):
    if not is_valid_name(name):
        return redirect('/')
    
    update_config('last_connected', name)

    tries = connect(name)
    return jsonify({'result': tries})

if __name__ == "__main__":
    if config['auto_connect'] == 1:
        connect(config['last_connected'])
    app.run(debug=True)

