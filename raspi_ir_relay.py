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

from flask import Flask, url_for, jsonify, make_response, render_template, json
import flask_from_url
import os
import subprocess
TESTING = True
DEBUG = True
REMOTE_CONF_DIR = '/etc/lirc/lirc.conf.d'
MACRO_CONF_DIR = 'macros'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('RASPI_IR_RELAY_SETTINGS', silent=True)

if TESTING:
    import testingRELAYplate as RELAY
else:
    import piplates.RELAYplate as RELAY

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


def get_list_of_relay_plates():
    plates = []
    i = 0
    for plate in RELAY.relaysPresent:
        if plate == 1:
            plates.append(i)
        i += 1
    return plates


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


def get_list_of_remotes():
    if not os.path.exists(REMOTE_CONF_DIR):
        os.mkdir(REMOTE_CONF_DIR)
    elif not os.path.isdir(REMOTE_CONF_DIR):
        raise Exception("Incorrect REMOTE_CONF_DIR configuration")
    remotes = []
    for item in os.listdir(REMOTE_CONF_DIR):
        if '.conf' not in item:
            continue
        remotes.append(item.split('.conf')[0])
    return remotes


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


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/api')
def api_versions():
    return jsonify(v1=url_for('api_v1'))


@app.route('/api/v1')
def api_v1():
    # return jsonify(relay_plates=get_list_of_relay_plates(), remote=get_lirc)
    endpoints = {}
    endpoints[url_for(api_v1_plate)] = 'plate'
    endpoints[url_for(api_v1_ir)] = 'ir'
    return jsonify(**endpoints)


@app.route('/api/v1/plate')
def api_v1_plate():
    endpoints = {}
    for relay_plate in get_list_of_relay_plates():
        endpoints[url_for(
            'api_v1_plate_num',
            plate_num=relay_plate
        )] = relay_plate
    return jsonify(**endpoints)


@app.route('/api/v1/plate/<int:plate_num>')
def api_v1_plate_num(plate_num):
    try:
        relay_status = get_state_of_relays_on_plate(plate_num)
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    endpoints = {}
    for relay_num, state in relay_status.items():
        endpoints[url_for(
            'api_v1_plate_num_relay_set',
            plate_num=plate_num,
            relay_num=relay_num
        )] = state
    return jsonify(**endpoints)


@app.route('/api/v1/plate/<int:plate_num>/toggleleds')
def api_v1_plate_num_toggle_leds(plate_num):
    try:
        toggle_leds_on_plate(plate_num)
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    return jsonify(status="ok")


@app.route('/api/v1/plate/<int:plate_num>/<int:relay_num>')
@app.route('/api/v1/plate/<int:plate_num>/<int:relay_num>/<state>')
def api_v1_plate_num_relay_set(plate_num, relay_num, state=None):
    try:
        relay_status = get_state_of_relays_on_plate(plate_num)
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    if relay_num not in relay_status.keys():
        return make_response(jsonify(err="Relay is invalid"), 403)
    if state not in ['off', 'on', 'toggle', None]:
        return make_response(jsonify(err="State is invalid"), 403)
    curr_relay_state = relay_status[relay_num]
    if ((curr_relay_state == 'on' and state == 'off')
            or (curr_relay_state == 'off' and state == 'on')
            or state == 'toggle'):
        curr_relay_state = toggle_state_of_relay(plate_num, relay_num)
    return jsonify(state=curr_relay_state)


@app.route('/api/v1/ir')
def api_v1_ir():
    endpoints = {}
    endpoints[url_for('api_v1_ir_macro')] = 'macro'
    endpoints[url_for('api_v1_ir_remote')] = 'remote'
    return jsonify(**endpoints)


@app.route('/api/v1/ir/macro')
def api_v1_ir_macro():
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


@app.route('/api/v1/ir/macro/<macro_name>')
@app.route('/api/v1/ir/macro/<macro_name>/<state>')
def api_v1_ir_macro_name(macro_name, state=None):
    try:
        macro = get_macro_definition(macro_name)
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    if state not in ['pressed', 'on', None]:
        return make_response(jsonify(err="State is invalid"), 403)
    if state in ['pressed', 'on']:
        for url in macro:
            func, args = flask_from_url.from_url(url)
            func(**args)
    return jsonify()


@app.route('/api/v1/ir/remote')
def api_v1_ir_remote():
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


@app.route('/api/v1/ir/remote/<remote_name>')
def api_v1_ir_remote_remote_name(remote_name):
    try:
        buttonlist = get_list_of_remote_buttons(remote_name)
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    buttons = {}
    for button in buttonlist:
        buttons[url_for(
            'api_v1_ir_remote_remote_button',
            remote=remote_name,
            button=button[0]
        )] = button[1]
    return jsonify(**buttons)


@app.route('/api/v1/ir/remote/<remote>/<button>')
@app.route('/api/v1/ir/remote/<remote>/<button>/state')
def api_v1_ir_remote_remote_button(remote, button, state=None):
    try:
        buttonlist = get_list_of_remote_buttons(remote)
    except Exception as ex:
        return make_response(jsonify(err=str(ex)), 403)
    if button not in [x[0] for x in buttonlist]:
        return make_response(jsonify(err="Button not defined"), 403)
    if state not in ['pressed', 'on', None]:
        return make_response(jsonify(err="State is invalid"), 403)
    if state in ['pressed', 'on']:
        cmd = subprocess.Popen(
            ['irsend', 'SEND_ONCE', remote, button],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        cmd.wait()
    button_status = {}
    for x in buttonlist:
        if x[0] == button:
            button_status['button'] = x[0]
            button_status['name'] = x[1]
    return jsonify(**button_status)


if __name__ == '__main__':
        app.run(host='0.0.0.0')
