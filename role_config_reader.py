import argparse
from typing import Iterator

from utils.config import DefaultConfig
from utils.role_config import SaveRoleConfig
from utils.screenshot import ConfiguredScreenshotter

parser = argparse.ArgumentParser(description='Process command-line arguments.')
parser.add_argument('-r', '--role', type=str, help='Role name', default=None)
parser.add_argument('-a', '--all', type=str, help='All roles', default=None)


def main(role_name: str, force=False):
    role_config_saver = SaveRoleConfig(role_name, DefaultConfig, force)
    screenshotter = ConfiguredScreenshotter(DefaultConfig)
    is_goalkeeper = role_name.lower().startswith("gk")

    role_config = []
    for attribute_image in screenshotter.iterate_attribute_images(is_goalkeeper):
        importance = role_config_saver.get_importance(attribute_image)
        role_config.append(importance)

    role_config_saver.save_role_config(role_config)

def iterate_positions() -> Iterator[str]:
    o_default = ["DE", "SU", "AT"]
    o_defence = ["DE", "ST", "CO"]
    o_default_with_au = o_default + ["AU"]
    de_su = ["DE", "SU"]

    su_at = ["SU", "AT"]
    de = ["DE"]
    su = ["SU"]
    at = ["AT"]
    roles = {
        "GK": {
            "SK": o_default,
            "GK": de,
        },
        "DC": {
            "BPD": o_defence,
            "CD": o_defence,
            "LIB": de_su,
            "WCB": o_default,
            "NNC": o_defence
        },
        "DW": {
            "WB": o_default_with_au,
            "CWB": su_at,
            "IWB": o_default_with_au,
            "FB": o_default_with_au,
            "IFB": de,
            "NNF": de,
        },
        "DMC": {
            "DLP": de_su,
            "REG": su,
            "RP": su,
            "BMW": de_su,
            "VOL": su_at,
            "HB": de,
            "DM": de_su,
            "ANC": de,
        },
        "DMW": {
            "WB": o_default_with_au,
            "CWB": su_at,
            "IWB": o_default_with_au,
        },
        "MC": {
            "BTB": su,
            "AP": su_at,
            "CM": o_default_with_au,
            "MEZ": su_at,
            "DLP": de_su,
            "CAR": su,
            "RP": su,
            "BMW": de_su,
        },
        "MW": {
            "W": su_at,
            "IW": su_at,
            "WP": su_at,
            "DW": de_su,
            "WM": o_default_with_au,
        },
        "AMC": {
            "AP": su_at,
            "AM": su_at,
            "SS": at,
            "ENG": su,
            "TRE": at,
        },
        "AMW": {
            "W": su_at,
            "IW": su_at,
            "IF": su_at,
            "TRE": at,
            "AP": su_at,
            "RAU": at,
            "WTF": su_at,
        },
        "ST": {
            "AF": at,
            "TRE": at,
            "DLF": su_at,
            "PF": o_default,
            "POA": at,
            "FN": su,
            "TF": su_at,
            "CF": su_at,
        },
    }

    for position, roles in roles.items():
        for role, orientations in roles.items():
            for orientation in orientations:
                yield "_".join([position, role, orientation])


if __name__ == '__main__':
    args: argparse.Namespace = parser.parse_args()
    if args.all:
        for role in iterate_positions():
            if input(f"next role is {role}. skip= 's'") == "s":
                continue
            main(role, force=True)
    else:
        main(args.role)
