""" Start a client
Run
Stop
"""

import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.DEALER)
socket.connect("tcp://localhost:5555")

# First subscribe to the server
socket.send_multipart([b'', b'Register to Coordinator'])

# Receive assignment
empty, response = socket.recv_multipart()
if response.startswith(b'ASSIGNED:'):
    client_id = response.decode().split(':', 1)[1]
    print(f"Received ID from server: {client_id}")


#  Do 10 requests, waiting each time for a response
for request in range(10):
    print(f"Sending request {request} …")
    socket.send_multipart([b'', b'Hello'])

    #  Get the reply.
    _, reply = socket.recv_multipart()
    msg = reply.decode()
    print(f"Received reply {request}: {msg} ")

# End client
socket.send_multipart([b'', b'Finish'])