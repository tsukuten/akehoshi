import logging

logger = logging.getLogger(__name__)

import Controller
import Generator


class Listener:
    def __init__(self, logger=logging.getLogger(__name__)):
        self.controllers = dict()
        self.logger = logger

    def enqueue(self, target, action):
        is_success = self.controllers[target].enqueue(action)
        if is_success:
            self.logger.info("success")
        else:
            self.logger.warning("fail")

    def register_controller(self, controller: Controller):
        self.controllers.append(controller)
        return controller.id

    def unregister_controller(self, controller_id):
        del self.controllers[controller_id]

    def register_generator(self, generator: Generator):
        self.generators.append(generator)

    def get_controllers(self, id=False):
        if id:
            return [controller.id for controller in self.controllers]
        else:
            return [controller for controller in self.controllers]

