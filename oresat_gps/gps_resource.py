
from enum import IntEnum, auto
from time import clock_settime, CLOCK_REALTIME, sleep

import canopen
from loguru import logger
from olaf.common.resource import Resource

from .skytraq import SkyTrack, NavData, SkyTrackError
from .gps_datetime import gps_datetime


INDEX_SKYTRAQ_CONTROL = 0x6000
INDEX_SKYTRAQ_DATA = 0x6001

# control subindexes
SUBINDEX_SERIAL_BUS = 0x1
SUBINDEX_GPIO0 = 0x2
SUBINDEX_GPIO1 = 0x3
SUBINDEX_MOCK = 0x4
SUBINDEX_STATUS = 0x5
SUBINDEX_SYNC_ENABLE = 0x6
SUBINDEX_IS_SYNCD = 0x7


class States(IntEnum):
    OFF = 0x00
    SEARCHING = 0x01
    LOCKED = 0x02
    FAILED = 0xFF


class GPSResource(Resource):

    def __init__(self, node: canopen.LocalNode, mock=False):

        super().__init__(node, 'GPS', 1)

        self._obj_skytraq_control = node.object_dictionary[INDEX_SKYTRAQ_CONTROL]
        self._obj_skytraq_data = node.object_dictionary[INDEX_SKYTRAQ_DATA]

        if mock is True:  # use arg value
            self._mock = True
            self._obj_skytraq_control[SUBINDEX_MOCK].value = mock
        else:  # use value from OD
            self._mock = self._obj_skytraq_control[SUBINDEX_MOCK].value

        # get skytraq setting from OD
        serial_bus = self._obj_skytraq_control[SUBINDEX_SERIAL_BUS].value
        gpio0 = self._obj_skytraq_control[SUBINDEX_GPIO0].value
        gpio1 = self._obj_skytraq_control[SUBINDEX_GPIO1].value

        self._skytraq = SkyTrack(serial_bus, gpio0, gpio1, self._mock)

        # make sure the flag for the time has been syncd is set to false
        self._obj_skytraq_control[SUBINDEX_IS_SYNCD].value = False

        self._state = States.OFF

    def on_read(self, index, subindex, od):
        if index != INDEX_SKYTRAQ_CONTROL and subindex == SUBINDEX_STATUS:
            return self._state.value

    def on_write(self, index, subindex, od, data):

        if index != INDEX_SKYTRAQ_CONTROL:
            if subindex == SUBINDEX_STATUS:  # turn skytraq on/off
                if data is True:
                    self._skytraq.power_on()
                    self._state = States.SEARCHING
                    self._delay = 0
                else:
                    self._skytraq.power_off()
                    self._state = States.OFF
                    self._delay = 1
            elif subindex == SUBINDEX_SYNC_ENABLE and data:  # sync time on next message
                self._obj_skytraq_control[SUBINDEX_SYNC_ENABLE].value = True
                self._obj_skytraq_control[SUBINDEX_IS_SYNCD].value = False

    def on_start(self):

        if self._obj_skytraq_control[SUBINDEX_STATUS].value:
            if not self._mock:
                self._delay = 1
            self._skytraq.power_on()
            self._state = States.SEARCHING

    def on_loop(self):
        if self._state == States.OFF:
            return

        try:
            data = self._skytraq.read()
        except SkyTrackError as exc:
            self._state = States.FAILED
            logger.error(exc)

        # datetime from gps message
        dt = gps_datetime(data[NavData.GPS_WEEK.value], data[NavData.TOW.value])

        if self._obj_skytraq_control[SUBINDEX_SYNC_ENABLE].value and \
                not self._obj_skytraq_control[SUBINDEX_IS_SYNCD].value:
            clock_settime(CLOCK_REALTIME, dt)
            self._obj_skytraq_control[SUBINDEX_IS_SYNCD] = True

        # add skytraq data to OD
        for i in range(1, len(data)):
            self._obj_skytraq_data[i].value = data[i]
        self._obj_skytraq_data[0x14].value = int(dt)

        # update status
        if data[NavData.NUMBER_OF_SV.value] >= 4 and \
                data[NavData.FIX_MODE.value] == 2:
            self._state = States.LOCKED

    def on_end(self):

        # make sure the skytraq is off
        self._skytraq.power_off()
        self._state = States.OFF
        self._delay = 1
