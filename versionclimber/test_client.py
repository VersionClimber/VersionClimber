import zmq
from versionclimber import config

from message import Message

context = zmq.Context()
socket = context.socket(zmq.REQ)
# TODO: move connection to cloud ip addr
socket.connect("tcp://localhost:50008")


#########################################
# Configuration
#########################################

# 1st step: Request the configuration
m = Message('request_config', '')
socket.send_pyobj(m)

conf = None
pkg_names = []
data = socket.recv_pyobj()

if data.category == 'send_config':
    print('Receive config')
    conf = data.content
    print(conf)
    # TODO : Activate configuration
    pkg_names = [pkg.name for pkg in self.pkgs]
else:
    print('Error: no config received', data)

while True:
    m = Message('request_work', '')
    socket.send_pyobj(m)

    data = socket.recv_pyobj()

    # Several cases:
    # Either receive request on
    # - package versions
    # - send work

    if data.category == 'send_work':
        _pkgindex, _index, config_to_test = data.content

        semantic_config = [ (pkg_names[i], config_to_test[i]) for i in range(pkg_names)]
        status = tryconfig(semantic_config)
        _status = 'success' if status == 0 else 'fail'

        # CPL TODO: compute
        m = Message('update_status', [_pkgindex, _index, _status])
        socket.send_pyobj(m)

    elif data.category == 'send_config':
        print("Error: config already loaded")

    else:
        print("Error: no message %s allowed"%data.category)

