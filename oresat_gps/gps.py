"""OreSat Linux updater D-Bus server"""

from logging import Logger
from enum import IntEnum, auto
from threading import Thread, Lock
from time import sleep
import io
import pynmea2
from serial import Serial
from astropy.coordinates import EarthLocation


DBUS_INTERFACE_NAME = "org.OreSat.GPS"
MOCK_DATA = "$GPGGA,184353.07,1929.045,S,02410.506,E,1,04,2.6,100.00,M,-33.9,M,,0000*6D"


class State(IntEnum):
    """The states oresat gps daemon can be in."""

    LOCKED = 0
    """Locked on satellites.."""

    SEARCHING = auto()
    """Looking for satellites."""

    HARDWARE_ERROR = auto()
    """Serial connection failed."""

    NMEA_ERROR = auto()
    """NMEA parser failed."""


class GPSServer():
    """The OreSat GPS daemon.

    Note: all D-Bus Methods, Properties, and Signals follow PascalCase naming.
    """

    # D-Bus interface(s) definition
    dbus = """
    <node>
        <interface name="org.OreSat.GPS">
            <property name="Status" type="y" access="read" />
            <property name="LockedSatellites" type="y" access="read" />
            <property name="StateVector" type="((ddd)(ddd)d)" access="read" />
        </interface>
    </node>
    """  # doesn't work in __init__()

    def __init__(self, logger: Logger, port="/dev/ttyS1", baud=115200):

        self._log = logger
        self._status = State.SEARCHING

        self._ser = Serial(port, baud, timeout=5.0)
        self._sio = io.TextIOWrapper(io.BufferedRWPair(self._ser, self._ser))

        self._satellites = 0
        self._state_vector = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), 0.0)

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

        self._log.debug("starting working loop")

        while self._running:
            # line = self._sio.readline()
            data = pynmea2.parse(MOCK_DATA)  # swap to line
            # print(EarthLocation().from_geodetic(lon=0.0, lat=0.0, height=100))
            print(repr(data))
            sleep(1)

        self._log.debug("stoping working loop")

    @property
    def Status(self):
        """uint8: Current status. Will be a State value."""
        return self._status.value

    @property
    def Satellites(self):
        """uint8: Number of GPS satellites locked onto."""
        return self._satellites

    @property
    def StateVector(self):
        """State Vector in ((pos_x, pos_y, pos_z), (vel_x, vel_y, vel_z),
        time) format.
        """
        return self._state_vector
