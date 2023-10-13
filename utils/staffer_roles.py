from typing import List

from utils.staffer_config import RoleConfig, Attr, ATTRIBUTE_NAME


def get_with_same_weight(attributes: List[ATTRIBUTE_NAME], weight=2) -> List[Attr]:
    return [
        Attr(attribute, weight) for attribute in attributes
    ]


def get_coach_default_attributes(weight=2) -> List[Attr]:
    return get_with_same_weight(["det", "dis", "mot"], weight)


# 'ada', 'ana d', 'att', 'def', 'det', 'fit', 'gkd', 'gkh', 'gks', 'judge a', 'judge p', 'jud sa', 'dis', 'men', 'mot', 'negotiating', 'mgm', 'phy', 'sps', 'tco', 'tac knw', 'tec', 'youth'


def get_head_coach() -> List[RoleConfig]:
    return [
        RoleConfig("Head Coach", get_with_same_weight(['judge a', 'judge p', 'tac knw', 'mgm', 'mot'])),
        RoleConfig("Head Coach Youth", get_with_same_weight(['judge a', 'judge p', 'tac knw', 'mgm', 'mot', 'youth'])),
        RoleConfig("Assistant Coach", get_with_same_weight(['judge a', 'judge p', 'mgm'])),
        RoleConfig("Assistant Coach Youth", get_with_same_weight(['judge a', 'judge p', 'mgm', 'youth'])),
    ]


def get_coach_roles() -> List[RoleConfig]:
    # source: https://fmcalc.com
    return [
        RoleConfig("GK Shot Stop", [Attr("gks", 9)] + get_coach_default_attributes(), normalize=False),
        RoleConfig("GK Handling", [Attr("gkh", 6), Attr("gkd", 3)] + get_coach_default_attributes(), normalize=False),
        RoleConfig("Defending Tac", [Attr("def", 6), Attr("tco", 3)] + get_coach_default_attributes(), normalize=False),
        RoleConfig("Defending Tec", [Attr("def", 6), Attr("tec", 3)] + get_coach_default_attributes(), normalize=False),
        RoleConfig("Attacking Tac", [Attr("att", 6), Attr("tco", 3)] + get_coach_default_attributes(), normalize=False),
        RoleConfig("Attacking Tec", [Attr("att", 6), Attr("tec", 3)] + get_coach_default_attributes(), normalize=False),
        RoleConfig("Possession Tac", [Attr("men", 6), Attr("tco", 3)] + get_coach_default_attributes(), normalize=False),
        RoleConfig("Possession Tec", [Attr("men", 6), Attr("tec", 3)] + get_coach_default_attributes(), normalize=False),
        RoleConfig("Fitness", [Attr("fit", 9)] + get_coach_default_attributes(), normalize=False),
    ]

