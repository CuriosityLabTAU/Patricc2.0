#!/usr/bin/python
# -*- coding: utf-8 -*-
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from play_block import *
import threading
import json
import copy

# class that enables each request in a different thread
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


# class that handles the interaction with the frontend of the students
# parse requests.
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    previous_block = None
    current_block = None
    block_path = 'blocks/'
    sounds_path = 'sounds/'

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        BaseHTTPRequestHandler.end_headers(self)

    def log_message(self, format, *args):
        pass

    def do_GET(self): # action?parameters
        # parse the request path, converts %22 = ", to \'
        cmd = self.path[1:].split('?')
        if len(cmd) == 2:
            action = cmd[0]
            param = cmd[1]

            print(action, param)

            res = ''

            if action == 'set_paths':
                the_paths = param.split('|')
                self.block_path = the_paths[0]
                if len(the_paths) > 1:
                    self.sounds_path = the_paths[1]
                self.current_block = play_block()
                res = 'done'

            if action == 'run_block':
                res = self.run_block(param)

            if action == 'play_audio':
                res = self.play_audio(param)

            self.send_response(200)
            self.end_headers()
            if res != '':
                self.wfile.write(bytes(res, 'utf-8'))
            else:
                print('Is not defined: ', action, param)
                self.wfile.write(bytes('error', 'utf-8'))
        else:
            self.wfile.write(bytes('error', 'utf-8'))

    def run_block(self, param):
        self.current_block.load_block(self.block_path + param)
        if self.previous_block:
            new_motor_commands = self.current_block.stitch_blocks(block_before=self.previous_block)
            self.current_block.play_editted(motor_commands=new_motor_commands)
        else:
            self.current_block.play()
        return 'done'

    def play_audio(self, param):
        # get the length of the audio
        # find the right "explain" block
        # stitch the block and audio
        # play the block

        return 'done'

def start_student_server():
    httpd = ThreadedHTTPServer(('127.0.0.1', 3000), SimpleHTTPRequestHandler)
    print('started student http local server on port: ', 3000)
    httpd.serve_forever()

start_student_server()