OreSat GPS Software
===================

Software for OreSat's hardware-based GPS using the `SkyTraq Venus838FLPx-L`_.


Quickstart
----------

* Install dependenies ``$ pip install -r requirements.txt``

* Make a virtual CAN bus

  * ``$ sudo ip link add dev vcan0 type vcan``

  * ``$ sudo ip link set vcan0 up``

* Run ``$ python -m oresat_gps``

  * Can mock the SkyTraq by adding the ``-m`` flag

  * See other options with ``-h`` flag


.. _SkyTraq Venus838FLPx-L: https://www.skytraq.com.tw/homesite/Venus838FLPx_PB_v1.pdf
