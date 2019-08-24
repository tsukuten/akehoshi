import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../webapi/')

from MotorController import MotorController
from UnitController import UnitController
from math import pi

class TestUnit(unittest.TestCase):
    """ test class of Unit and Motor Controller
    """
    def setUp(self):
        print("setup")
        self.unit = UnitController(dry_run=test_dry_run)
        self.motor = MotorController(dry_run=test_dry_run)

    def test_set_brightness_ok(self):
        """ Unit: test ok range(ledid('a'-'l') and brightness([0 <-(0.1)-> 1]))
        """
        ok_ledid = [ i for i in range(0,12) ]
        ok_britness_float = [ float(i)/ 10 for i in range(0,11) ]
        ok_britness_int = [int(0), int(1)]
        for c in ok_ledid:
            for b in ok_britness_float:
                # print('test set_brightness(\'{}\', {})'.format(c, b))
                res = self.unit.set_brightness(c, b)
                self.assertEqual(c, res[0])
                self.assertEqual(b, res[1])
        for c in ok_ledid:
            for b in ok_britness_int:
                # print('test set_brightness(\'{}\', {})'.format(c, b))
                res = self.unit.set_brightness(c, b)
                self.assertEqual(c, res[0])
                self.assertEqual(b, res[1])

    def test_set_brightness_ng(self):
        """ Unit: test value where ValueError is expected
        """
        ng_ledid = ['m', 'A', 'L']
        ng_value_brightness = [-1, -0.1, 1.1, 100]
        for c in ng_ledid:
            print('test set_brightness({}, {})'.format(c, 1))
            with self.assertRaises(TypeError) as cm:
                self.unit.set_brightness(c, 1)
            print(cm.exception)
            self.assertEqual(cm.exception.args[0],'ledid(={}) and brightness(={}) is expected int or float'.format(type(c), type(1)))
        for b in ng_value_brightness:
            print('test set_brightness(\'{}\', {})'.format('a', b))
            with self.assertRaises(ValueError) as cm:
                self.unit.set_brightness('a', b)
            exception = cm.exception
            self.assertEqual(exception.args[0], 'brightness is not in range: [0,1]')

    def test_move_ra_absolute_ok_range(self):
        """ Motro: test ok range([-π, π])
        """
        ok_pos = [ float(i) * pi / 10 for i in range(-10,10)]
        for p in ok_pos:
            print('test move_ra_absolute({})'.format(round(p,2)))
            ra_pos = self.motor.move_ra_absolute(p)
            self.assertEqual(round(ra_pos, 2), round(p, 2))

    def test_move_ra_absolute_invalid_range(self):
        """ Motro: test ng range( p < -π or π < p)
        """
        ng_pos = [-3 * pi, -2*pi-0.1, 2*pi+0.1, 3 * pi]
        for p in ng_pos:
            print('test move_ra_absolute({})'.format(round(p,2)))
            with self.assertRaises(ValueError) as cm:
                origin_pos = self.motor.get_ra_pos()
                ra_pos = self.motor.move_ra_absolute(p)
            exception = cm.exception
            print(exception)
            self.assertEqual(exception.args[0], 'InterfaceError: Invalid position(={}), expected range({},{})'.format(round(p,2), round(self.motor.ra_range[0], 2), round(self.motor.ra_range[1], 2)))
            self.assertNotEqual(origin_pos, p)

    def test_move_dec_absolute(self):
        """ Motro: test ok range([-π, π])
        """
        ok_pos = [ float(i) * pi / 10 for i in range(-10,10)]
        for p in ok_pos:
            print('test move_ra_absolute({})'.format(round(p,2)))
            ra_pos = self.motor.move_dec_absolute(p)
            self.assertEqual(round(ra_pos, 2), round(p, 2))

    def test_move_dec_absolute_invalid_range(self):
        """ Motro: test ng range( p < -2π or 2π < p)
        """
        ng_pos = [-2 * pi, -pi-0.1, pi+0.1, 2 * pi]
        for p in ng_pos:
            print('test move_dec_absolute({})'.format(round(p,2)))
            with self.assertRaises(ValueError) as cm:
                origin_pos = self.motor.get_dec_pos()
                ra_pos = self.motor.move_dec_absolute(p)
            exception = cm.exception
            self.assertEqual(exception.args[0], 'InterfaceError: Invalid position(={}), expected range({},{})'.format(round(p,2), round(self.motor.dec_range[0], 2), round(self.motor.dec_range[1], 2)))
            self.assertNotEqual(origin_pos, p)

test_dry_run = True
unittest.main()
