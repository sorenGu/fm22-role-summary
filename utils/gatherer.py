import argparse
import json
from json import JSONDecodeError
from termcolor import colored, cprint
import os
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
    for max_value, color in (
        (0, "grey"),
        (20, "light_grey"),
        (25, "yellow"),
        (30, "light_yellow"),
        (35, "green"),
        (40, "light_green"),
        (45, "blue"),
        (50, "light_blue"),
        (55, "light_red"),
        (60, "light_magenta")
    ):
        colored(color, color)
        if max_value > value:
            return color
    return "light_cyan"

class Row:
    def __init__(self, role_name="Overall"):
        self.role_name = role_name
        self.average_value = None
        self.elements = {
            "key": Element(1.5),
            "preferable": Element(1),
            None: Element(0.5),
        }

    def add(self, key, value):
        self.elements[key].add(value)
        if key is not None:
            self.elements[None].add(value)

    def add_row_values(self, row: "Row"):
        for key, element in row.elements.items():
            self.elements[key].set(element)

    def output(self, more_data=False, max_score=None):
        output = self.compile_average_value()

        string_representation = f"{self.average_value :6.2f}"

        percentage = ""
        if max_score:
            if max_score == self.average_value:
                percentage = "    <★>"
            else:
                percentage = f"{self.average_value/max_score * 100:8.2f}%"

        cprint(f"{self.get_bar_string(self.average_value)} {self.role_name: >7}:{string_representation}{percentage}", get_text_color(self.average_value))
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

    def output(self, args: argparse.Namespace, max_score=None):
        self.compile_complete_data()
        self.complete_data = self.complete_data.output(max_score=max_score)

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
