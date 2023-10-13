from collections import defaultdict
from typing import List, Dict

from utils.staffer_config import StaffAttributes, RoleConfig
from utils.staffer_roles import get_coach_roles, get_head_coach

input_file = "C:\\Users\\Soeren\\Documents\\Sports Interactive\\Football Manager 2023\\staff_hsv.rtf"

file_name = "potentional coaches"
input_file = f"C:\\Users\\Soeren\\Documents\\Sports Interactive\\Football Manager 2023\\{file_name}.rtf"


def main(input_file_path: str, roles_configs: List[RoleConfig]):
    attribute_order_is_set = False
    attribute_order = []
    staff_attributes: Dict[str, StaffAttributes] = defaultdict(dict)

    with open(input_file_path, "r", encoding="utf8") as f:
        for line in f.readlines():
            data = line.split("|")
            if len(data) < 4:
                continue
            staff_name = data[2].strip()
            data = data[4:-1]

            if not attribute_order_is_set:
                attribute_order = [header.strip().lower() for header in data]
                attribute_order_is_set = True
                continue

            for attribute_name, value in zip(attribute_order, data):
                try:
                    value = int(value)
                except ValueError as e:
                    if not staff_name.strip():
                        break
                    raise ValueError(f"Failed to parse data for '{staff_name}' with data: {data}")
                staff_attributes[staff_name][attribute_name] = value

    for roles_config in roles_configs:
        for staffer, attributes in staff_attributes.items():
            roles_config.evaluate_staffer(staffer, attributes)

        roles_config.output()


if __name__ == "__main__":
    from colorama import init as colorama_init
    colorama_init()
    print(file_name)
    main(input_file, get_head_coach())
