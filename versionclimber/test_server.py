import zmq
from versionclimber import config
from message import Message

config_file = '../config.yaml'
cstream = open(config_file).read()
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:50008")

conf = config.load_config(config_file)
data = socket.recv_pyobj()

if data.category== 'request' and data.content == 'config':
    m = Message('send_config', cstream)
    socket.send_pyobj(m)

print(conf['packages'])
versions_to_compute = list(conf['packages'])
n= len(versions_to_compute)
versions = {}

# Work todo
while versions_to_compute:

    data = socket.recv_pyobj()
    if data.category == 'request':
        if data.content == 'work':
            pkg = versions_to_compute.pop()
            m = Message('request_version', pkg)
            socket.send_pyobj(m)
        elif data.content == 'config':
            m = Message('send_config', cstream)
            socket.send_pyobj(m)



    data = socket.recv_pyobj()

    data = socket.recv_pyobj()