from pathlib import Path
from typing import Any
from loader import Loader
import re


class MapParser:
    def split_lines(self, raw_input: Loader):
        lines = raw_input.split("\n")
        return lines

    def clean_lines(self, lines: list[str]) -> str:
        self.clean_lines = []
        for line in lines:
            clean_line = line.split("#")[0].strip()
            if not clean_line == "":
                self.clean_lines.append(clean_line)
        return self.clean_lines

    def get_raw_dict(self, clean_lines: list[str]):
        for clean_line in clean_lines:








