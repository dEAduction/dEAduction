"""
#######################################
# response.py : Lean response objects #
#######################################

Author(s)      : Patrick Massot   <patrick.massot@math.cnrs.fr>
Revised        : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Maintainers(s) : Florian Dupeyron <florian.dupeyron@mugcat.fr>
Date           : July 2020

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

from enum import Enum

@dataclass
class Response:
    response: ClassVar[str]

    @classmethod
    def from_dict(cls, dic):
        return cls(**dic)
            
############################################
# Messages and tasks
############################################
@dataclass
class Message:
    Severity = Enum("Severity", "information warning error")

    file_name   : str
    severity    : Severity
    caption     : str
    text        : str

    pos_line    : int
    pos_col     : int
    end_pos_line: Optional[int] = None
    end_pos_col : Optional[int] = None

    @classmethod
    def from_dict(cls, dic):
        dic["severity"] = getattr(Message.Severity, dic["severity"])
        return cls(**dic)

@dataclass
class AllMessagesResponse(Response):
    response = "all_messages"
    msgs: List[Message]

    @classmethod
    def from_dict(cls, dic):
        return cls([Message.from_dict(msg) for msg in dic["msgs"]])

@dataclass
class Task:
    file_name   : str
    pos_line    : int
    pos_col     : int

    desc        : str

    end_pos_line: Optional[int] = None
    end_pos_col : Optional[int] = None

@dataclass
class CurrentTasksResponse(Response):
    response = "current_tasks"

    is_running: bool
    tasks     : List[Task]
    cur_task  : Optional[Task] = None

    @classmethod
    def from_dict(cls, dic):
        dic["tasks"] = [Task(**task) for task in dic.pop("tasks")]
        return cls(**dic)

############################################
# Command responses
############################################
@dataclass
class CommandResponse(Response):
    response = "ok"

    seq_num: int
    message: Optional[str]

    @classmethod
    def from_dict(cls,dic):
        if not "message" in dic: dic["message"]=""
        return super().from_dict(dic)

@dataclass
class ErrorResponse(Response):
    response = "error"
    message: str
    seq_num: Optional[int]

############################################
# Completion
############################################
@dataclass
class CompletionCandidate:
    type_        : Optional[str]
    tactic_params: Optional[str]
    text         : str
    doc          : Optional[str]

    @classmethod
    def from_dict(cls, dic):
        dic["type_"] = dic.pop("type")
        return cls(**dic)

@dataclass
class CompleteResponse(CommandResponse):
    prefix     : str
    completions: List[CompletionCandidate]

    @classmethod
    def from_dict(cls, dic):
        if not "message" in dic: dic["message"] = ""

        dic["completions"] = [CompletionCandidate.from_dict(cdt)
                              for cdt in dic.pop("completions")]
        return cls(**dic)

############################################
# Info response
############################################
GoalState = NewType('GoalState', str)

@dataclass
class InfoSource:
    line  : int
    column: int
    file  : Optional[str]

@dataclass
class WidgetInfo:
    line: int
    column: int
    id: int

@dataclass
class InfoRecord:
    full_id         : Optional[str]        = None
    text            : Optional[str]        = None
    type_           : Optional[str]        = None
    doc             : Optional[str]        = None
    source          : Optional[InfoSource] = None
    state           : Optional[GoalState]  = None
    tactic_param_idx: Optional[int]        = None
    tactic_params   : Optional[List[str]]  = None
    widget          : Optional[WidgetInfo] = None

    @classmethod
    def from_dict(cls, dic):
        if 'full-id' in dic:
            dic['full_id'] = dic.pop('full-id')
        if 'type' in dic:
            dic['type_'] = dic.pop('type')
        if 'source' in dic:
            dic['source'] = InfoSource(**dic.pop('source'))
        if 'widget' in dic:
            dic['widget'] = WidgetInfo(**dic.pop('widget'))

        return cls(**dic)

@dataclass
class InfoResponse(CommandResponse):
    record: Optional[InfoRecord]

    @classmethod
    def from_dict(cls, dic):
        if not 'message' in dic: dic["message"] = ""
        dic['record'] = InfoRecord.from_dict(dic.pop('record'))
        return cls(**dic)

############################################
# Search response
############################################
@dataclass
class SearchItem:
    source: Optional[InfoSource]
    text  : str
    type_ : str
    doc   : Optional[str]

    @classmethod
    def from_dict(cls, dic):
        dic['type_'] = dic.pop('type')
        return cls(**dic)

@dataclass
class SearchResponse(CommandResponse):
    results: List[SearchItem]

    @classmethod
    def from_dict(cls, dic):
        if not "message" in dic: dic["message"] = ""

        dic['results'] = [SearchItem.from_dict(si)
                          for si in dic.pop('results')]
        return cls(**dic)

############################################
# Hole commands
############################################
@dataclass
class HoleCommandAction:
    name       : str
    description: str

@dataclass
class Position:
    line  : int
    column: int

@dataclass
class HoleCommands:
    file_name: str
    start    : Position
    end      : Position
    results  : List[HoleCommandAction]

    @classmethod
    def from_dict(cls, dic):
        dic['results'] = [HoleCommandAction(**hc)
                          for hc in dic.pop('results')]
        return cls(**dic)

@dataclass
class HoleCommandsResponse(CommandResponse, HoleCommands):
    @classmethod
    def from_dict(cls,dic):
        if not "message" in dic: dic["message"]=""
        return super().from_dict(dic)

@dataclass
class AllHoleCommandsResponse(CommandResponse):
    holes: List[HoleCommands]

    @classmethod
    def from_dict(cls, dic):
        if not "message" in dic: dic["message"]=""

        dic['holes'] = [HoleCommands.from_dict(hole)
                          for hole in dic.pop('holes')]
        return cls(**dic)

@dataclass
class HoleReplacementAlternative:
    code       : str
    description: str

@dataclass
class HoleReplacements:
    file_name   : str
    start       : Position
    end         : Position
    alternatives: List[HoleReplacementAlternative]

    @classmethod
    def from_dict(cls, dic):
        dic['alternatives'] = [HoleReplacementAlternative(**alt)
                               for alt in dic.pop('alternatives')]
        return cls(**dic)

@dataclass
class HoleResponse(CommandResponse):
    replacements: Optional[HoleReplacements]
    message     : Optional[str]

    @classmethod
    def from_dict(cls, dic):
        if not "message" in dic: dic["message"] = ""

        if 'replacements' in dic:
            dic['replacements'] = HoleReplacements.from_dict(
                    dic.pop('replacements'))
        return cls(**dic)

############################################
# Response object factory
############################################
def from_dict(dic: dict) -> Response:
    response = dic.pop('response')
    if response == 'ok':
        if 'completions' in dic:
            return CompleteResponse.from_dict(dic)
        elif 'record' in dic:
            return InfoResponse.from_dict(dic)
        elif 'results' in dic and 'start' in dic:
            return HoleCommandsResponse.from_dict(dic)
        elif 'results' in dic:
            return SearchResponse.from_dict(dic)
        elif 'holes' in dic:
            return AllHoleCommandsResponse.from_dict(dic)
        elif 'replacements' in dic:
            return HoleResponse.from_dict(dic)

    # Now try classes for messages that do have a helpful response field
    for cls in [AllMessagesResponse, CurrentTasksResponse, CommandResponse,
            ErrorResponse]:
        if response == cls.response: # type: ignore
            return cls.from_dict(dic) # type: ignore
    raise ValueError("Couldn't parse response string.")
