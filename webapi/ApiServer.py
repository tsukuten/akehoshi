import sys,os

from flask import Flask, jsonify, abort, make_response,request
from flask_cors import CORS
import logging
from math import pi
import json

from MotorController import MotorController
from UnitController import UnitController

from logging import getLogger

api = Flask(__name__)
api.interface_error = [ValueError, TypeError]
CORS(api)


unit = None
motor = None

@api.route('/leds/<int:ledId>', methods=['GET'])
def get_leds_info(ledId):
    global unit
    ret = unit.get_brightness(ledId)
    result = {
        "result": True,
        "ledId": ret[0],
        "brightness": ret[1]
    }
    return make_response(jsonify(result))

# # // Example of JSON to handle
# # { "brightness" : 0.3 }
@api.route('/leds/<int:ledId>', methods=['POST'])
def set_leds(ledId):
    global unit
    if request.headers['Content-Type'] != 'application/json':
        return (jsonify(error=True, mes='Content-Type is not match, expected \'application/json\'({})'.format(request.headers['Content-Type'])), 400)
    obj = json.loads(request.data.decode('utf-8'))
    led = unit.set_brightness(ledId, obj['brightness'])
    result = {
        "result": True,
        "ledId": ledId,
        "brightness": led[1]
    }
    return make_response(jsonify(result))

@api.route('/leds/all', methods=['GET'])
def get_leds_all():
    global unit
    result = {
        'result': True,
        'brightness': unit.get_all_brightness()
    }
    return jsonify(result)

# // Example of JSON to handle
# { "brightness": {"1":0 ,"3":0.07,"9":0.11} }

@api.route('/leds/all', methods=['POST'])
def set_leds_all():
    global unit
    if request.headers['Content-Type'] != 'application/json':
        return (jsonify(error=True, mes='Content-Type is not match, expected \'application/json\'({})'.format(request.headers['Content-Type'])), 400)
    print(request.data)
    print(json.loads(request.data.decode('utf-8')))
    obj = json.loads(request.data.decode('utf-8'))
    result_array = unit.set_multi_brightness(obj['brightness'])
    error_array = { res[0]:res[2] for res in result_array }
    result = {
        "result" : True,
        "brightness": { res[0]:res[1] for res in result_array },
        "error": error_array
    }
    return jsonify(result)

@api.route('/ra', methods=['POST'])
def set_ra():
    global motor
    if request.headers['Content-Type'] != 'application/json':
        return (jsonify(error=True, mes='Content-Type is not match, expected \'application/json\'({})'.format(request.headers['Content-Type'])), 400)
    print('ra_pos = {}'.format(request.data))
    data = json.loads(request.data.decode('utf-8'));
    ra_pos = motor.move_ra_absolute(data["position"])
    result = {
        "result" : True,
        "position": data["position"]
    }
    return jsonify(result)

@api.route('/dec', methods=['POST'])
def set_dec():
    global motor
    if request.headers['Content-Type'] != 'application/json':
        return (jsonify(error=True, mes='Content-Type is not match, expected \'application/json\'({})'.format(request.headers['Content-Type'])), 400)
    data = json.loads(request.data.decode('utf-8'));
    dec_pos = motor.move_dec_absolute(data["position"])
    result = {
        "result" : True,
        "position": data["position"]
    }
    return jsonify(result)

@api.errorhandler(500)
def error_handler(error):
    type = "undefined"
    type = 'FaitalError'
    for e in api.interface_error:
        if isinstance(error , e):
            type = 'InterfaceError'
    return (jsonify(type=type, message = error.args[0], error=True), 200)

@api.errorhandler(400)
def notfound_handler(a):
    print(a)
    return (jsonify(type='', mes="notfound", error=True), 400)

def run(host, port, dry_run=False):
    print('run')
    global unit
    unit = UnitController(dry_run=dry_run)
    # motor = MotorController(dry_run=dry_run)
    api.run(host=host, port=port)
