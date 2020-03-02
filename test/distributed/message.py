class Message(object):
    def __init__(self, category, content):
        self.category = category
        self.content = content

    def __str__(self):
        return ': '.join(self.category, self.content)

