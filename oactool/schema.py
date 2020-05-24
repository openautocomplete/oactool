from __future__ import annotations

from enum import Enum
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator


class Argument(BaseModel):
    name: Optional[str]
    description: Optional[str]


class Option(BaseModel):
    names_short: List[str] = []
    names_long: List[str] = []
    description: Optional[str]

    @root_validator
    def check_names(cls, values):
        if not (values.get("names_short") or values.get("names_long")):
            raise ValueError("at least one name should be included")
        return values


class Command(BaseModel):
    names: List[str]
    description: Optional[str]


class Components(BaseModel):
    arguments: Optional[Dict[str, Argument]]
    options: Optional[Dict[str, Option]]
    commands: Optional[Dict[str, Command]]


class PatternType(Enum):
    GROUP = "group"
    COMMAND = "command"
    ARGUMENT = "argument"
    OPTION = "option"


class BasePattern(BaseModel):
    type: str
    repeated: bool = False
    optional: bool = False


class CommandPattern(BasePattern):
    type: Literal["command"]
    command: Command


class ArgumentPattern(BasePattern):
    type: Literal["argument"]
    argument: Argument


class OptionPattern(BasePattern):
    type: Literal["option"]
    option: Option
    separators_long: List[str] = ["=", " "]
    separators_short: List[str] = [" ", ""]
    prefix_long: str = "--"
    prefix_short: str = "-"

    argument: Optional[ArgumentPattern]


class GroupPattern(BasePattern):
    type: Literal["group"]
    exclusive: bool = False
    patterns: List[Union[GroupPattern, CommandPattern, ArgumentPattern, OptionPattern]]


GroupPattern.update_forward_refs()


class Cli(BaseModel):
    name: str
    pattern_groups: List[GroupPattern]

    @validator("pattern_groups")
    def check_pattern_groups(cls, v):
        if not v:
            raise ValueError("at least one pattern group should be included")
        return v


class OpenAutoComplete(BaseModel):
    version: str = Field(regex=r"^\d+.\d+$")


class Specification(BaseModel):
    openautocomplete: OpenAutoComplete
    components: Components
    cli: Cli
