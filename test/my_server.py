#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq


context = zmq.Context()
socket = context.socket(zmq.ROUTER)
socket.bind("tcp://*:5555")

id_map= {} # identity (bytes) -> assigned_id
id_counter = 0

print("Server started...")

while True:
    #  Wait for next request from client
    #message = socket.recv()
    identity, empty, message = socket.recv_multipart()

    if identity not in id_map:
        id_counter += 1
        assigned_id = f"client-{id_counter}"
        id_map[identity] = assigned_id
        print(f"Assigned {assigned_id} to {identity.hex()}")

        socket.send_multipart([identity, b'', f"ASSIGNED:{assigned_id}".encode()])
    else:
        msg = message.decode()
        print(f"Client {id_map[identity]}: {msg}")
        time.sleep(1)

        if msg == 'Hello':
            #  Send reply back to client
            socket.send_multipart([identity, b'', b'World'])
        
        elif msg == 'Finish':
            print(f"Client {id_map[identity]} finished.")
            socket.send_multipart([identity, b'', b'Goodbye'])
            del id_map[identity]
            if not id_map:
                print("All clients finished. Stopping server.")
                break

