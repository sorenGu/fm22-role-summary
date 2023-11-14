import argparse
import json
import os
from json import JSONDecodeError
from typing import List, Tuple

from colorama import Fore, Style

os.system('color')

class Element:
    def __init__(self, weight: float):
        self.weight = weight
        self.value = 0
        self.number_of_attributes = 0

    def add(self, value):
        self.number_of_attributes += 1
        self.value += value

    def set(self, element: "Element"):
        self.value += element.value
        self.number_of_attributes += element.number_of_attributes

    def get_average(self):
        if self.number_of_attributes == 0:
            return 0
        return self.value / self.number_of_attributes


def get_text_color(value):
    for max_value, style in (
            (0, (Fore.WHITE,)),
            (20, (Fore.WHITE, Style.BRIGHT)),
            (25, (Fore.YELLOW,)),
            (30, (Fore.YELLOW, Style.BRIGHT)),
            (35, (Fore.GREEN,)),
            (40, (Fore.GREEN, Style.BRIGHT)),
            (45, (Fore.CYAN,)),
            (50, (Fore.CYAN, Style.BRIGHT)),
            (55, (Fore.RED,)),
            (60, (Fore.RED, Style.BRIGHT)),
    ):
        if max_value > value:
            return "".join(str(x) for x in style)
    return "".join(str(x) for x in (Fore.MAGENTA, Style.BRIGHT))


def get_text_color_small(value):
    default = "".join(str(x) for x in (Fore.MAGENTA, Style.BRIGHT))
    for max_value, style in (
            (0, (Fore.WHITE,)),
            (3, (Fore.WHITE, Style.BRIGHT)),
            (6, (Fore.YELLOW, Style.BRIGHT)),
            (9, (Fore.GREEN, Style.BRIGHT)),
            (12, (Fore.CYAN, Style.BRIGHT)),
    ):
        try:
            if max_value > value:
                return "".join(str(x) for x in style)
        except TypeError:
            return default
    return default

class Row:
    percentage_of_max_score = None
    efficiency = None
    general_attributes: List[Tuple[int, int]]= [(1,2),(1,3),(1,4),(1,6),(1,7),(2,0),(2,4),(2,5),(2,6)]

    def __init__(self, role_name="Overall"):
        self.role_name = role_name
        self.average_value = None
        self.elements = {
            "key": Element(2),
            "preferable": Element(1),
            "general": Element(0.5),
            None: Element(0.2),
        }

    def add(self, key, value, row_i, attribute_j):
        self.elements[None].add(value)

        if key is None:
            if (row_i, attribute_j) in self.general_attributes:
                self.elements["general"].add(value)
                return
        else:
            self.elements[key].add(value)

    def add_row_values(self, row: "Row"):
        for key, element in row.elements.items():
            self.elements[key].set(element)

    @property
    def average_value_repr(self):
        return self.average_value - 100

    def output(self, more_data=False):
        output = self.compile_average_value()

        string_representation = f"{self.average_value_repr :6.2f}"

        percentage = ""
        if self.percentage_of_max_score:
            if self.percentage_of_max_score >= 99.9:
                percentage = f"{get_text_color_small(300)}    <★>  "
            else:
                percentage = f"{get_text_color_small(self.percentage_of_max_score - 96)}{self.percentage_of_max_score:8.2f}%"

        print(f"{self.role_name: <10}: {get_text_color(self.average_value_repr)}{string_representation}{Style.RESET_ALL}"
              f"{percentage}"
              f"{Style.RESET_ALL} eff:"
              f"{get_text_color_small(self.efficiency - 100)}{self.efficiency:4.0f}%{Style.RESET_ALL}")
        if more_data:
            print(output)
        return string_representation

    def compile_average_value(self):
        output = ""
        if self.average_value is not None:
            return self.average_value

        overall = 0
        divisor = 0
        many_value_corrector = 1
        for key, element in self.elements.items():
            average = element.get_average()
            output += f"{key}: {average:.2f}, "

            overall += average * element.weight
            divisor += element.weight

            many_value_corrector += element.number_of_attributes * max(element.weight, 1) * .003
        self.average_value = (overall / divisor) * 8 * many_value_corrector
        return output

    @staticmethod
    def get_bar_string(value):
        bar_score = int(value / 2.5)
        bar_mid_point = 16
        bar = f"|{'=' * (min(bar_score, bar_mid_point))}{' ' * (bar_mid_point - max(bar_score, 0))}|{'=' * (bar_score - bar_mid_point)}{' ' * (bar_mid_point - max((bar_score - bar_mid_point), 0))}|"
        return bar


class Gatherer:
    def __init__(self, role_name="Overall"):
        self.role_name = role_name
        self.rows: tuple[Row, Row, Row] = (Row(), Row(), Row())
        self.complete_data: Row = None

    def reset(self):
        self.rows: tuple[Row, Row, Row] = (Row(), Row(), Row())
        self.complete_data: Row = None

    def output(self):
        self.compile_complete_data()
        self.complete_data = self.complete_data.output()

    def compile_complete_data(self):
        if self.complete_data is not None:
            return

        self.complete_data = Row(self.role_name)
        for row in self.rows:
            self.complete_data.add_row_values(row)
        self.complete_data.compile_average_value()

    def add_to_row(self, row_i, attribute_number, value, importance=None):
        self.rows[row_i].add(importance, value, row_i, attribute_number)

    def calculate_efficiency(self, main_processor):
        self.complete_data.efficiency = 5 * self.complete_data.average_value / main_processor.base_line_gatherer.complete_data.average_value


class RoleGatherer(Gatherer):
    best_score_in_team = "???"

    def __init__(self, role_name, role_config):
        super().__init__(role_name)
        self.role_config = role_config

    def add_to_row(self, row_i, attribute_number, value, importance=None):
        self.rows[row_i].add(self.role_config[row_i][attribute_number], value, row_i, attribute_number)


class BaseLineGatherer(Gatherer):
    def add_to_row(self, row_i, attribute_number, value, importance=None):
        self.rows[row_i].elements[None].add(value)
