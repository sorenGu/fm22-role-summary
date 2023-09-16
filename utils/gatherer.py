import argparse
import json
import os
from json import JSONDecodeError

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
            (25, (Fore.RED,)),
            (30, (Fore.RED, Style.BRIGHT)),
            (35, (Fore.YELLOW,)),
            (40, (Fore.YELLOW, Style.BRIGHT)),
            (45, (Fore.GREEN,)),
            (50, (Fore.GREEN, Style.BRIGHT)),
            (55, (Fore.CYAN,)),
            (60, (Fore.CYAN, Style.BRIGHT)),
    ):
        if max_value > value:
            return "".join(str(x) for x in style)
    return "".join(str(x) for x in (Fore.MAGENTA, Style.BRIGHT))

class Row:
    percentage_of_max_score = None

    def __init__(self, role_name="Overall"):
        self.role_name = role_name
        self.average_value = None
        self.elements = {
            "key": Element(1.5),
            "preferable": Element(1),
            None: Element(0.3),
        }

    def add(self, key, value):
        self.elements[key].add(value)
        if key is not None:
            self.elements[None].add(value)

    def add_row_values(self, row: "Row"):
        for key, element in row.elements.items():
            self.elements[key].set(element)

    def output(self, more_data=False):
        output = self.compile_average_value()

        string_representation = f"{self.average_value :6.2f}"

        percentage = ""
        if self.percentage_of_max_score:
            if self.percentage_of_max_score >= 99.9:
                percentage = "    <★>"
            else:
                percentage = f"{self.percentage_of_max_score:8.2f}%"

        print(f"{self.get_bar_string(self.average_value)} {self.role_name: >11}:{get_text_color(self.average_value)}{string_representation}{percentage}{Style.RESET_ALL}")
        if more_data:
            print(output)
        return string_representation

    def compile_average_value(self):
        output = ""
        if self.average_value is not None:
            return output

        overall = 0
        divisor = 0
        for key, element in self.elements.items():
            average = element.get_average()
            output += f"{key}: {average:.2f}, "

            overall += average * element.weight
            divisor += element.weight
        self.average_value = ((overall / divisor) - 10) * 10
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

    def output(self, args: argparse.Namespace):
        self.compile_complete_data()
        self.complete_data = self.complete_data.output()

        old_data = self.get_old_data()
        if args.old_data:
            print("------------------------\nold data:")
            for data in old_data["data"]:
                print("-", data)

        old_data["data"] = old_data["data"][:4]
        old_data["data"].insert(0, self.complete_data)

        if args.save_key:
            if "key_data" not in old_data:
                old_data["key_data"] = {}
            old_data["key_data"][args.save_key] = self.complete_data

        self.save_old_data(old_data)

    def compile_complete_data(self):
        if self.complete_data is not None:
            return

        self.complete_data = Row(self.role_name)
        for row in self.rows:
            self.complete_data.add_row_values(row)
        self.complete_data.compile_average_value()

    def add_to_row(self, row_i, attribute_number, importance, value):
        self.rows[row_i].add(importance, value)

    def save_old_data(self, old_data):
        with open("old_data.json", "w") as f:
            json.dump(old_data, f)

    def get_old_data(self):
        try:
            with open("old_data.json", "r") as f:
                return json.load(f)
        except (JSONDecodeError, FileNotFoundError):
            pass
        return {"data": []}


class RoleGatherer(Gatherer):
    def __init__(self, role_name, role_config):
        super().__init__(role_name)
        self.role_config = role_config

    def add_to_row(self, row_i, attribute_number, importance, value):
        self.rows[row_i].add(self.role_config[row_i][attribute_number], value)
