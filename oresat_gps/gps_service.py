"""
GPS SkyTraq Service.

Reads the GPS data stream from SkyTraq and puts the data into the OD.
"""

from datetime import datetime
from enum import IntEnum
from os import geteuid
from time import CLOCK_REALTIME, clock_settime

import canopen
from olaf import Gpio, NetworkError, Service, logger

from .skytraq import FixMode, SkyTraq, SkyTraqError, gps_datetime


class GpsState(IntEnum):
    """SkyTraq GPS State."""

    OFF = 0x00
    SEARCHING = 0x01
    LOCKED = 0x02
    ERROR = 0xFF


class GpsService(Service):
    """GPS SkyTraq Service."""

    def __init__(self, skytraq: SkyTraq, gpio_lna: Gpio, gpio_skytraq: Gpio):
        super().__init__()

        self._gpio_skytraq = gpio_skytraq
        self._gpio_lna = gpio_lna
        self._skytraq = skytraq

        self._state = GpsState.OFF

        self._uid = geteuid()
        if self._uid != 0:
            logger.warning("not running as root, cannot set system time to time from skytraq")

        self.is_syncd_obj: canopen.objectdictionary.Variable = None

    def on_start(self):
        self.node.add_sdo_callbacks("status", None, self._on_read, self._on_write)

        self.is_syncd_obj = self.node.od["time_syncd"]
        # make sure the flag for the time has been syncd is set to false
        self.is_syncd_obj.value = False

        self._skytraq_power_on()

    def on_stop(self):
        self._skytraq_power_off()

    def _on_read(self):
        return self._state.value

    def _on_write(self, value):
        # turn skytraq on/off
        if value:
            self._skytraq_power_on()
        else:
            self._skytraq_power_off()

    def on_loop(self):
        if not self._skytraq.is_conencted:
            self.sleep(0.1)
            return  # do nothing

        try:
            nav_data = self._skytraq.read()
        except SkyTraqError:
            return

        skytraq_rec = self.node.od["skytraq"]

        if nav_data.fix_mode == FixMode.NO_FIX:
            skytraq_rec["fix_mode"].value = FixMode.NO_FIX.value
        else:
            # datetime from gps message
            ts = gps_datetime(nav_data.gps_week, nav_data.tow)

            # sync clock if it hasn't been syncd yet
            if not self.is_syncd_obj.value and self._uid == 0:
                clock_settime(CLOCK_REALTIME, ts)
                logger.info("set time based off of skytraq time")
                self.is_syncd_obj.value = True

            # add all skytraq data to OD
            for i in nav_data._asdict().keys():
                if i == "message_id":
                    continue
                skytraq_rec[i].value = nav_data._asdict()[i]

            dt = datetime.fromtimestamp(ts)
            ms_since_midnight = (((((dt.hour * 60) + dt.minute) * 60) + dt.second) * 1000) + (
                dt.microsecond // 1000
            )
            skytraq_rec["time_since_midnight"].value = ms_since_midnight

            # send gps tpdos
            try:
                self.node.send_tpdo(3)
                self.node.send_tpdo(4)
                self.node.send_tpdo(5)
                self.node.send_tpdo(6)
            except NetworkError:
                pass  # CAN network is down

        # update status
        if nav_data.number_of_sv >= 4 and nav_data.fix_mode >= FixMode.FIX_2D:
            self._state = GpsState.LOCKED
        else:
            self._state = GpsState.SEARCHING

    def on_loop_error(self, error: str):
        self._skytraq_power_off()
        self._state = GpsState.ERROR
        logger.exception(error)

    def _skytraq_power_on(self):
        logger.info("turning SkyTraq on")
        self._gpio_skytraq.high()
        self._gpio_lna.high()
        self._skytraq.connect()
        self._state = GpsState.SEARCHING

    def _skytraq_power_off(self):
        logger.info("turning SkyTraq off")
        self._skytraq.disconnect()
        self._gpio_lna.low()
        self._gpio_skytraq.low()
        self._state = GpsState.OFF
