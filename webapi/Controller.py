import logging
import uuid

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, name):
        self.name = name
        self.id = uuid.uuid4()

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id

    def execute(self, event_name, arguments):
        pass
