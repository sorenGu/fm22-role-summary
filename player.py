import argparse
import datetime

from utils.config import DefaultConfig
from utils.data_gatherer import TeamDataWithTeam, TeamDataAllRoles, PlayerDataAllRoles
from utils.role_config import TeamConfig
from utils.screenshot import ConfiguredScreenshotter, get_player_name, gather_attributes

parser = argparse.ArgumentParser(description='Process command-line arguments.')
parser.add_argument('-t', '--team', required=True, type=str, help='Team name', default=None)
parser.add_argument('--rm', required=False, type=str, help='Remove player from team', default=None)
parser.add_argument('-s', '--save', action='store_true')


def main(team, save, **kwargs):
    start = datetime.datetime.now()
    team_config = TeamConfig(team)
    team_data = TeamDataWithTeam(team_config)
    player_name = read_data(team_data)

    team_data.display_all_roles(highlighted_name=player_name)
    if save:
        team_data.save_config()

    print(f"Time: {datetime.datetime.now() - start}")


def player_all_roles(team, **kwargs):
    start = datetime.datetime.now()
    team_config = TeamConfig(team)
    team_data = PlayerDataAllRoles(team_config)

    read_data(team_data, print_data=False)
    team_data.sort_by_value()
    team_data.display_all_roles()


    print(f"Time: {datetime.datetime.now() - start}")


def read_data(team_data, print_data=True):
    screenshotter = ConfiguredScreenshotter(DefaultConfig)
    player_name = get_player_name(screenshotter)
    attributes = gather_attributes(screenshotter)
    team_data.add_player_to_team(player_name, attributes, print_data=print_data)
    return player_name


def remove_player_from_team(player, team):
    team_config = TeamConfig(team)
    team_data = TeamDataWithTeam(team_config)

    team_data.remove_player(player)
    team_data.save_config()


if __name__ == '__main__':
    args: argparse.Namespace = parser.parse_args()
    if not args.rm:
        main(args.team, args.save)
    else:
        if not args.team:
            print("need team to remove player from (-t)")
        remove_player_from_team(args.rm, args.team)

