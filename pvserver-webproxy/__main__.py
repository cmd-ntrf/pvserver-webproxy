import getpass
import socket
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
        p = Popen(self.cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        while True:
            self.lines.append(p.stdout.readline())

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        machine_name = self.request.host
        machine_name = machine_name.split(':')[0]
        if machine_name != "localhost":
            machine_name = "".join(machine_name.split('.')[1:])
        self.render("template.html", 
                    title="Paraview Server",
                    username=getpass.getuser(),
                    machine_name=machine_name,
                    hostname=socket.getfqdn(),
                    port=PARAVIEW_PORT,
                    lines=thread.lines)

if __name__ == "__main__":
    WEBSERVER_PORT = sys.argv[1]
    app = tornado.web.Application([(r"/", MainHandler),])
    app.listen(WEBSERVER_PORT)

    PARAVIEW_PORT = find_free_port()
    thread = CommandThread(['paraview-mesa', 'pvserver', '--backend', 'swr', '--', '--server-port={}'.format(PARAVIEW_PORT)])
    thread.start()

    tornado.ioloop.IOLoop.current().start()
