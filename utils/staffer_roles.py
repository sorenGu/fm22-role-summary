from typing import List

from utils.staffer_config import RoleConfig, Attr


def get_coach_default_attributes(weight=2) -> List[Attr]:
    return [
        Attr("det", weight),
        Attr("dis", weight),
        Attr("mot", weight),
    ]


# 'ada', 'ana d', 'att', 'def', 'det', 'fit', 'gkd', 'gkh', 'gks', 'judge a', 'judge p', 'jud sa', 'dis', 'men', 'mot', 'negotiating', 'mgm', 'phy', 'sps', 'tco', 'tac knw', 'tec', 'youth'


def get_coach_roles() -> List[RoleConfig]:
    # source: https://fmcalc.com
    return [
        RoleConfig("GK Shot Stop", [Attr("gks", 9)] + get_coach_default_attributes()),
        RoleConfig("GK Handling", [Attr("gkh", 6), Attr("gkd", 3)] + get_coach_default_attributes()),
        RoleConfig("Defending Tac", [Attr("def", 6), Attr("tco", 3)] + get_coach_default_attributes()),
        RoleConfig("Defending Tec", [Attr("def", 6), Attr("tec", 3)] + get_coach_default_attributes()),
        RoleConfig("Attacking Tac", [Attr("att", 6), Attr("tco", 3)] + get_coach_default_attributes()),
        RoleConfig("Attacking Tec", [Attr("att", 6), Attr("tec", 3)] + get_coach_default_attributes()),
        RoleConfig("Possession Tac", [Attr("men", 6), Attr("tco", 3)] + get_coach_default_attributes()),
        RoleConfig("Possession Tec", [Attr("men", 6), Attr("tec", 3)] + get_coach_default_attributes()),
        RoleConfig("Fitness", [Attr("fit", 9)] + get_coach_default_attributes()),
    ]
