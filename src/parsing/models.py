# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  models.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: stephanie <stephanie@student.42.fr>       +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/26 17:40:32 by stmaire         #+#    #+#               #
#  Updated: 2026/06/08 15:33:51 by stephanie       ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Literal

"""
Pydantic models for validating the drone simulation map configuration.

This module defines the data structures and validation rules required
to ensure that a parsed map file is syntactically and logically correct
before initializing the simulation.
"""


class Zone(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str  # Retrait de min_length=1 (déjà garanti par ton Regex de parsing)
    x: int
    y: int
    is_start: bool
    is_end: bool
    zone: Literal['normal', 'blocked', 'restricted', 'priority'] = 'normal'
    color: str | None = None
    max_drones: int = 1  # Retrait de ge=1
    line_num: int = Field(exclude=True)


class Connection(BaseModel):
    zone1: str  # Retrait de min_length=1
    zone2: str  # Retrait de min_length=1
    max_link_capacity: int  # Retrait de ge=1
    line_num: int = Field(exclude=True)


class MapConfigModel(BaseModel):
    model_config = ConfigDict(extra='forbid')
    nb_drones: int  # Retrait de ge=1 (déjà géré par ton parser)
    zones: list[Zone]
    connections: list[Connection]

    @model_validator(mode='after')
    def validate_config(self) -> 'MapConfigModel':
        start_zone_lines: list[int] = []
        end_zone_lines: list[int] = []
        zones_names: set[str] = set()
        seen_zone_coord: set[tuple[int, int]] = set()
        seen_connection: set[tuple[str, str]] = set()

        for zone in self.zones:
            # --- AJOUT MINIMUM : Validation de max_drones avec ligne ---
            if zone.max_drones < 1:
                raise ValueError(f"Line {zone.line_num}: max_drones must be at least 1.")

            if zone.name in zones_names:
                raise ValueError(f"Line {zone.line_num}: Cannot use the same "
                                 f"zone name '{zone.name}' more than once.")
            zones_names.add(zone.name)
            if zone.is_start is True:
                if (
                    zone.max_drones is not None
                    and zone.max_drones < self.nb_drones
                ):
                    raise ValueError(f"Line {zone.line_num}: "
                                     f"start_zone capacity "
                                     f"(max_drones= {zone.max_drones})"
                                     f" cannot be less than the total number "
                                     f"of drones ({self.nb_drones}).")
                start_zone_lines.append(zone.line_num)
            if zone.is_end is True:
                if zone.zone == 'blocked':
                    raise ValueError(
                        f"Invalid card: the end_zone is a blocked_zone."
                    )
                end_zone_lines.append(zone.line_num)

            coord = (zone.x, zone.y)
            if coord in seen_zone_coord:
                raise ValueError(f"Line {zone.line_num}: Another zone already "
                                 f"exists at these coordinates: {coord}")
            seen_zone_coord.add(coord)

        number_start_zones: int = len(start_zone_lines)
        number_end_zones: int = len(end_zone_lines)
        if number_start_zones == 0:
            raise ValueError("There is no start_hub in the map.")
        if number_end_zones == 0:
            raise ValueError("There is no end_hub in the map.")
        if number_start_zones > 1:
            raise ValueError(
                f"There must be exactly one start_hub. "
                f"Found {number_start_zones} at lines {start_zone_lines}"
                )
        if number_end_zones > 1:
            raise ValueError(
                f"There must be exactly one end_hub. "
                f"Found {number_end_zones} at lines {end_zone_lines}"
                )

        for connection in self.connections:
            # --- AJOUT MINIMUM : Validation de max_link_capacity avec ligne ---
            if connection.max_link_capacity < 1:
                raise ValueError(f"Line {connection.line_num}: max_link_capacity must be at least 1.")

            connection_tuple = (connection.zone1, connection.zone2)
            reverse_connection_tuple = (connection.zone2, connection.zone1)

            if (
                connection_tuple in seen_connection
                    or reverse_connection_tuple in seen_connection
                    ):
                raise ValueError(f"Line {connection.line_num}: "
                                 f"The same connection must not appear "
                                 f"more than once (e.g., a-b and b-a "
                                 f"are considered duplicates).")

            if connection.zone1 not in zones_names:
                raise ValueError(f"Line {connection.line_num}: "
                                 f"'{connection.zone1}' refers to an unknown "
                                 f"zone.")
            if connection.zone2 not in zones_names:
                raise ValueError(f"Line {connection.line_num} "
                                 f"'{connection.zone2}' refers to an unknown "
                                 f"zone.")
            if connection.zone1 == connection.zone2:
                raise ValueError(f"Line {connection.line_num}: A zone cannot "
                                 f"connect to itself, "
                                 f"zone1 and zone2 must be different.")
            seen_connection.add(connection_tuple)

        return self
