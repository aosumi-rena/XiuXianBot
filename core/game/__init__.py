"""
Game mechanics package for XiuXianBot.

This package contains the core game mechanics and calculations
that are shared across different platform adapters.
"""

from core.game.mechanics import (
    calculate_cultivation_gain,
    start_cultivation,
    calculate_hunt_rewards,
    calculate_ascension_chance,
    get_daily_element
)

from core.game.elements import (
    ELEMENTS,
    RESTRAINED_ELEMENTS,
    MUTUAL_ELEMENTS,
    get_element_relationship,
    get_element_multipliers,
    get_element_description
)

__all__ = [
    'calculate_cultivation_gain',
    'start_cultivation',
    'calculate_hunt_rewards',
    'calculate_ascension_chance',
    'get_daily_element',
    'ELEMENTS',
    'RESTRAINED_ELEMENTS',
    'MUTUAL_ELEMENTS',
    'get_element_relationship',
    'get_element_multipliers',
    'get_element_description'
]
