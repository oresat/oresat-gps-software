import logging
from datetime import datetime
from os import geteuid
from time import CLOCK_REALTIME, clock_settime, sleep

import gpiod
from gpiod.line import Direction, Value
from oresat_cand import NodeClient

from .gen.gps_od import GpsEntry, GpsSkytraqFixMode, GpsStatus, GpsTpdo
from .skytraq import SkyTraq, SkyTraqError, gps_time

V1_0 = "1.0"
STQ_EN = 2
MAX_EN = 4

V1_1 = "1.1"
STQ_1PPS = 2
GPS_EN = 4


def ms_since_midnight(ts: int) -> int:
    dt = datetime.fromtimestamp(ts)
    return (((((dt.hour * 60) + dt.minute) * 60) + dt.second) * 1000) + (dt.microsecond // 1000)


class Gps:
    SUPPORTED_HW_VERSIONS = [V1_0, V1_0]

    def __init__(self, port: str, hw_version: str, node: NodeClient, mock_hw: bool = False):
        super().__init__()

        self.hw_version = hw_version
        self.node = node
        self.skytraq = SkyTraq(port, mock_hw)
        self.mock_hw = mock_hw
        self.ipc_error = False

        self.gpio_lines = None
        if not mock_hw:
            if self.hw_version == V1_0:
                self.gpio_lines = gpiod.request_lines(
                    "/dev/gpiochip3",
                    consumer="oresat-gps",
                    config={
                        STQ_EN: gpiod.LineSettings(
                            direction=Direction.OUTPUT,
                            output_value=Value.INACTIVE,
                        ),
                        MAX_EN: gpiod.LineSettings(
                            direction=Direction.OUTPUT,
                            output_value=Value.INACTIVE,
                        ),
                    },
                )
            elif self.hw_version == V1_1:
                self.gpio_lines = gpiod.request_lines(
                    "/dev/gpiochip3",
                    consumer="oresat-gps",
                    config={
                        STQ_1PPS: gpiod.LineSettings(
                            direction=Direction.INPUT,
                        ),
                        GPS_EN: gpiod.LineSettings(
                            direction=Direction.OUTPUT,
                            output_value=Value.INACTIVE,
                        ),
                    },
                )
            else:
                logging.warning(f"unknown hardware verison {self.hw_version}")

        self._last_packet = b""
        self.state = GpsStatus.OFF
        self._running = False

        self.uid = geteuid()
        if self.uid != 0:
            logging.warning("not running as root, cannot set system time to gps time")

    def run(self):
        self._power_on()
        packet_count = 0

        self._running = True
        while self._running:
            if not self.skytraq.is_conencted:
                sleep(0.1)
                return  # do nothing

            try:
                nav_data, self._last_packet = self.skytraq.read()
            except SkyTraqError as e:
                logging.debug(e)
                return

            ts = gps_time(nav_data.gps_week, nav_data.tow)

            if (
                nav_data.fix_mode != GpsSkytraqFixMode.NO_FIX.value
                and not self.node.od_read(GpsEntry.TIME_SYNCD)
                and self.uid == 0
            ):
                clock_settime(CLOCK_REALTIME, ts)
                logging.info("set time based off of gps time")
                self.node.od_write(GpsEntry.TIME_SYNCD, True)

            packet_count += 1

            if nav_data.number_of_sv >= 4 and nav_data.fix_mode >= GpsSkytraqFixMode.FIX_2D.value:
                self.state = GpsStatus.LOCKED
            else:
                self.state = GpsStatus.SEARCHING

            self.node.od_write_multi(
                {
                    GpsEntry.STATUS: self.state.value,
                    GpsEntry.SKYTRAQ_FIX_MODE: nav_data.fix_mode,
                    GpsEntry.SKYTRAQ_NUMBER_OF_SV: nav_data.number_of_sv,
                    GpsEntry.SKYTRAQ_GPS_WEEK: nav_data.gps_week,
                    GpsEntry.SKYTRAQ_TOW: nav_data.tow,
                    GpsEntry.SKYTRAQ_LATITUDE: nav_data.latitude,
                    GpsEntry.SKYTRAQ_LONGITUDE: nav_data.longitude,
                    GpsEntry.SKYTRAQ_ELLIPSOID_ALT: nav_data.ellipsoid_alt,
                    GpsEntry.SKYTRAQ_MEAN_SEA_LVL_ALT: nav_data.mean_sea_lvl_alt,
                    GpsEntry.SKYTRAQ_GDOP: nav_data.gdop,
                    GpsEntry.SKYTRAQ_PDOP: nav_data.pdop,
                    GpsEntry.SKYTRAQ_HDOP: nav_data.hdop,
                    GpsEntry.SKYTRAQ_VDOP: nav_data.vdop,
                    GpsEntry.SKYTRAQ_TDOP: nav_data.tdop,
                    GpsEntry.SKYTRAQ_ECEF_X: nav_data.ecef_x,
                    GpsEntry.SKYTRAQ_ECEF_Y: nav_data.ecef_y,
                    GpsEntry.SKYTRAQ_ECEF_Z: nav_data.ecef_z,
                    GpsEntry.SKYTRAQ_ECEF_VX: nav_data.ecef_vx,
                    GpsEntry.SKYTRAQ_ECEF_VY: nav_data.ecef_vy,
                    GpsEntry.SKYTRAQ_ECEF_VZ: nav_data.ecef_vz,
                    GpsEntry.SKYTRAQ_TIME_SINCE_MIDNIGHT: ms_since_midnight(ts),
                    GpsEntry.SKYTRAQ_PACKET_COUNT: packet_count,
                }
            )
            self.node.send_tpdo([GpsTpdo.TPDO_3, GpsTpdo.TPDO_4, GpsTpdo.TPDO_5, GpsTpdo.TPDO_6])

        self._power_off()

    def stop(self):
        self._running = False

    def _power_on(self):
        logging.info("turning gps on")
        if not self.mock_hw:
            if self.hw_version == V1_0:
                self.gpio_lines.set_value(STQ_EN, Value.ACTIVE)
                self.gpio_lines.set_value(MAX_EN, Value.ACTIVE)
            elif self.hw_version == V1_1:
                self.gpio_lines.set_value(GPS_EN, Value.ACTIVE)
        self.skytraq.connect()
        self.state = GpsStatus.SEARCHING

    def _power_off(self):
        logging.info("turning gps off")
        self.skytraq.disconnect()
        if not self.mock_hw:
            if self.hw_version == V1_0:
                self.gpio_lines.set_value(STQ_EN, Value.INACTIVE)
                self.gpio_lines.set_value(MAX_EN, Value.INACTIVE)
            elif self.hw_version == V1_1:
                self.gpio_lines.set_value(GPS_EN, Value.INACTIVE)
        self.state = GpsStatus.OFF

    def _set_time_syncd(self, value: bool):
        logging.info(f"time syncd set to {value}")
        self.node.od_write(GpsEntry.TIME_SYNCD, value)

    def _get_last_packet(self) -> bytes:
        return self._last_packet
