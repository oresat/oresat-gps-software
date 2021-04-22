"""OreSat Linux updater D-Bus server"""

from logging import Logger
from enum import IntEnum, auto
from threading import Thread, Lock
from datetime import datetime, timedelta, timezone
from time import clock_settime, CLOCK_REALTIME
from serial import Serial, SerialException
from oresat_gps.skytraq import NavData, parse_skytraq_binary


DBUS_INTERFACE_NAME = "org.OreSat.GPS"

TOW_BASE = datetime(2019, 4, 7, tzinfo=timezone.utc)
"""Last gps week rollover, note: next is in 2038"""


class State(IntEnum):
    """The states oresat gps daemon can be in."""

    SEARCHING = 0
    """Looking for satellites."""

    LOCKED = auto()
    """Locked on satellites.."""

    HARDWARE_ERROR = auto()
    """Serial connection failed."""

    PARSER_ERROR = auto()
    """Binary message parser failed."""


def gps_time(gps_week: int, tow: int) -> float:
    """Get the time from gps_week and TOW (time of week) as a float similar
    to time.time()
    """

    usec = tow % 100 * 1000
    # 86400 is number of seconds in a day
    sec = (tow / 100) % 86400
    day = ((tow / 100) / 86400) + (gps_week * 7)
    dt = TOW_BASE + timedelta(days=day, seconds=sec, microseconds=usec)

    return dt.timestamp()


class GPSServer():
    """The OreSat GPS daemon.

    Note: all D-Bus Methods, Properties, and Signals follow PascalCase naming.
    """

    # D-Bus interface(s) definition
    dbus = """
    <node>
        <interface name="org.OreSat.GPS">
            <property name="Satellites" type="y" access="read" />
            <property name="StateVector" type="(iiiiiiuu)" access="read" />
            <property name="Status" type="y" access="read" />
            <property name="Sync" type="b" access="readwrite" />
        </interface>
    </node>
    """  # doesn't work in __init__()

    def __init__(self,
                 logger: Logger,
                 port="/dev/ttyS2",
                 baud=9600,
                 sync_time=False):
        """
        Attributes
        ----------
        logger: logging.Logger
            Logger to use.
        port: str
            Serial port to use.
        baud: str
            Baud to use.
        time_sync: bool
            Set the system time on first lock.
        """

        self._log = logger
        self._status = State.SEARCHING
        self._sync_time = sync_time
        self._nav_data = tuple([0] * 20)

        self._ser = Serial(port, baud, timeout=5.0)

        # set up working thread
        self._running = False
        self._working_thread = Thread(target=self._working_loop)
        self._mutex = Lock()

    def __del__(self):
        self.quit()

    def run(self):
        """Start the D-Bus server."""
        self._log.debug("starting working thread")
        self._running = True
        self._working_thread.start()

    def quit(self):
        """Stop the D-Bus server."""
        self._log.debug("stopping working thread")
        self._running = False
        if self._working_thread.is_alive():
            self._working_thread.join()

    def _working_loop(self):
        """The main loop pulling data from GPS antenna. Will be in its own
        thread, seperate from D-Bus.
        """

        # swap to binary mode
        self._ser.write(b'\xA0\xA1\x00\x03\x09\x02\x00\x0B\x0D\x0A')

        self._log.debug("starting working loop")

        while self._running:
            try:
                line = self._ser.readline()
            except SerialException as exc:
                self._log.error('Device error: {}'.format(exc))
                self._status = State.HARDWARE_ERROR
                continue

            data = parse_skytraq_binary(line)
            if not data:
                self._status = State.PARSER_ERROR
                continue

            if data[0] == 0xA8:
                if data[NavData.FIX_MODE.value] == 2:
                    gps_week = data[NavData.GPS_WEEK.value]
                    tow = data[NavData.TOW.value]
                    if not self._sync_time:  # need to sync_time
                        clock_settime(CLOCK_REALTIME, gps_time(gps_week, tow))
                        self._sync_time = True

                self._mutex.acquire()
                if data[NavData.FIX_MODE.value] == 2:
                    self._status = State.LOCKED
                else:
                    self._status = State.SEARCHING
                self._nav_nav_data = data
                self._mutex.release()

        self._log.debug("stoping working loop")

    @property
    def Sync(self):
        """bool: sync system time on next lock"""
        return self._sync_time

    @Sync.setter
    def Sync(self):
        self._sync_time = False

    @property
    def Status(self):
        """uint8: Current status. Will be a State value."""
        return self._status.value

    @property
    def Satellites(self):
        """uint8: Number of GPS satellites locked onto."""
        return self._nav_data[NavData.NUMBER_OF_SV.value]

    @property
    def StateVector(self):
        """State Vector in ((pos_x, pos_y, pos_z), (vel_x, vel_y, vel_z),
        (time_coarse, time_fine)) format. All postions and velocities are int32
        and time are uint32.
        """

        self._mutex.acquire()
        gps_week = self._nav_data[NavData.GPS_WEEK.value]
        tow = self._nav_data[NavData.TOW.value]
        self._mutex.release()

        if tow > 0:  # avoid divide by 0
            time = gps_time(gps_week, tow)
            time_coarse = int(time)
            time_fine = tow % 100
        else:
            time_coarse = 0
            time_fine = 0

        self._mutex.acquire()
        temp = (self._nav_data[NavData.ECEF_X.value],
                self._nav_data[NavData.ECEF_Y.value],
                self._nav_data[NavData.ECEF_Z.value],
                self._nav_data[NavData.ECEF_VX.value],
                self._nav_data[NavData.ECEF_VY.value],
                self._nav_data[NavData.ECEF_VZ.value],
                time_coarse,
                time_fine)
        self._mutex.release()

        return temp
