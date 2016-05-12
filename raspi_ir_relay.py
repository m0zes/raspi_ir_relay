#!/usr/bin/python
# Copyright (c) 2016, <name of copyright holder>
# Author: Tygart, Adam <mozestygart@gmail.com>
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function

from flask import Flask, url_for, jsonify, make_response, render_template, json,\
    request
import flask_from_url
import time
import os
import subprocess
from flask_socketio import SocketIO, emit

try:
    import piplates.RELAYplate as RELAY
except:
    print("Warning: piplates controller could not be loaded")
    print("Warning: enabling TESTING mode")
    TESTING = True
    import testingRELAYplate as RELAY

DEBUG = True
LIRCD_CONF = '/etc/lirc/lircd.conf'
REMOTE_CONF_DIR = os.path.join(os.path.dirname(LIRCD_CONF), 'lircd.conf.d')
MACRO_CONF_DIR = 'macros'
PLATE_CONF_DIR = 'plates'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('RASPI_IR_RELAY_SETTINGS', silent=True)
socketio = SocketIO(app)

if not os.path.isabs(REMOTE_CONF_DIR):
    REMOTE_CONF_DIR = os.path.join(
        os.path.dirname(__file__),
        REMOTE_CONF_DIR
    )

if not os.path.isabs(MACRO_CONF_DIR):
    MACRO_CONF_DIR = os.path.join(
        os.path.dirname(__file__),
        MACRO_CONF_DIR
    )

if not os.path.isabs(PLATE_CONF_DIR):
    PLATE_CONF_DIR = os.path.join(
        os.path.dirname(__file__),
        PLATE_CONF_DIR
    )


def get_list_of_relay_plates():
    plates = []
    i = 0
    for plate in RELAY.relaysPresent:
        if plate == 1:
            plates.append(i)
        i += 1
    return plates


def load_relay_plate_conf(plate_num):
    plate_fn = os.path.join(PLATE_CONF_DIR, "plate_{}.json".format(plate_num))
    if not os.path.exists(plate_fn) or not os.path.isfile(plate_fn):
        plate_conf = {"name": "plate_{}".format(plate_num)}

        for relay in range(1, 8):
            plate_conf['relay_{}'.format(relay)] = 'relay_{}'.format(relay)
    else:
        with open(plate_fn, 'r') as f:
            plate_conf = json.load(f)
    return plate_conf


def save_relay_plate_conf(plate_num, plate_conf):
    if not os.path.exists(PLATE_CONF_DIR):
        os.mkdir(PLATE_CONF_DIR)
    plate_fn = os.path.join(PLATE_CONF_DIR, "plate_{}.json".format(plate_num))
    with open(plate_fn, 'w') as f:
        json.dump(plate_conf, f)


def get_state_of_relays_on_plate(plate_num):
    if RELAY.getADDR(plate_num) != plate_num:
        raise Exception("Plate Number is invalid")
    status_num = RELAY.relaySTATE(plate_num)
    relay_status = {}
    relay_num = 0
    while relay_num < 7:
        relay_num += 1
        if status_num & 1 == 1:
            relay_status[relay_num] = 'on'
        else:
            relay_status[relay_num] = 'off'
        status_num = status_num >> 1
    return relay_status


def toggle_state_of_relay(plate_num, relay_num):
    RELAY.relayTOGGLE(plate_num, relay_num)
    relay_status = get_state_of_relays_on_plate(plate_num)
    return relay_status[relay_num]


def toggle_leds_on_plate(plate_num):
    if plate_num not in get_list_of_relay_plates():
        raise Exception("Plate Number is invalid")
    RELAY.toggleLED(plate_num)


def setup_remote_conf_dir():
    if not os.path.exists(REMOTE_CONF_DIR):
        os.mkdir(REMOTE_CONF_DIR)
    elif not os.path.isdir(REMOTE_CONF_DIR):
        raise Exception("Incorrect REMOTE_CONF_DIR configuration")


def get_list_of_remotes():
    setup_remote_conf_dir()
    remotes = []
    for item in os.listdir(REMOTE_CONF_DIR):
        if '.conf' not in item:
            continue
        remotes.append(item.split('.conf')[0])
    return remotes


def get_list_of_buttons_for_irrecord():
    proc = subprocess.Popen(
        ['irrecord', '--list-namespace'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    buttons, error = proc.communicate()
    if proc.returncode > 0:
        raise Exception(error)
    lb = []
    for button in buttons.decode('ascii', 'ignore').split('\n'):
        if button == '':
            continue
        lb.append(button.strip())
    return lb


def generate_lircd_conf():
    with open(LIRCD_CONF, 'w') as f:
        for remote in get_list_of_remotes():
            f.write(
                'include "{}"\n'.format(
                    os.path.join(
                        REMOTE_CONF_DIR,
                        '{}.conf'.format(remote)
                    )
                )
            )


def set_remote_definition(remote_json, remote_name=None):
    setup_remote_conf_dir()
    ds_name = remote_json.keys()[0]
    if remote_name is None:
        remote_name = ds_name
    remote_fn = "{}.conf".format(remote_name)
    with open(os.path.join(REMOTE_CONF_DIR, remote_fn), 'w') as f:
        for line in remote_json[ds_name].split('\n'):
            if 'begin remote' in line:
                named = False
            if 'name' in line:
                line = '\tname {}\n'.format(remote_name)
                named = True
            if 'begin codes' in line and not named:
                f.write('\tname {}\n'.format(remote_name))
            if 'end remote' in line:
                f.write('{}\n'.format(line))
                break
            f.write('{}\n'.format(line))
    generate_lircd_conf()


def remove_remote_definition(remote_name):
    setup_remote_conf_dir()
    os.remove(os.path.join(
        REMOTE_CONF_DIR,
        "{}.conf".format(remote_name)
    ))
    generate_lircd_conf()


def get_list_of_remote_buttons(remote_name):
    conf_file = os.path.join(REMOTE_CONF_DIR, "{}.conf".format(remote_name))
    buttons = []
    with open(conf_file, 'r') as f:
        started_codes = False
        for line in f:
            if 'begin codes' in line:
                started_codes = True
                continue
            if not started_codes:
                continue
            if 'end codes' in line:
                break
            line = line.strip()
            if '#' in line:
                line, comment = line.split('#', 1)
            else:
                line = line.split()[0]
                comment = line
            buttons.append([line, comment.strip()])
        else:
            raise Exception("Malformed remote configuration")
    return buttons


def press_ir_button(remote, button):
    cmd = subprocess.Popen(
        ['irsend', 'SEND_ONCE', remote, button],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = cmd.communicate()
    if len(stderr) > 0 or cmd.returncode > 0:
        raise Exception(stderr)


def get_list_of_macros():
    if not os.path.exists(MACRO_CONF_DIR):
        os.mkdir(MACRO_CONF_DIR)
    elif not os.path.isdir(MACRO_CONF_DIR):
        raise Exception("Incorrect MACRO_CONF_DIR configuration")
    macros = []
    for item in os.listdir(MACRO_CONF_DIR):
        if '.json' not in item:
            continue
        macros.append(item.split('.json')[0])
    return macros


def get_macro_definition(macro_name):
    macrolist = get_list_of_macros()
    macro_fn = "{}.json".format(macro_name)
    if macro_fn not in macrolist:
        raise Exception("Macro undefined")
    with open(os.path.join(MACRO_CONF_DIR, macro_fn), 'r') as f:
        return json.load(f)


def set_macro_definition(macro_json, macro_name=None):
    ds_name = macro_json.keys()[0]
    if macro_name is None:
        macro_name = ds_name
    macro_fn = "{}.json".format(macro_name)
    with open(os.path.join(MACRO_CONF_DIR, macro_fn), 'w') as f:
        json.dump(macro_json[ds_name], f)


def remove_macro_definition(macro_name):
    os.remove(os.path.join(
        MACRO_CONF_DIR,
        "{}.json".format(macro_name)
    ))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/wss')
def websockets():
    return render_template('wss.html')


@app.route('/api/')
def api_versions():
    return jsonify(v1=url_for('api_v1'))


@app.route('/api/v1/')
def api_v1():
    endpoints = {}
    endpoints[url_for('api_v1_plate')] = 'plate'
    endpoints[url_for('api_v1_ir')] = 'ir'
    return jsonify(**endpoints)


@app.route('/api/v1/pause')
def pause():
    pause_time = request.args.get('time')
    if pause_time is None:
        pause_time = 1
    time.sleep(pause_time)
    return jsonify(status="ok")


@app.route('/api/v1/plate/')
def api_v1_plate():
    endpoints = {}
    for relay_plate in get_list_of_relay_plates():
        endpoints[url_for(
            'api_v1_plate_num',
            plate_num=relay_plate
        )] = relay_plate
    return jsonify(**endpoints)


@app.route('/api/v1/plate/<int:plate_num>/')
def api_v1_plate_num(plate_num):
    try:
        relay_status = get_state_of_relays_on_plate(plate_num)
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    plate_conf = load_relay_plate_conf(plate_num)
    plate_name = request.args.get('name')
    if plate_name is None:
        plate_name = plate_conf['name']
    else:
        plate_conf['name'] = plate_name
        save_relay_plate_conf(plate_num, plate_conf)
    endpoints = {'name': plate_name}
    for relay_num, state in relay_status.items():
        endpoints[url_for(
            'api_v1_plate_num_relay_set',
            plate_num=plate_num,
            relay_num=relay_num
        )] = {
            'state': state,
            'name': plate_conf['relay_{}'.format(relay_num)]
        }
    return jsonify(**endpoints)


@app.route('/api/v1/plate/<int:plate_num>/toggleleds')
def api_v1_plate_num_toggle_leds(plate_num):
    try:
        toggle_leds_on_plate(plate_num)
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    return jsonify(status="ok")


@app.route('/api/v1/plate/<int:plate_num>/<int:relay_num>/')
@app.route('/api/v1/plate/<int:plate_num>/<int:relay_num>/<state>')
def api_v1_plate_num_relay_set(plate_num, relay_num, state=None):
    try:
        relay_status = get_state_of_relays_on_plate(plate_num)
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    if relay_num not in relay_status.keys():
        return make_response(jsonify(err="Relay is invalid"), 403)
    if state is None:
        state = request.args.get('state')
    if state not in ['off', 'on', 'toggle', None]:
        return make_response(jsonify(err="State is invalid"), 403)
    plate_conf = load_relay_plate_conf(plate_num)
    relay_name = request.args.get('name')
    if relay_name is None:
        relay_name = plate_conf['relay_{}'.format(relay_num)]
    else:
        plate_conf['relay_{}'.format(relay_num)] = relay_name
        save_relay_plate_conf(plate_num, plate_conf)
    curr_relay_state = relay_status[relay_num]
    if ((curr_relay_state == 'on' and state == 'off')
            or (curr_relay_state == 'off' and state == 'on')
            or state == 'toggle'):
        curr_relay_state = toggle_state_of_relay(plate_num, relay_num)
    return jsonify(state=curr_relay_state, name=relay_name)


@app.route('/api/v1/ir/')
def api_v1_ir():
    endpoints = {}
    endpoints[url_for('api_v1_ir_macro')] = 'macro'
    endpoints[url_for('api_v1_ir_remote')] = 'remote'
    endpoints[url_for('api_v1_irrecord_buttons')] = 'irrecord_buttons'
    return jsonify(**endpoints)


@app.route('/api/v1/ir/irrecord_buttons')
def api_v1_irrecord_buttons():
    try:
        buttons = get_list_of_buttons_for_irrecord()
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    return jsonify(buttons=buttons)


@app.route('/api/v1/ir/macro/', methods=['GET', 'PUT'])
def api_v1_ir_macro():
    if request.method == 'PUT':
        try:
            set_macro_definition(request.get_json())
        except Exception as ex:
            return make_response(jsonify(err=str(ex)), 403)
    try:
        macrolist = get_list_of_macros()
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    macros = {}
    for macro in macrolist:
        macros[url_for(
            'api_v1_ir_macro_name',
            macro_name=macro
        )] = macro
    return jsonify(**macros)


@app.route('/api/v1/ir/macro/<macro_name>/', methods=['GET', 'POST', 'DELETE'])
@app.route('/api/v1/ir/macro/<macro_name>/<state>')
def api_v1_ir_macro_name(macro_name, state=None):
    if request.method == 'POST':
        try:
            set_macro_definition(request.get_json(), macro_name)
        except Exception as ex:
            return make_response(jsonify(err=str(ex)), 403)
    try:
        macro = get_macro_definition(macro_name)
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    if request.method == 'DELETE':
        try:
            remove_macro_definition(macro_name)
        except Exception as ex:
            return make_response(jsonify(err=str(ex)), 403)
        return jsonify(status="ok")
    if state is None:
        state = request.args.get('state')
    if state not in ['pressed', 'on', None]:
        return make_response(jsonify(err="State is invalid"), 403)
    if state in ['pressed', 'on']:
        for url in macro:
            func, args = flask_from_url.from_url(url)
            func(**args)
    formatted_macro = {}
    formatted_macro[macro_name] = macro
    return jsonify(**formatted_macro)


@app.route('/api/v1/ir/remote/', methods=['GET', 'PUT'])
def api_v1_ir_remote():
    if request.method == 'PUT':
        try:
            set_remote_definition(request.get_json())
        except Exception as ex:
            return make_response(jsonify(err=str(ex)), 403)
    try:
        remotelist = get_list_of_remotes()
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    remotes = {}
    for remote in remotelist:
        remotes[url_for(
            'api_v1_ir_remote_remote_name',
            remote_name=remote
        )] = remote
    return jsonify(**remotes)


@app.route('/api/v1/ir/remote/<remote>/', methods=['GET', 'POST', 'DELETE'])
def api_v1_ir_remote_remote_name(remote):
    if request.method == 'POST':
        try:
            set_remote_definition(request.get_json(), remote)
        except Exception as ex:
            return make_response(jsonify(err=str(ex)), 403)
    try:
        buttonlist = get_list_of_remote_buttons(remote)
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    if request.method == 'DELETE':
        try:
            remove_remote_definition(remote)
        except Exception as ex:
            return make_response(jsonify(err=str(ex)), 403)
        return jsonify(status="ok")
    buttons = {}
    for button in buttonlist:
        buttons[url_for(
            'api_v1_ir_remote_remote_button',
            remote=remote,
            button=button[0]
        )] = button[1]
    return jsonify(**buttons)


@app.route('/api/v1/ir/remote/<remote>/<button>/')
@app.route('/api/v1/ir/remote/<remote>/<button>/<state>')
def api_v1_ir_remote_remote_button(remote, button, state=None):
    try:
        buttonlist = get_list_of_remote_buttons(remote)
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    if button not in [x[0] for x in buttonlist]:
        return make_response(jsonify(err="Button not defined"), 403)
    if state is None:
        state = request.args.get('state')
    if state not in ['pressed', 'on', None]:
        return make_response(jsonify(err="State is invalid"), 403)
    if state in ['pressed', 'on']:
        try:
            press_ir_button(remote, button)
        except Exception as ex:
            return make_response(jsonify(err=str(ex)), 403)
    button_status = {}
    for x in buttonlist:
        if x[0] == button:
            button_status['button'] = x[0]
            button_status['name'] = x[1]
    return jsonify(**button_status)


@socketio.on('start irrecord', namespace='/irrecord')
def start_irrecord(message):
    print(message)
    emit('irrecord output', {'data': message['data']})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
