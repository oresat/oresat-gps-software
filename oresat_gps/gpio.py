import os


class GPIOError(Exception):
    '''Error with GPIO'''


class GPIO:

    def __init__(self, num: int):

        self._num = num
        self._is_on = False  # save on IO calls

        if not os.path.isdir(f'/sys/class/gpio/gpio{self._num}'):
            raise GPIOError(f'gpio{num} does not exist')

        try:
            with open('/sys/class/gpio/export', 'w') as f:
                f.write(self._num)
            with open('/sys/class/gpio/export', 'w') as f:
                f.write(self._num)
        except PermissionError:
            pass  # will always fail, tho it actually works

        with open(f'/sys/class/gpio/gpio{self._num}/direction', 'w') as f:
            f.write('out')

        with open(f'/sys/class/gpio/gpio{self._num}/value', 'r') as f:
            self._is_on = f.read() == '1'

    def on(self):

        if self._is_on:
            return  # already on

        with open(f'/sys/class/gpio/gpio{self._num}/value', 'w') as f:
            f.write('1')

        self._is_on = True

    def off(self):

        if not self._is_on:
            return  # already off

        with open(f'/sys/class/gpio/gpio{self._num}/value', 'w') as f:
            f.write('0')

        self._is_on = False

    @property
    def is_on(self):

        return self._is_on

    @property
    def num(self):

        return self._num
