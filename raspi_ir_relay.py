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

from flask import Flask, url_for, jsonify, make_response, render_template
TESTING = True
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('RASPI_IR_RELAY_SETTINGS', silent=True)

if TESTING:
    import testingRELAYplate as RELAY
else:
    import piplates.RELAYplate as RELAY


def get_list_of_relay_plates():
    plates = list(range(0, 9))
    for plate_num in plates:
        if RELAY.getADDR(plate_num) != plate_num:
            plates.remove(plate_num)
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
    for relay_plate in get_list_of_relay_plates():
        endpoints[url_for(
            'api_v1_plate_num',
            plate_num=relay_plate
        )] = relay_plate
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
        endpoints = {}
        for relay_num, state in relay_status.items():
            endpoints[url_for(
                'api_v1_plate_num_relay_set',
                plate_num=plate_num,
                relay_num=relay_num
            )] = state
        return jsonify(**endpoints)
    except Exception as ex:
        return make_response(jsonify(err=ex.message), 403)


@app.route('/api/v1/plate/<int:plate_num>/<int:relay_num>')
@app.route('/api/v1/plate/<int:plate_num>/<int:relay_num>/<state>')
def api_v1_plate_num_relay_set(plate_num, relay_num, state=None):
    if state not in ['off', 'on', 'toggle', None]:
        return make_response(jsonify(err="State is invalid"), 403)
    try:
        relay_status = get_state_of_relays_on_plate(plate_num)
    except Exception as ex:
        return make_response(jsonify(err=ex.message), 403)
    if relay_num not in relay_status.keys():
        return make_response(jsonify(err="Relay is invalid"), 403)
    curr_relay_state = relay_status[relay_num]
    if ((curr_relay_state == 'on' and state == 'off')
            or (curr_relay_state == 'off' and state == 'on')
            or state == 'toggle'):
        curr_relay_state = toggle_state_of_relay(plate_num, relay_num)
    return jsonify(state=curr_relay_state)


if __name__ == '__main__':
        app.run(host='0.0.0.0')
