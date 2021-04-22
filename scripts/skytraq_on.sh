# SkyTraq
echo 98 > /sys/class/gpio/export
echo 98 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio98/direction
echo 1 > /sys/class/gpio/gpio98/value

# LNA
echo 100 > /sys/class/gpio/export
echo 100 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio100/direction
echo 1 > /sys/class/gpio/gpio100/value
