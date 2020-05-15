from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, TypeVar, Union

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
    type: PatternType
    repeated: bool = False
    optional: bool = False


class CommandPattern(BasePattern):
    type: PatternType = Field(default=PatternType.COMMAND.value, const=True)
    command: Command


class ArgumentPattern(BasePattern):
    type: PatternType = Field(default=PatternType.ARGUMENT.value, const=True)
    argument: Argument


class OptionPattern(BasePattern):
    type: PatternType = Field(default=PatternType.OPTION.value, const=True)
    option: Option
    argument: Optional[ArgumentPattern]


class GroupPattern(BasePattern):
    type: PatternType = Field(default=PatternType.GROUP.value, const=True)
    exclusive: bool = False
    patterns: List[Union[GroupPattern, CommandPattern, ArgumentPattern, OptionPattern]]


SupportedPatternT = TypeVar("SupportedPatternT", GroupPattern, CommandPattern, ArgumentPattern, OptionPattern)

GroupPattern.update_forward_refs()


class Cli(BaseModel):
    name: str
    option_separators_long: List[str] = ["=", " "]
    option_separators_short: List[str] = [" ", ""]
    option_prefix_long: str = "--"
    option_prefix_short: str = "-"
    pattern_groups: List[GroupPattern]

    @validator("pattern_groups")
    def check_pattern_groups(cls, v):
        if not v:
            raise ValueError("at least one pattern group should be included")
        return v


class OpenAutoCompletion(BaseModel):
    version: str = Field(regex=r"^\d+.\d+$")


class Specification(BaseModel):
    openautocompletion: OpenAutoCompletion
    components: Components
    cli: Cli
