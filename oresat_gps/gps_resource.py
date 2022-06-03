
from enum import IntEnum, auto
from time import clock_settime, CLOCK_REALTIME, sleep

import canopen
from olaf import Resource, scet_int_from_time, logger

from .skytraq import SkyTrack, NavData, FixMode, SkyTrackError
from .gps_datetime import gps_datetime


class ControlSubindex(IntEnum):
    SERIAL_BUS = 0x1
    GPIO0 = 0x2
    GPIO1 = 0x3
    MOCK = 0x4
    STATUS = 0x5
    SYNC_ENABLE = 0x6
    IS_SYNCD = 0x7


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

        self.control_rec = self.od[self.INDEX_SKYTRAQ_CONTROL]
        self.data_rec = self.od[self.INDEX_SKYTRAQ_DATA]

        # control subindexes
        self.mock_obj = self.control_rec[ControlSubindex.MOCK.value]
        self.sync_enable_obj = self.control_rec[ControlSubindex.SYNC_ENABLE.value]
        self.is_syncd_obj = self.control_rec[ControlSubindex.IS_SYNCD.value]
        self.is_syncd_obj = self.control_rec[ControlSubindex.STATUS.value]

        if self.mock_hw:  # use arg value
            self.mock_obj.value = self.mock_hw
        else:  # use value from OD
            self._mock_hw = self.mock_obj.value

        if self.mock_hw:
            logger.warning('mocking SkyTrack')
            self.delay = 1
        else:
            self.delay = 0

        # get skytraq setting from OD
        serial_bus = self.control_rec[ControlSubindex.SERIAL_BUS.value].value
        gpio0 = self.control_rec[ControlSubindex.GPIO0.value].value
        gpio1 = self.control_rec[ControlSubindex.GPIO1.value].value

        self._skytraq = SkyTrack(serial_bus, gpio0, gpio1, self.mock_hw)

        # make sure the flag for the time has been syncd is set to false
        self.is_syncd_obj.value = False

        self._state = States.OFF

    def on_read(self, index, subindex, od):
        if index == self.INDEX_SKYTRAQ_CONTROL and subindex == ControlSubindex.STATUS:
            return self._state.value

    def on_write(self, index, subindex, od, data):

        if index == self.INDEX_SKYTRAQ_CONTROL:
            if subindex == ControlSubindex.STATUS:  # turn skytraq on/off
                if od.decode_raw(data):
                    logger.info('turning SkyTrack on')
                    self._skytraq.power_on()
                    self._state = States.SEARCHING
                    if not self.mock_hw:
                        self.delay = 0  # serial bus will loop rate
                else:
                    logger.info('turning SkyTrack off')
                    self._skytraq.power_off()
                    self._state = States.OFF
                    self.data_rec[NavData.NUMBER_OF_SV.value].value = 0  # zero this for TPDO
                    self.delay = 1
            elif subindex == ControlSubindex.SYNC_ENABLE:  # sync time on next message
                self.sync_enable_obj.value = True
                self.is_syncd_obj.value = False

    def on_start(self):

        if not self.mock_hw:
            self.delay = 1
        self._skytraq.power_on()
        self._state = States.SEARCHING

    def on_loop(self):
        if self._state == States.OFF:
            return

        try:
            data = self._skytraq.read()
        except SkyTrackError as exc:
            logger.error(exc)
            return

        if data[NavData.FIX_MODE.value] == FixMode.NO_FIX:
            self.data_rec[1].value = 0
        else:
            # datetime from gps message
            dt = gps_datetime(data[NavData.GPS_WEEK.value], data[NavData.TOW.value])

            # sync clock if it hasn't been syncd yet
            if self.sync_enable_obj.value and not self.is_syncd_obj.value:
                clock_settime(CLOCK_REALTIME, dt)
                logger.info('set time based off of skytraq time')
                self.is_syncd_obj.value = True

            # add all skytraq data to OD
            for i in range(1, len(data)):
                self.data_rec[i].value = data[i]
            self.data_rec[0x14].value = scet_int_from_time(int(dt))

            # send gps tpdos
            self.send_tpdo(2)
            self.send_tpdo(3)
            self.send_tpdo(4)
            self.send_tpdo(5)

        # update status
        if data[NavData.NUMBER_OF_SV.value] >= 4 and \
                data[NavData.FIX_MODE.value] >= FixMode.FIX_2D:
            self._state = States.LOCKED
        else:
            self._state = States.SEARCHING

    def on_end(self):

        # make sure the skytraq is off
        self._skytraq.power_off()
        self._state = States.OFF
        self.delay = 1
