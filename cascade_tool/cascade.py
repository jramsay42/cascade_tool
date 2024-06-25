"""
Author: Justin Ramsay

Equations from Practical RF System Design by William Egan

Assumptions:
    Module gain is the transducer power gain
    Modules are unilateral
    Interconnects are at the reference impedance
    Module parameters referred to the reference impedance
"""
import types
import numpy

class Module(object):
    def __init__(self, gain=0, gain_uncertainty=0, input_vswr=1, output_vswr=1, p1dB=1000,
             oip3=1000, noise_figure=0, gain_std_dev=0, noise_figure_uncertainty=0,
             p1dB_uncertainty=0, oip3_uncertainty=0):
        """
        gain in dB, negative for a loss
        gain_uncertainty in dB +/- from nominal value
        input_vswr as dimensionless ratio
        output_vswr as dimensionless ratio
        p1dB in dB referred to the output
        p1dB_uncertainty in dB +/- from nominal value
        oip3 in dB referred to the output
        oip3_uncertainty in dB +/- from nominal value
        noise_figure in dB
        noise_figure_uncertainty in dB +/- from nominal value
        gain_std_dev in dB
        """
        self.gain = gain
        self.gain_uncertainty = gain_uncertainty
        self.gain_std_dev = gain_std_dev
        self.input_vswr = input_vswr
        self.output_vswr = output_vswr
        self.p1dB = p1dB
        self.p1dB_uncertainty = p1dB_uncertainty
        self.oip3 = oip3
        self.oip3_uncertainty = oip3_uncertainty
        self.noise_figure = noise_figure
        self.noise_figure_uncertainty = noise_figure_uncertainty

class Interconnect(object):
    def __init__(self, gain=0, gain_uncertainty=0, input_vswr=1, output_vswr=1, noise_figure=0):
        """
        Model of a passive interconnect referred to a system impedance

        gain in dB, negative for a loss
        gain_uncertainty in dB +/- from nominal value
        input_vswr as dimensionless ratio
        output_vswr as dimensionless ratio
        noise_figure in dB
        """
        self.gain = gain
        self.gain_uncertainty = gain_uncertainty
        self.input_vswr = input_vswr
        self.output_vswr = output_vswr
        self.noise_figure = noise_figure

class VariableAttenuator(Module):
    def __init__(self):
        pass

class Cascade(object):
    def __init__(self):
        #A lineup must go module -> interconnect -> module
        self.lineup = []
        self.keys = ["Mean Gain", "Max Gain", "Min Gain", "Gain Std Dev", "Phase +/-", "Phase Std Dev",
                "Mean Noise Figure", "Max Noise Figure", "Min Noise Figure", "Mean P1dB", "Max P1dB", "Min P1dB"]

    def add_element(self, element):
        self.lineup.append(element)

    def calculate_derived_data(self):
        """
        Calculates all derived gains and phase uncertainties for each element,
        based off the elements connected to it
        """
        lineup_derived_data = [] #Ordered list of dictionaries

        for i in range(0, len(self.lineup)):
            item = self.lineup[i]
            element_derived_data = dict.fromkeys(self.keys, 0)

            if type(item) is Interconnect:
                interconnect_voltage_gain = 10**(item.gain/20)

                round_trip_voltage_gain = interconnect_voltage_gain**2 * ((self.lineup[i-1].output_vswr -1) /
                        (self.lineup[i-1].output_vswr + 1)) * ((self.lineup[i+1].input_vswr - 1) / (self.lineup[i+1].input_vswr + 1)) #Equation 2.53

                mean_effective_gain = 10*numpy.log10(interconnect_voltage_gain**2 / (1 - round_trip_voltage_gain**2)) #Equation 2.59
                max_effective_gain = 20*numpy.log10(interconnect_voltage_gain / (1 - round_trip_voltage_gain)) #Equation 2.55
                min_effective_gain = 20*numpy.log10(interconnect_voltage_gain / (1 + round_trip_voltage_gain)) #Equation 2.56
                gain_std_dev = 0.7 * (max_effective_gain - mean_effective_gain) #Equation 2.74
                phase_uncertainty = numpy.arcsin(round_trip_voltage_gain) / (2 * numpy.pi) * 360 #Equation 2.81
                phase_std_dev = 0.7 * phase_uncertainty #Equation 2.82

                element_derived_data["Mean Gain"] = mean_effective_gain
                element_derived_data["Max Gain"] = max_effective_gain
                element_derived_data["Min Gain"] = min_effective_gain
                element_derived_data["Gain Std Dev"] = gain_std_dev
                element_derived_data["Phase +/-"] = phase_uncertainty
                element_derived_data["Phase Std Dev"] = 0.7 * phase_std_dev
            else:
                element_derived_data["Mean Gain"] = item.gain
                element_derived_data["Max Gain"] = item.gain + item.gain_uncertainty
                element_derived_data["Min Gain"] = item.gain - item.gain_uncertainty
                element_derived_data["Gain Std Dev"] = item.gain_std_dev
                element_derived_data["Phase +/-"] = 0  
                element_derived_data["Phase Std Dev"] = 0
            
            lineup_derived_data.append(element_derived_data)
        return lineup_derived_data


    def calculate_cumulative_data(self):
        """
        Returns a list of dictionaries containing the cumulative lineup characteristics at the output of each element
        """
        lineup_cumulative_data = [] #Ordered list of dictionaries
        lineup_derived_data = self.calculate_derived_data()

        element_cumulative_data = dict.fromkeys(self.keys, 0)

        for i in range(0, len(self.lineup)):
            element_cumulative_data["Mean Gain"] += lineup_derived_data[i]["Mean Gain"]
            element_cumulative_data["Max Gain"] += lineup_derived_data[i]["Max Gain"]
            element_cumulative_data["Min Gain"] += lineup_derived_data[i]["Min Gain"]
            element_cumulative_data["Phase +/-"] += lineup_derived_data[i]["Phase +/-"]
            #TODO: Implement noise
            #element_cumulative_data["Noise Figure"] = 0

            if i==0:
                element_cumulative_data["Gain Std Dev"] = lineup_derived_data[i]["Gain Std Dev"]
                element_cumulative_data["Phase Std Dev"] = lineup_derived_data[i]["Phase Std Dev"]
            else:
                #Assumes the errors are uncorrelated, so we take the root of the sum of squares
                element_cumulative_data["Gain Std Dev"] = numpy.sqrt((lineup_derived_data[i]["Gain Std Dev"])**2 +
                        (lineup_cumulative_data[i-1]["Gain Std Dev"])**2)
                element_cumulative_data["Phase Std Dev"] = numpy.sqrt((lineup_derived_data[i]["Phase Std Dev"])**2 +
                        (lineup_cumulative_data[i-1]["Phase Std Dev"])**2)

            #Appending a copy as python dictionaries are mutable and a reference is passed
            lineup_cumulative_data.append(element_cumulative_data.copy())

        return lineup_cumulative_data

    def round_cumulative_data(self, lineup_cumulative_data):
        """
        Takes a list of dictionaries containing the cumulative lineup characteristics at the output of each element
        and rounds the values for display.
        """
        for i in range(0, len(self.lineup)):
            element = lineup_cumulative_data[i]

            element["Mean Gain"] = round(element["Mean Gain"], 2)
            element["Max Gain"] = round(element["Max Gain"], 2)
            element["Min Gain"] = round(element["Min Gain"], 2)
            element["Phase +/-"] = round(element["Phase +/-"], 4)
            element["Gain Std Dev"] = round(element["Gain Std Dev"], 2)
            element["Phase Std Dev"] = round(element["Phase Std Dev"], 4)
            element["Mean Noise Figure"] = round(element["Mean Noise Figure"], 2)
            element["Max Noise Figure"] = round(element["Max Noise Figure"], 2)
            element["Min Noise Figure"] = round(element["Min Noise Figure"], 2)
        return lineup_cumulative_data
