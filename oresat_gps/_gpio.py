"""Utility class for working with gpiod."""

from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

import gpiod


@dataclass(frozen=True)
class GpioMapping:
    """Abstracts Gpio lines.

    chip_name: path to the gpiochip the line belongs to
    line_name: the name of the line specified in the device tree
    offset: the numeric offset of the line within the gpio bank
    direction: the gpio line's direction either input or output
    """

    chip_path: str
    line_name: str
    offset: int
    direction: gpiod.line.Direction

    def request(self, consumer: str, initial_value: gpiod.line.Value) -> gpiod.LineRequest:
        """Request the line from the gpiochip.

        The LineRequest object is intended to be used as a context manager.

        :example:
        with mapping.request(consumer="gps", initial_value=gpiod.line.Value.ACTIVE) as request:
            request.set_value(mapping.offset, gpiod.line.Value.INACTIVE)
        """
        return gpiod.request_lines(
            path=self.chip_path,
            consumer=consumer,
            config={
                self.offset: gpiod.LineSettings(
                    direction=self.direction,
                    output_value=initial_value,
                )
            },
        )


def generate_gpio_chips() -> Generator[str]:
    """Scan through available gpio chips.

    gpiochips are numbered non-deterministicly, so all chips must be scanned
    """
    for chip_path in Path("/dev").glob("gpiochip*"):
        if gpiod.is_gpiochip_device(str(chip_path)):
            # Gpiod expects a string
            yield str(chip_path)


def find_line(line_name: str, direction: gpiod.line.Direction) -> GpioMapping:
    """Scan available gpiochips for a line by name."""
    for chip_path in generate_gpio_chips():
        with gpiod.Chip(chip_path) as chip:
            offset = chip.line_offset_from_id(line_name)
            if offset >= 0:
                return GpioMapping(
                    chip_path=chip_path, line_name=line_name, offset=offset, direction=direction
                )
    raise RuntimeError(f"Can't find {line_name} on any chip.")
