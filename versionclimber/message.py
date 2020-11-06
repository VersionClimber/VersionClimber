""" Message to communicate btw client / server.

TODO: Add client id to log info from server.
"""
class Message(object):
    def __init__(self, category, content=None):
        self.category = category
        self.content = content

    def __str__(self):
        return ': '.join(self.category, self.content)

