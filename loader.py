# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  loader.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: stmaire <stmaire@student.42.fr>           +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/05/26 17:40:21 by stmaire         #+#    #+#               #
#  Updated: 2026/05/26 17:40:22 by stmaire         ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from pathlib import Path


class Loader:
    def load_file(self, file_path: str) -> str:
        """
        Loads a configuration file.
        Handles cases: missing file, empty file, permission error
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Missing file: '{path.name}' not found")

        try:
            with open(path, mode="r", encoding="utf-8") as f:
                content = f.read().strip()
        except PermissionError:
            raise PermissionError(
                f"You don't have permission for the directory '{path.parent}'"
                f"or for the file'{path.name}'"
            )
        except IsADirectoryError:
            raise IsADirectoryError(
                f"Expected a file, but '{path.name}' is a directory."
            )

        if not content:
            raise ValueError(f"file '{path.name}' is empty.")

        return content
