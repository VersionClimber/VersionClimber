# server
import zmq
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:50008")


statusarray = ['undone' for n in range(len(configarray))]

currentindex = 0
foundbestanchor = False
successfound = False # if some slave returns success then this is set to True
successindex = float('inf')

############################
data = self.socket.recv()
fields = data.split(" ")

ret = [-1, currentindex, configarray[currentindex]]
