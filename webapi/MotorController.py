import sys
import os
from math import pi
from logging import getLogger
import planetproj

# Add the path to use planetproj module
# sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../planetproj_progs/host/')

logger = getLogger(__name__)

class MotorController:
    def __init__(self, dry_run = False):
        if dry_run:
            logger.warning('dry_run is True')
        self.state = ''
        try:
            self.motor = planetproj.Motor(dry_run=dry_run)
        except FileNotFoundError as e:
            logger.error('i2c is not connected')
            sys.exit()
        except Exception as e:
            raise
        self.ra = 0 #Rgiht Ascension(赤経)
        self.ra_range = (-2*pi, 2*pi)
        self.dec = 1 #DEClination(赤緯)
        self.dec_range = (-pi, pi)
        logger.info('ra port:{} range:{}'.format(self.ra, self.ra_range))
        logger.info('dec port:{} range:{}'.format(self.dec, self.dec_range))
        self.pos = [0, 0]
        self.init_motor()

    def init_motor(self, power=0.8):
        logger.info('initialize motor')
        self.change_state('try-init')
        self.motor.set_power(self.ra, power)
        self.motor.set_power(self.dec, power)
        logger.info('ra  set_power: {}'.format(power))
        logger.info('dec set_power: {}'.format(power))
        self.motor.set_zero_position(self.ra)
        self.motor.set_zero_position(self.dec)
        self.change_state('initialized')

    def move_ra_absolute(self, pos):
        if not self.ra_range[0] <= pos <= self.ra_range[1]:
            raise ValueError('InterfaceError: Invalid position(={}), expected range({},{})'.format(round(pos,2), round(self.ra_range[0], 2), round(self.ra_range[1], 2)))
        self.change_state('active')
        self.motor.do_rotate_degree_absolute(self.ra, pos)
        ra_pos = self.get_ra_pos()
        self.change_state('non-active')
        return ra_pos

    def move_dec_absolute(self, pos):
        if not self.dec_range[0] <= pos <= self.dec_range[1]:
            raise ValueError('InterfaceError: Invalid position(={}), expected range({},{})'.format(round(pos,2), round(self.dec_range[0], 2), round(self.dec_range[1], 2)))
        self.change_state('active')
        self.motor.do_rotate_degree_absolute(self.dec, pos)
        dec_pos = self.get_dec_pos()
        self.change_state('non-active')
        return dec_pos

    #### not tested so do NOT use it ####
    # R.A. only provides relative move, and DEC does not provide relative move
    # def move_ra_relative(self, pos):
    #     self.change_state('active')
    #     self.motor.do_rotate_degree_relative(self.ra, pos)
    #     ra_pos = self.get_ra_pos()
    #     self.change_state('non-active')
    #     return ra_pos

    def get_ra_pos(self):
        ra_pos = self.motor.get_current_degree(self.ra)
        self.pos[self.ra] = ra_pos
        return ra_pos

    def get_dec_pos(self):
        dec_pos = self.motor.get_current_degree(self.dec)
        self.pos[self.dec] = dec_pos
        return dec_pos

    def change_state(self, state):
        pre_state = self.state
        self.state = state
        logger.debug('The state  has changed: {} -> {}'.format(pre_state, self.state))
