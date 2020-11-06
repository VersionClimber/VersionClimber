import zmq
from versionclimber import config

from message import Message

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:50008")

# 1st step: Request the configuration
m = Message('request', 'config')
socket.send_pyobj(m)
data = socket.recv_pyobj()

if data.category == 'send_config':
    print('Receive config')
    config_stream = data.content
    conf = config.load_config_from_stream(config_stream)
    print(conf)
else:
    print('Error', data)

m = Message('request', 'work')
socket.send_pyobj(m)
data = socket.recv_pyobj()

# Several cases:
# Either receive request on
# - package versions
# - work

