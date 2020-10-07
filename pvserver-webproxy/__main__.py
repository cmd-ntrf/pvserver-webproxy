import getpass
import socket
import subprocess
import sys

import tornado.ioloop
import tornado.web

import threading

from contextlib import closing
from subprocess import Popen, PIPE, STDOUT

# https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

class CommandThread(threading.Thread):
    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd
        self.lines = []

    def run(self):
        self.proc = Popen(self.cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        while self.proc:
            self.lines.append(self.proc.stdout.readline())

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        machine_name = self.request.host
        machine_name = machine_name.split(':')[0]
        if machine_name != "localhost":
            machine_name = ".".join(machine_name.split('.')[1:])
        self.render("template.html", 
                    title="Paraview Server",
                    username=getpass.getuser(),
                    machine_name=machine_name,
                    hostname=socket.getfqdn(),
                    port=PARAVIEW_PORT,
                    version=PARAVIEW_VERSION,
                    lines=thread.lines)

class StopHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Stopping ParaView Server...')
        if '/user' in self.request.uri:
            self.redirect('/hub/home')
        self.finish()
        tornado.ioloop.IOLoop.current().stop()

if __name__ == "__main__":
    WEBSERVER_PORT = sys.argv[1]
    app = tornado.web.Application([(r"/", MainHandler), (r"/stop", StopHandler),])
    app.listen(WEBSERVER_PORT)

    PARAVIEW_PORT = find_free_port()
    PARAVIEW_VERSION = subprocess.check_output(['pvserver', '--version']).split()[-1]
    thread = CommandThread(['paraview-mesa', 'pvserver', '--backend', 'swr', '--', '--server-port={}'.format(PARAVIEW_PORT)])
    thread.daemon = True
    thread.start()

    tornado.ioloop.IOLoop.current().start()
