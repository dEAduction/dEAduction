"""
#####################################
# request.py : Lean Request objects #
#####################################

Author(s)     : Patrick Massot   <patrick.massot@math.cnrs.fr>
Revised       : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s): Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date          : July 2020

Copyright (c) 2020 the dEAduction team

This file is part of d∃∀duction.

    d∃∀duction is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    d∃∀duction is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with d∃∀duction. If not, see <https://www.gnu.org/licenses/>.
"""

from dataclasses import dataclass
from typing import (
    Optional,
    List,
    NewType,
    ClassVar
)

import json

from enum import Enum

@dataclass
class Request:
    command: ClassVar[str] = ''

    def __post_init__(self):
        self.seq_num = 0

    def to_json_dict(self) -> str:
        dic = self.__dict__.copy()
        dic['command'] = self.command
        return dic 

@dataclass
class SyncRequest(Request):
    command  = 'sync'
    file_name: str
    content  : Optional[str] = None

    def to_json(self):
        dic = self.__dict__.copy()
        dic['command'] = 'sync'
        if dic['content'] is None:
            dic.pop('content')
        return json.dumps(dic)

@dataclass
class CompleteRequest(Request):
    command = 'complete'
    file_name: str
    line: int
    column: int
    skip_completions: bool = False

@dataclass
class InfoRequest(Request):
    command = 'info'
    file_name: str
    line: int
    column: int

@dataclass
class SearchRequest(Request):
    command = 'search'
    query: str

@dataclass
class HoleCommandsRequest(Request):
    command = 'hole_commands'
    file_name: str
    line: int
    column: int

@dataclass
class AllHoleCommandsRequest(Request):
    command = 'all_hole_commands'
    file_name: str

@dataclass
class HoleRequest(Request):
    command = 'hole'
    file_name: str
    line: int
    column: int
    action: str

@dataclass
class RoiRange:
    begin_line: int
    end_line: int

@dataclass
class FileRoi:
    file_name: str
    ranges: List[RoiRange]

    def to_dict(self):
        return {'file_name': self.file_name,
                'ranges': [rr.__dict__ for rr in self.ranges] }

CheckingMode = Enum('CheckingMode',
    'nothing visible-lines visible-lines-and-above visible-files open-files')
@dataclass
class RoiRequest(Request):
    command = 'roi'
    mode: CheckingMode
    files: List[FileRoi]

    def to_json(self) -> str:
        dic = self.__dict__.copy()
        dic['command'] = 'roi'
        dic['mode'] = dic['mode'].name
        dic['files'] = [fileroi.to_dict() for fileroi in dic['files']]

        return json.dumps(dic)

@dataclass
class SleepRequest(Request):
    command = 'sleep'

@dataclass
class LongSleepRequest(Request):
    command = 'long_sleep'
