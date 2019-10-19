import sys
import os
import planetproj
import queue
import threading

# Add the path to use planetproj module
# sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../planetproj_progs/host/')

import logging
logger = logging.getLogger(__name__)

class UnitController:
    def __init__(self, dry_run=False):
        if dry_run:
            logger.warning('dry_run is True')

        self.north = 0
        self.south = 1

        self.state = [None] * 2

        self.north_board_addr = planetproj.planetproj.ADDR_LED_1
        self.south_board_addr = planetproj.planetproj.ADDR_LED_2

        self.actions_queue = [None] * 2
        self.actions_queue[self.north] = queue.Queue()
        self.actions_queue[self.south] = queue.Queue()

        self.leds_num = 12
        self.leds_range = [None] * 2
        self.leds_range[self.north] = range(0,6)
        self.leds_range[self.south] = range(6,12)
        self.isKilled = False

        self.init_thread = [None] * 2
        self.init_thread[self.north] = threading.Thread(target=self.init_manager, args=[self.north, dry_run])
        self.init_thread[self.north].name = "NorthUnitInitThread"
        self.init_thread[self.south] = threading.Thread(target=self.init_manager, args=[self.south, dry_run])
        self.init_thread[self.south].name = "SouthUnitInitThread"

        self.worker = [None] * 2
        self.worker[self.north] = threading.Thread(target=self.unit_mng_worker, args=[self.north, dry_run])
        self.worker[self.north].name = "NorthUnitThread"
        self.worker[self.south] = threading.Thread(target=self.unit_mng_worker, args=[self.south, dry_run])
        self.worker[self.south].name = "SouthUnitThread"

        self.unit_manager = [None] * 2


    def start(self):
        for init_t in self.init_thread:
            init_t.start()

        for init_t in self.init_thread:
            init_t.join()

        for t in self.worker:
            t.start()
            logger.info("start worker in {}".format(t.name))
        return self

    def end(self):
        self.isKilled = True
        for q in self.actions_queue:
            q.put(None)
        for t in self.worker:
            t.join()
        logger.info('close')

    def __enter__(self):
        self.start()

    def __exit__(self):
        self.end()

    def unit_mng_worker(self, axis, dry_run):
        while not self.isKilled:
            logger.info("queue is ready")
            received_action = self.actions_queue[axis].get()
            if received_action is None:
                logger.info("close worker")
                break;
            logger.info('running' + str(received_action[0]) + ' args: ' + str(received_action[1]))
            received_action[0](*received_action[1])
            self.actions_queue[axis].task_done()

    def init_manager(self, axis, dry_run):
        try:
            manager = planetproj.LED(
                addrs = [self.north_board_addr, self.south_board_addr],
                num_leds_per_dev = 6,
                dry_run=dry_run)
            self._init_unit(manager, axis)
            self.unit_manager[axis] = manager
        except FileNotFoundError as e:
            logger.error('i2c is not connected')
            sys.exit()
        except Exception as e:
            raise

    def _init_unit(self, manager, axis):
        logger.info('initilize unit')
        self.change_state(axis, 'try-init')

        manager.set_brightness_multi([(i, 0) for i in self.leds_range[axis]])
        self.change_state(axis, 'initialized')

    def _set_brightness_multi(self, ary):
        north_value = [ (item[0], item[1]) for item in ary if item[0] < 6]
        south_value = [ (item[0], item[1]) for item in ary if item[0] >= 6]
        if len(north_value) > 0:
            logger.debug(north_value)
            self.actions_queue[self.north].put((self.unit_manager[self.north].set_brightness_multi, [north_value]))
        if len(south_value) > 0:
            logger.debug(south_value)
            self.actions_queue[self.south].put((self.unit_manager[self.south].set_brightness_multi, [south_value]))
        # self.leds.set_brightness_multi(ary)

    def set_brightness(self, ledid, brightness):
        try:
            n = int(ledid)
            b = float(brightness)
        except TypeError:
            e = 'ledid(={}) and brightness(={}) is expected int or float'.format(type(ledid), type(brightness))
            logger.error(e)
            return (ledid, None, e);

        try:
            self._set_brightness_multi([(n, b)])
        except OSError as error:
            e = 'cannot write devices'
            logger.error(e)
            return (ledid, None, e);
        except ValueError:
            raise
        return (ledid, '', None)

    def get_brightness(self, ledid):
        self.change_state('active')
        b = self.leds.get_brightness(ledid)
        self.change_state('non-active')
        return (ledid, b)

    def set_multi_brightness(self, brightness_ary):
        self._set_brightness_multi(brightness_ary)
        return [(0,0,0)]

    def get_all_brightness(self):
        result_dict = {}
        for ledid in range(0, self.leds_num):
            result_dict[ledid] =  self.leds.get_brightness(ledid)
        return result_dict

    def change_state(self, axis, state):
        pre_ra, pre_dec = self.state
        self.state[axis] = state
        logger.debug('The state  has changed: {} -> {}'.format([pre_ra, pre_dec], self.state))

    def shutdown(self):
        self.change_state('try-exit')
        try:
            self.leds.set_brightness_multi([ (p, 0) for p in range(0, len(self.ledids)) ])
        except ValueError as e:
            error_message = ' {} in shutdown'.format(e.message)
            raise ValueError(error_message)
        self.change_state('exited')

if __name__ == '__main__':
    import time

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s:%(threadName)s:%(name)s:%(levelname)s:%(message)s')
    m = UnitController(dry_run=True)
    m.start()
    m.set_multi_brightness([(i,0.5) for i in range(0,12)])
    m.end()
