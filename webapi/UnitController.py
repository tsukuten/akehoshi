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

        self.action_queue = [None] * 2
        self.action_queue[self.north] = queue.Queue()
        self.action_queue[self.south] = queue.Queue()

        self.leds_num = 12
        self.isKilled = False

        self.init_thread = [None] * 2
        self.init_thread[self.north] = threading.Thread\
            (target=self.init_unit, args=[self.nort], kwargs={"dry_run":dry_run})
        self.init_thread[self.north].name = "NorthUnitInitThread"
        self.init_thread[self.south] = threading.Thread \
            (target=self.init_unit, args=[self.south], kwargs={"dry_run":dry_run})
        self.init_thread[self.south].name = "SouthUnitInitThread"

        self.worker = [None] * 2
        self.worker[self.north] = threading.Thread\
            (target=self.unit_mng_worker, args=[self.north, dry_run])
        self.worker[self.north].name = "NorthUnitThread"
        self.worker[self.south] = threading.Thread \
            (target=self.unit_mng_worker, args=[self.south, dry_run])
        self.worker[self.south].name = "SouthUnitThread"


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

    def unit_mng_woker(self, axis, dry_run):
        while not self.isKilled:
            received_action = self.actions_queue[axis].get()
            if received_action is None:
                logger.info("close worker")
                break;
            received_action[0](*received_action[1])
            self.actions_queue[axis].task_done()

    def init_manager(self, axis, dry_run):
        try:
            manager = planetproj.LED(
                addrs = [self.north_board_addr, self.south_board_addr],
                num_leds_per_dev = 6,
                dry_run=dry_run)
            manager._init_unit(manager, axis)
            self.unit_manager[axis] = manager
        except FileNotFoundError as e:
            logger.error('i2c is not connected')
            sys.exit()
        except Exception as e:
            raise

    def _init_unit(self, manager, axis):
        logger.info('initilize unit')
        self.change_state(axis, 'try-init')
        manager.set_brightness_multi([0,0,0,0,0,0])
        self.change_state(axis, 'initialized')

    def _set_brightness_multi(self, ary):
        self.leds.set_brightness_multi(ary)

    def set_brightness(self, ledid, brightness):
        self.change_state('active')
        try:
            n = int(ledid)
            b = float(brightness)
        except TypeError:
            e = 'ledid(={}) and brightness(={}) is expected int or float'.format(type(ledid), type(b))
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
        res = self.leds.get_brightness(n)
        self.change_state('non-active')
        return (ledid, res, None)

    def get_brightness(self, ledid):
        self.change_state('active')
        b = self.leds.get_brightness(ledid)
        self.change_state('non-active')
        return (ledid, b)

    def set_multi_brightness(self, brightness_dict):
        send_array = []
        for ledid in brightness_dict.keys():
                (l, b, e) = self.set_brightness(ledid, brightness_dict[ledid])
                # send_dict[str(l)] = (b, e)
                send_array.append((l, b, e))
        return send_array

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
