import sys
import os
from math import pi
import planetproj
import threading
import queue

# Add the path to use planetproj module
# sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../planetproj_progs/host/')

import logging
logger = logging.getLogger(__name__)

class MotorController:
    def __init__(self, dry_run = False):
        if dry_run:
            logger.warning('dry_run is True')

        self.isKilled = False

        self.ra  = 1 #Rgiht Ascension(赤経)
        self.dec = 0 #DEClination(赤緯)

        self.state = [None] * 2
        self.range = [None] * 2

        self.range[self.ra]  = (-2*pi, 2*pi)
        self.range[self.dec] = (-pi, pi)
        self.actions_queue = [None] *2

        self.actions_queue[self.ra]  = queue.Queue()
        self.actions_queue[self.dec] = queue.Queue()

        self.motor_manager = [None] * 2

        self.pos = [0, 0]

        self.worker = [None] * 2
        self.worker[self.ra] = threading.Thread\
            (target=self.motor_mng_woker, args=[self.ra, dry_run])
        self.worker[self.ra].name = "RAMotorThread"
        self.worker[self.dec] = threading.Thread\
            (target=self.motor_mng_woker, args=[self.dec, dry_run])
        self.worker[self.dec].name = "DECMotorThread"

        self.init_thread = [None] * 2
        self.init_thread[self.ra] = threading.Thread \
            (target=self.init_manager, args=[self.ra, dry_run])
        self.init_thread[self.ra].name = "RAMotorInitThread"
        self.init_thread[self.dec] = threading.Thread \
            (target=self.init_manager, args=[self.dec, dry_run])
        self.init_thread[self.dec].name = "DECMotorInitThread"

        logger.info('ra port:{} range:{}'.format(self.ra, self.range[self.ra]))
        logger.info('dec port:{} range:{}'.format(self.dec, self.range[self.dec]))

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

    def motor_mng_woker(self, axis, dry_run):
        while not self.isKilled:
            received_action = self.actions_queue[axis].get()
            if received_action is None:
                logger.info("close worker")
                break;
            received_action[0](*received_action[1])
            self.actions_queue[axis].task_done()

    def init_manager(self, axis, dry_run):
        try:
            manager = planetproj.Motor(dry_run=dry_run)
            self._init_motor(manager, axis)
            self.motor_manager[axis] = manager
        except FileNotFoundError as e:
            logger.error('i2c is not connected')
            return
        except Exception as e:
            raise

    def _init_motor(self, manager, axis, power=0.8):
        logger.info('initialize motor')
        self.change_state(axis, 'try-init')
        manager.set_power(axis, power)
        if axis == self.ra:
            manager.set_max_idx(axis, 850)
        logger.info('set_power: {}'.format(power))
        manager.set_zero_position(axis)
        self.change_state(axis, 'initialized')

    def _task_move_absolute(self, axis, pos):
        self.change_state(axis, 'active')
        self.motor_manager[axis].do_rotate_degree_absolute(axis, pos)
        after_pos = self.get_ra_pos()
        self.change_state(axis, 'non-active')
        return after_pos

    def move_ra_absolute(self, pos, enqueue = True):
        if not enqueue and self.actions_queue[self.ra].qsize() > 0:
            raise ValueError('Error: already enqueued action')
        if not self.range[self.ra][0] <= pos <= self.range[self.ra][1]:
            raise ValueError('InterfaceError: Invalid position(={}), expected range({},{})'.format(round(pos,2), round(self.range[self.ra][0], 2), round(self.range[self.ra][1], 2)))
        self.actions_queue[self.ra].put((self._task_move_absolute, [self.ra, pos]))
        logger.info('enqueued: move_ra_absolute({}), queue size:{}'.format(pos, self.actions_queue[self.ra].qsize()))
        return

    def move_dec_absolute(self, pos, enqueue = True):
        if not enqueue and self.actions_queue[self.dec].qsize() > 0:
            raise ValueError('Error: already enqueued action')
        if not self.range[self.dec][0] <= pos <= self.range[self.dec][1]:
            raise ValueError('InterfaceError: Invalid position(={}), expected range({},{})'.format(round(pos,2), round(self.range[self.dec][0], 2), round(self.range[self.dec][1], 2)))
        self.actions_queue[self.dec].put((self._task_move_absolute, [self.dec, pos]))
        logger.info('enqueued: move_dec_absolute({}), queue size:{}'.format(pos, self.actions_queue[self.dec].qsize()))
        return

    #### not tested so do NOT use it ####
    # R.A. only provides relative move, and DEC does not provide relative move
    # def move_ra_relative(self, pos):
    #     self.change_state(axis, 'active')
    #     self.motor.do_rotate_degree_relative(self.ra, pos)
    #     ra_pos = self.get_ra_pos()
    #     self.change_state(axis, 'non-active')
    #     return ra_pos

    def get_ra_pos(self):
        ra_pos = self.motor_manager[self.ra].get_current_degree(self.ra)
        self.pos[self.ra] = ra_pos
        return ra_pos

    def get_dec_pos(self):
        dec_pos = self.motor_manager[self.dec].get_current_degree(self.dec)
        self.pos[self.dec] = dec_pos
        return dec_pos

    def change_state(self, axis, state):
        pre_ra, pre_dec = self.state
        self.state[axis] = state
        logger.debug('The state  has changed: {} -> {}'.format([pre_ra, pre_dec], self.state))

if __name__ == '__main__':
    import time

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s:%(threadName)s:%(name)s:%(levelname)s:%(message)s')
    m = MotorController(dry_run=True)
    m.start()
    m.move_ra_absolute(3.14)
    m.move_dec_absolute(-3.14)
    time.sleep(5)
    m.end()
