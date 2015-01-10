__author__ = 'mpesavento'

# add the shared settings file to namespace
import sys
import argparse
from os.path import dirname, abspath

sys.path.insert(0, dirname(dirname(abspath(__file__))))
import settings
from spacebrew.spacebrew import SpacebrewApp
import json
from websocket import create_connection


class SpacebrewClient(object):
    def __init__(self, name, server='127.0.0.1', port=9000):
        self.server = server
        self.port = port
        self.timestamp = 0

        # configure the spacebrew client
        self.brew = SpacebrewApp(name, server=server)
        self.osc_paths = [
            {'address': "/muse/eeg", 'arguments': 4},
            {'address': "/muse/eeg/quantization", 'arguments': 4},
            {'address': "/muse/eeg/dropped_samples", 'arguments': 1},
            {'address': "/muse/acc", 'arguments': 3},
            {'address': "/muse/acc/dropped_samples", 'arguments': 1},
            {'address': "/muse/batt", 'arguments': 4},
            {'address': "/muse/drlref", 'arguments': 2},
            {'address': "/muse/elements/low_freqs_absolute", 'arguments': 4},
            {'address': "/muse/elements/delta_absolute", 'arguments': 4},
            {'address': "/muse/elements/theta_absolute", 'arguments': 4},
            {'address': "/muse/elements/alpha_absolute", 'arguments': 4},
            {'address': "/muse/elements/beta_absolute", 'arguments': 4},
            {'address': "/muse/elements/gamma_absolute", 'arguments': 4},
            {'address': "/muse/elements/delta_relative", 'arguments': 4},
            {'address': "/muse/elements/theta_relative", 'arguments': 4},
            {'address': "/muse/elements/alpha_relative", 'arguments': 4},
            {'address': "/muse/elements/beta_relative", 'arguments': 4},
            {'address': "/muse/elements/gamma_relative", 'arguments': 4},
            {'address': "/muse/elements/delta_session_score", 'arguments': 4},
            {'address': "/muse/elements/theta_session_score", 'arguments': 4},
            {'address': "/muse/elements/alpha_session_score", 'arguments': 4},
            {'address': "/muse/elements/beta_session_score", 'arguments': 4},
            {'address': "/muse/elements/gamma_session_score", 'arguments': 4},
            {'address': "/muse/elements/touching_forehead", 'arguments': 1},
            {'address': "/muse/elements/horseshoe", 'arguments': 4},
            {'address': "/muse/elements/is_good", 'arguments': 4},
            {'address': "/muse/elements/blink", 'arguments': 1},
            {'address': "/muse/elements/jaw_clench", 'arguments': 1},
            {'address': "/muse/elements/experimental/concentration", 'arguments': 1},
            {'address': "/muse/elements/experimental/mellow", 'arguments': 1}
        ]

        self.ws = create_connection("ws://%s:%s" % (self.server, self.port))

        for path in self.osc_paths:
            spacebrew_name = path['address'].split('/')[-1]
            self.brew.add_subscriber(spacebrew_name, "string")
            self.brew.subscribe(spacebrew_name, self.handle_value)

    def handle_value(self, string_value):
        value = json.loads(string_value)
        path = value[0]
        splitpath = path.split('/')
        if splitpath[-1] is "alpha_relative":
            self.timestamp+=1
            value_out = [path] + [self.timestamp] + [(value[1]+value[2])/2]
            muse_id = "biodata_test"
            message = {"message": {
                "value": value_out,
                "type": "string", "name": "alpha_relative", "clientName": muse_id}}
            self.ws.send(json.dumps(message))


    def start(self):
        self.brew.start()


parser = argparse.ArgumentParser(
    description='Receive data from Spacebrew.')
parser.add_argument(
    '--name',
    help='Your name or ID without spaces or special characters',
    default='example')

if __name__ == "__main__":
    args = parser.parse_args()
    sb_client = SpacebrewClient('booth-%s' % args.name, settings.CLOUDBRAIN_ADDRESS)
    sb_client.start()
