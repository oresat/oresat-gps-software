"""Utility functions for working with gpiod."""

import gpiod
from gpiod.line import Direction, Value


def request_gpio_output(
    chip_path: str,
    offset: int,
    line_name: str,
) -> gpiod.LineRequest:
    """Request a line from a gpiochip by numeric offset.

    Parameters
    ----------
    chip_path
                Path to the gpiochip character device
    offset
                Numeric offset of the desired line within the gpiochip
    line_name
                A human-readable name for the desired line set in the device tree

    Raises
    ------
    RuntimeError
        If the requested line doesn't have the expected name

    Returns
    -------
    gpiod.LineRequest
        A request for gpiod line as an output.

    """
    # Check if the given gpiochip device has the expected line name at the given offset
    with gpiod.Chip(chip_path) as chip:
        if chip.get_line_info(offset).name != line_name:
            raise RuntimeError(f"Line {line_name} not found at offset {offset} on chip {chip_path}")
        return chip.request_lines(
            consumer="oresat-gps",
            config={
                offset: gpiod.LineSettings(
                    direction=Direction.OUTPUT,
                    output_value=Value.INACTIVE,
                )
            },
        )
