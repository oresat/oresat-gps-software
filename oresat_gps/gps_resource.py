import logging
from os import geteuid
from enum import IntEnum
from time import clock_settime, CLOCK_REALTIME

import gpio
from olaf import Resource, scet_int_from_time, logger

from .skytraq import SkyTrack, NavData, FixMode, gps_datetime

# fix internal gpio the logger from over logging
logging.getLogger().handlers[0].setLevel(logging.ERROR)


class ControlSubindex(IntEnum):
    SERIAL_BUS = 0x1
    GPIO0 = 0x2
    GPIO1 = 0x3
    MOCK = 0x4
    STATUS = 0x5
    IS_SYNCD = 0x6


class States(IntEnum):
    OFF = 0x00
    SEARCHING = 0x01
    LOCKED = 0x02
    FAILED = 0xFF


class GPSResource(Resource):

    INDEX_SKYTRAQ_CONTROL = 0x6000
    INDEX_SKYTRAQ_DATA = 0x6001

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._gpio0 = None
        self._gpio1 = None
        self._gpio0_pin = None
        self._gpio1_pin = None
        self._skytraq = None
        self._state = States.OFF

        self._uid = geteuid()
        if self._uid != 0:
            logger.warning('not running as root, cannot set system time to time from skytraq')

    def on_start(self):

        self.control_rec = self.od[self.INDEX_SKYTRAQ_CONTROL]
        self.data_rec = self.od[self.INDEX_SKYTRAQ_DATA]

        # control subindexes
        self.mock_obj = self.control_rec[ControlSubindex.MOCK.value]
        self.is_syncd_obj = self.control_rec[ControlSubindex.IS_SYNCD.value]
        self.status_obj = self.control_rec[ControlSubindex.STATUS.value]

        # make sure the flag for the time has been syncd is set to false
        self.is_syncd_obj.value = False

        self.mock_obj.value = self.mock_hw
        self._gpio0_pin = self.control_rec[ControlSubindex.GPIO0.value].value
        self._gpio1_pin = self.control_rec[ControlSubindex.GPIO1.value].value
        if self.mock_hw:
            logger.warning('mocking SkyTrack')
        else:
            self._gpio0 = gpio.setup(self._gpio0_pin, gpio.OUT)
            self._gpio1 = gpio.setup(self._gpio1_pin, gpio.OUT)

        self._skytraq_power_on()
        serial_bus = self.control_rec[ControlSubindex.SERIAL_BUS.value].value
        self._skytraq = SkyTrack(serial_bus, self._new_message, self._new_error, self.mock_hw)
        self._skytraq.start()
        self._state = States.SEARCHING

    def on_end(self):
        self._skytraq.stop()
        self._skytraq_power_off()
        self._state = States.OFF

    def on_read(self, index, subindex, od):
        if index == self.INDEX_SKYTRAQ_CONTROL and subindex == ControlSubindex.STATUS:
            return self._state.value

    def on_write(self, index, subindex, od, data):

        if index == self.INDEX_SKYTRAQ_CONTROL and subindex == ControlSubindex.STATUS:
            # turn skytraq on/off
            if od.decode_raw(data):
                self._skytraq_power_on()
            else:
                self._skytraq_power_off()
                self.data_rec[NavData.NUMBER_OF_SV.value].value = 0  # zero this for TPDO

    def _new_message(self, nav_data: NavData):

        if nav_data.fix_mode == FixMode.NO_FIX:
            self.data_rec[1].value = 0
        else:
            # datetime from gps message
            dt = gps_datetime(nav_data.gps_week, nav_data.tow)

            # sync clock if it hasn't been syncd yet
            if not self.is_syncd_obj.value and self._uid == 0:
                clock_settime(CLOCK_REALTIME, dt)
                logger.info('set time based off of skytraq time')
                self.is_syncd_obj.value = True

            # add all skytraq data to OD
            for i in range(len(nav_data)):
                self.data_rec[i].value = nav_data[i]
            self.data_rec[0x14].value = scet_int_from_time(dt)

            # send gps tpdos
            self.send_tpdo(2)
            self.send_tpdo(3)
            self.send_tpdo(4)
            self.send_tpdo(5)

        # update status
        if nav_data.number_of_sv >= 4 and nav_data.fix_mode >= FixMode.FIX_2D:
            self._state = States.LOCKED
        else:
            self._state = States.SEARCHING

    def _new_error(self, error: str):

        logger.error(error)

    def _skytraq_power_on(self):

        logger.info('turning SkyTrack on')
        if not self.mock_hw:
            self._gpio0.output(self._gpio0_pin, gpio.HIGH)
            self._gpio1.output(self._gpio1_pin, gpio.HIGH)
        self._state = States.SEARCHING

    def _skytraq_power_off(self):

        logger.info('turning SkyTrack off')
        if not self.mock_hw:
            self._gpio0.output(self._gpio0_pinp, gpio.LOW)
            self._gpio1.output(self._gpio1_pin, gpio.LOW)
        self._state = States.OFF
