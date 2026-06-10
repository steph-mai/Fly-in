# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  errors.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: stmaire <stmaire@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/06/10 15:35:59 by stmaire         #+#    #+#               #
#  Updated: 2026/06/10 15:36:00 by stmaire         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #
"""Module defining custom exceptions for the Fly-In simulation."""


class FlyInError(Exception):
    """
    Base class for all exceptions in the simulation.

    Attributes:
        message (str): A descriptive error message.
    """

    def __init__(self, message: str) -> None:
        """
        Initialize the error.

        Args:
            message: The human-readable error description.
        """
        super().__init__(message)
        self.message: str = message


class MapSyntaxError(FlyInError):
    """Raised when the map parser fails to process the input file."""

    def __str__(self) -> str:
        """
        Return the formatted error message.

        Returns:
            str: A string tagged with [SYNTAX ERROR].
        """
        return f"[SYNTAX ERROR] {self.message}"


class MapLogicalError(FlyInError):
    """Raised when Pydantic rejects the map according to business rules."""

    def __str__(self) -> str:
        """
        Return the formatted error message.

        Returns:
            str: A string tagged with [LOGICAL ERROR].
        """
        return f"[LOGICAL ERROR] {self.message}"


class MapLoadError(FlyInError):
    """Raised when a map file is not found, unreadable, or inaccessible."""

    def __str__(self) -> str:
        """
        Return the formatted error message.

        Returns:
            str: A string tagged with [SYSTEM ERROR].
        """
        return f"[SYSTEM ERROR] {self.message}"
