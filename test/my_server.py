#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#


""" Algorithm

Launch the server.

The agents will connect to the server and register themselves.  
Loop :
    -> AGENT : New Agents register with the server. 
    <- SERVER : The server will get the ID of each agent and store them as idle information (status). 
    
    -> AGENT : The agent will send a result to the server.
    <- SERVER : The server will receive the result, process it (solution?), timestamp the agent, and set its status to idle.

    -> SERVER : The server will request work to idle agents when work remain.
    <- AGENT : The agent receive the request and process it.
    The agent status is set to busy.


The server will wait for messages from the agents.

"""
from dataclasses import dataclass, field
from typing import Dict

import time
import zmq

server_address = "tcp://*:5555"

context = zmq.Context()
socket = context.socket(zmq.ROUTER)
socket.bind(server_address)

# Store agents with their status

agents : Dict[bytes, AgentInfo] = {} # identity (bytes) -> assigned_id
#idle_agents = []
#running_agents = []

agent_counter : int = 0

# Manage information
@dataclass
class AgentInfo:
    identity: bytes
    number: int
    last_seen: float
    status: str = field(default="idle") # idle, busy
    last_configuration: str = field(default="")
    def __repr__(self):
        return f"AgentInfo(identity={self.identity}, number={self.number}, last_seen={self.last_seen}, status={self.status}, last_configuration={self.last_message})"


print("Server started...")

agent_names = []

# Fake
works = [str(x) for x in range(10000)]

while works:
    #  Wait for next request from client
    #message = socket.recv()
    identity, empty, message = socket.recv_multipart()
    msg = message.decode()

    now = time.time()

    if identity not in agent_names:
        agent_counter += 1
        agents[identity] = AgentInfo(
            identity=identity,
            number=agent_counter,
            last_seen=now,
            status="idle",
            last_configuration=''
        )
        print(f"[NEW AGENT] {agents[identity]}")
    
    agent = agents[identity]
    agent.last_seen = now
    agent.status = 'idle'

    # Process the message/result from the agent

    idles = get_idle_agents()
    
    
    
    
def get_idle_agents():
    """
    Get the list of idle agents.
    """
    return [agent for agent in agents.values() if agent.status == 'idle']

def get_busy_agents():
    """
    Get the list of busy agents.
    """
    return [agent for agent in agents.values() if agent.status == 'busy']

"""
    else:
        msg = message.decode()
        print(f"Client {agent_names[identity]}: {msg}")
        time.sleep(1)

        if msg == 'Hello':
            #  Send reply back to client
            socket.send_multipart([identity, b'', b'World'])
        
        elif msg == 'Finish':
            print(f"Client {agent_names[identity]} finished.")
            socket.send_multipart([identity, b'', b'Goodbye'])
            del agent_names[identity]
            if not agent_names:
                print("All clients finished. Stopping server.")
                break

"""

