import sys
import os
import planetproj
from logging import getLogger

# Add the path to use planetproj module
# sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../planetproj_progs/host/')

logger = getLogger(__name__)

class UnitController:
    def __init__(self, dry_run=False):
        if dry_run:
            logger.warning('dry_run is True')
        logger.warning('initialize')
        self.state = ''
        self.change_state('try-init')
        self.leds_num = 12
        self.north_board_addr = planetproj.planetproj.ADDR_LED_1
        self.south_board_addr = planetproj.planetproj.ADDR_LED_2
        try:
            self.leds = planetproj.LED(
                      addrs = [self.north_board_addr, self.south_board_addr],
                      num_leds_per_dev = 6,
                      dry_run=dry_run)
        except FileNotFoundError as e:
            logger.error('i2c is not connected')
            sys.exit()
        except Exception as e:
            raise

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

    def change_state(self, state):
        pre_state = self.state
        self.state = state
        # print('The state  has changed: {} -> {}'.format(pre_state, self.state))

    def shutdown(self):
        self.change_state('try-exit')
        try:
            self.leds.set_brightness_multi([ (p, 0) for p in range(0, len(self.ledids)) ])
        except ValueError as e:
            error_message = ' {} in shutdown'.format(e.message)
            raise ValueError(error_message)
        self.change_state('exited')
