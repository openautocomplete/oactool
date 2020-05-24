import re
import subprocess
from typing import Iterable, List, Tuple

from oactool.schema import Cli, Components, GroupPattern, OpenAutoComplete, Option, OptionPattern, Specification


def clean_description(s: str) -> str:
    s = re.sub(pattern=r"-[ \t]*\n[\s]+", repl="", string=s)
    s = re.sub(pattern=r"[ \n\t\r]+", repl=" ", string=s, flags=re.MULTILINE)
    return s.strip()


def make_option(options: List[str], description: str) -> OptionPattern:
    options_short = []
    options_long = []
    options_old = []

    for option in options:
        if match := re.match(r"^-([^-])$", option):
            options_short += [match[1]]

        elif match := re.match(r"^--(.*)$", option):
            options_long += [match[1]]

        elif match := re.match(r"^-(.+)$", option):
            options_old += [match[1]]

    if not options_old:
        return OptionPattern(
            type="option",
            optional=True,
            option=Option(names_short=options_short, names_long=options_long, description=description),
        )
    else:
        return OptionPattern(
            type="option",
            optional=True,
            option=Option(names_short=options_short, names_long=options_old, description=description),
            prefix_long="-",
            separators_long=[" "],
        )


def parse(command: str) -> Iterable[Tuple[List[str], str]]:
    man = subprocess.getoutput(f"man {command} | col -b")

    for i in re.finditer(pattern=r"^\s+((?:(?:(?:-\S+))[\s|])+)\s*((?:.+\n)+)$", string=man, flags=re.MULTILINE):
        options = re.findall(pattern=r"-[^=\s\[,]+", string=i[1])
        description = clean_description(i[2]).capitalize()

        yield options, description


def do_parse_man(command: str) -> Specification:
    main_pattern = GroupPattern(
        type="group", patterns=[make_option(options, description) for options, description in parse(command)],
    )

    return Specification(
        openautocomplete=OpenAutoComplete(version="1.0"),
        components=Components(),
        cli=Cli(name=command, pattern_groups=[main_pattern]),
    )
