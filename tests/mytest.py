import gpiod
import gpiosim
import pytest


@pytest.fixture
def gpio_sim():
    sim = gpiosim.Chip(num_lines=8, line_names={0: "fizz", 1: "fizz", 5: "foo", 7: "bar"})
    yield sim
    del sim


@pytest.fixture
def gpio_chip(gpio_sim):
    chip = gpiod.Chip(gpio_sim.dev_path)
    yield chip
    chip.close()
    del chip


def test_chip_line_request_works(gpio_chip):
    assert gpio_chip.get_info().num_lines == 8
    assert gpio_chip.get_line_info(5).name == "foo"
