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

def result_dictionary_builder(mean_gain=0, max_gain=0, min_gain=0, gain_std_dev=0, mean_p1dB=0000, max_p1dB=0000, min_p1dB=0000, 
            mean_noise_figure=0, max_noise_figure=0, min_noise_figure=0, phase_uncertainty=0, phase_std_dev=0):
            """
                This function does not check that its inputs are of the required format
            """
            return {'Mean Gain': mean_gain, 'Max Gain': max_gain, 'Min Gain': min_gain, 'Gain Std Dev': gain_std_dev, 'Mean P1dB': mean_p1dB,
            'Max P1dB': max_p1dB, 'Min P1dB': min_p1dB, 'Mean Noise Figure': mean_noise_figure, 'Max Noise Figure': max_noise_figure,
            'Min Noise Figure': min_noise_figure, 'Phase +/-': phase_uncertainty, 'Phase Std Dev': phase_std_dev}

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

    #Dictionaries with the expected results
    dict_0 = result_dictionary_builder(mean_gain=12, max_gain=13, min_gain=11, gain_std_dev=0.5)
    dict_1 = result_dictionary_builder(mean_gain=10.5, max_gain=11.75, min_gain=9.26, gain_std_dev=0.53, 
            phase_uncertainty=1.6227, phase_std_dev=0.7951)
    dict_2 = result_dictionary_builder(mean_gain=18.5, max_gain=21.75, min_gain=15.26, gain_std_dev=1.36,
            phase_uncertainty=1.6227, phase_std_dev=0.7951)
    dict_3 = result_dictionary_builder(mean_gain=17.54, max_gain=21.55, min_gain=13.52, gain_std_dev=1.46,
            phase_uncertainty=6.6861, phase_std_dev=2.6054)
    dict_4 = result_dictionary_builder(mean_gain=19.54, max_gain=25.55, min_gain=13.52, gain_std_dev=1.66,
            phase_uncertainty=6.6861, phase_std_dev=2.6054)
    dict_5 = result_dictionary_builder()

    #dict_0 = {'Mean Gain': 12, 'Max Gain': 13, 'Min Gain': 11, 'Gain Std Dev': 0.5, 'Phase +/-': 0, 'Phase Std Dev': 0, 'Mean Noise Figure': 0}
    #dict_1 = {'Mean Gain': 10.5, 'Max Gain': 11.75, 'Min Gain': 9.26, 'Gain Std Dev': 0.53, 'Phase +/-': 1.6227, 'Phase Std Dev': 0.7951}
    #dict_2 = {'Mean Gain': 18.5, 'Max Gain': 21.75, 'Min Gain': 15.26, 'Gain Std Dev': 1.36, 'Phase +/-': 1.6227, 'Phase Std Dev': 0.7951}
    #dict_3 = {'Mean Gain': 17.54, 'Max Gain': 21.55, 'Min Gain': 13.52, 'Gain Std Dev': 1.46, 'Phase +/-': 6.6861, 'Phase Std Dev': 2.6054}
    #dict_4 = {'Mean Gain': 19.54, 'Max Gain': 25.55, 'Min Gain': 13.52, 'Gain Std Dev': 1.66, 'Phase +/-': 6.6861, 'Phase Std Dev': 2.6054}
    dict_5 = {'Mean Gain': 18.93, 'Max Gain': 26.76, 'Min Gain': 11.09, 'Gain Std Dev': 2.1, 'Phase +/-': 18.5963, 'Phase Std Dev': 6.3911}
    dict_6 = {'Mean Gain': 48.93, 'Max Gain': 58.76, 'Min Gain': 39.09, 'Gain Std Dev': 2.47, 'Phase +/-': 18.5963, 'Phase Std Dev': 6.3911}

    assert display_results[0] == dict_0
    assert display_results[1] == dict_1
    assert display_results[2] == dict_2
    assert display_results[3] == dict_3
    assert display_results[4] == dict_4
    assert display_results[5] == dict_5


    #for i in range(0, len(display_results)):
    #    element = display_results[i]
    #    print("Output at stage {}: {}".format(i, display_results[i]))

test_cascade()