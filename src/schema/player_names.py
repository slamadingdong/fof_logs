"""Convenience dataclasses to hold the names of all players on the field."""
from dataclasses import dataclass


@dataclass
class PlayerNames:
    # Offensive players. Not every position will have a name since not every
    # position will be on the field for every play.
    qb_name: str = ''
    rb_name: str = ''
    fb_name: str = ''
    te_name: str = ''
    x_name: str = ''
    z_name: str = ''
    slot_1_name: str = ''
    slot_2_name: str = ''
    lt_name: str = ''
    lg_name: str = ''
    c_name: str = ''
    rg_name: str = ''
    rt_name: str = ''

    # Defensive players. Which are filled will depend on offensive personnel
    # and whether this is a 4-3 or 3-4 defense.
    rcb_name: str = ''
    lcb_name: str = ''
    nb_name: str = ''
    db_name: str = ''
    ss_name: str = ''
    fs_name: str = ''
    lde_name: str = ''
    ldt_name: str = ''
    rdt_name: str = ''
    nt_name: str = ''
    rde_name: str = ''
    slb_name: str = ''
    wlb_name: str = ''
    mlb_name: str = ''
    silb_name: str = ''
    wilb_name: str = ''
    ball_carrier_name: str = ''
    primary_receiver_name: str = ''
    secondary_receiver_name: str = ''
    targeted_receiver_name: str = ''
