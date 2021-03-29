import os
import json
import pprint

from flask import Flask, request, url_for
from signalwire.voice_response import VoiceResponse, Gather

app = Flask(__name__)

with open('configure.json') as f:
    ccConfig = json.load(f)
    # Dump config to console, for debugging
    pprint.pprint(ccConfig)

HOSTNAME = ccConfig['settings']['hostname']
SIGNALWIRE_SPACE = ccConfig['signalwire']['space']
SIGNALWIRE_PROJECT = ccConfig['signalwire']['project']
SIGNALWIRE_TOKEN = ccConfig['signalwire']['token']


@app.route('/get_menu', methods=['GET', 'POST'])
def get_menu():
    response = VoiceResponse()

    # read menus from config
    menus = ccConfig['settings']['menus']

    # check to see if a default menu was specified, else default to "main"
    menu = request.values.get("menu")
    if menu not in menus:
        menu = "main"

    # read input_type variable
    input_type = request.values.get("input_type")

    # check if user input was provided via dtmf entry
    if input_type == "dtmf":
        # get digits pressed at menu
        digits = request.values.get("Digits")
        input_action = menus[menu][digits]["action"]
        response.redirect(url=input_action)
        response.hangup()
    else:
        # no user input was detected, so lets present a menu
        gather = Gather(action='/get_menu' + "?menu=" + menu, input='dtmf', timeout="5", method='POST', numDigits="1")

        # loop through menus and generate menu options
        for key in menus[menu]:
            print(key, '->', menus[menu][key]["verbiage"])
            gather.say(menus[menu][key]["verbiage"])

        # add menu to response
        response.append(gather)
        response.hangup()

    # return response
    return str(response)


@app.route("/transfer_call", methods=['POST', 'GET'])
def transfer_call():
    response = VoiceResponse()
    farward_to = ccConfig['settings']['callTransferTo_']
    # print(farward_to)
    response.say("please wait your call is connecting....")
    response.dial(farward_to, action=url_for('quit_call'))
    print(farward_to)
    return str(response)


@app.route("/connect_dgf", methods=['POST', 'GET'])
def connect_dgf():
    response = VoiceResponse()
    farward_to = ccConfig['settings']['GDF_connection']
    # print(farward_to)
    response.dial(farward_to, action=url_for('quit_call'))
    # print(farward_to)
    return str(response)


@app.route('/quit_call', methods=['GET', 'POST'])
def quit_call():
    response = VoiceResponse()
    response.say('Thank you for calling Eagle.net')
    response.hangup()
    return str(response)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
