# client
import zmq
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:50008")

slaveid = 1
slaveidstring = str(slaveid) + " "
currentindex = -1

print(slaveidstring, "requestwork ", currentindex)
socket.send(b'request:' + slaveidstring + 'requestwork ' + str(currentindex))
data = socket.recv()