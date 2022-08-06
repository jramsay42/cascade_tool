import pytest
import os 
import sys

#Add the source directory to the path
TEST_DIRECTORY = os.path.dirname(__file__)
SRC_DIRECTORY = '..'
sys.path.insert(0, os.path.abspath(os.path.join(TEST_DIRECTORY, SRC_DIRECTORY)))

from cascade import Module
from cascade import Interconnect
from cascade import Cascade

def test_cascade():
    module_one = Module(gain=12, gain_uncertainty=1, output_vswr=1.5, gain_std_dev=0.5)
    cable_one = Interconnect(gain=-1.5)
    module_two = Module(gain=8, gain_uncertainty=2, input_vswr=1.5, output_vswr=2, gain_std_dev=1.25)
    cable_two = Interconnect(gain=-1)
    module_three = Module(gain=2, gain_uncertainty=2, input_vswr=2, output_vswr=2.8, gain_std_dev=0.8)
    cable_three = Interconnect(gain=-0.8)
    module_four = Module(gain=30, gain_uncertainty=2, input_vswr=3.2, gain_std_dev=1.3)

    lineup = Cascade()
    lineup.add_element(module_one)
    lineup.add_element(cable_one)
    lineup.add_element(module_two)
    lineup.add_element(cable_two)
    lineup.add_element(module_three)
    lineup.add_element(cable_three)
    lineup.add_element(module_four)

    results = lineup.calculate_cumulative_data()
    display_results = lineup.round_cumulative_data(results)

    for i in range(0, len(display_results)):
        element = display_results[i]
        print("Output at stage {}: {}".format(i, display_results[i]))

test_cascade()