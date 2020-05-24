import argparse
import shlex
from collections import defaultdict
from typing import Dict, Iterable, List, Union

import click

from oactool.schema import (
    Argument,
    ArgumentPattern,
    Cli,
    CommandPattern,
    Components,
    GroupPattern,
    OpenAutoComplete,
    Option,
    OptionPattern,
    Specification,
)

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--command")
parser.add_argument("-s", "--short-option", default=list(), action="append")
parser.add_argument("-l", "--long-option", default=list(), action="append")
parser.add_argument("-o", "--old-option", default=list(), action="append")
parser.add_argument("-r", "--require-parameter", action="store_true")
parser.add_argument("-f", "--no-files", action="store_true")
parser.add_argument("-x", "--exclusive", action="store_true")
parser.add_argument("-n", "--condition")
parser.add_argument("-d", "--description")
parser.add_argument("-a", "--arguments")


def make_arg(optional: bool) -> ArgumentPattern:
    return ArgumentPattern(type="argument", optional=optional, argument=Argument())


def make_option(args) -> OptionPattern:
    if not args.old_option:
        option = Option(names_short=args.short_option, names_long=args.long_option, description=args.description)
        p = OptionPattern(type="option", option=option, optional=True)
    else:
        option = Option(names_short=args.short_option, names_long=args.old_option, description=args.description)
        p = OptionPattern(type="option", option=option, optional=True, prefix_long="-", separators_long=[" "])

    if args.require_parameter:
        p.argument = make_arg(optional=False)

    return p


def parse_complete(fish_splitted: List[str]):
    args = parser.parse_args(fish_splitted[1:])

    command = args.command

    if args.short_option or args.long_option or args.old_option:
        return command, make_option(args)

    return command, None


def iter_completes(fish_completes: str) -> Iterable[List[str]]:
    for i, comp in enumerate(fish_completes.splitlines()):
        if not comp.startswith("complete"):
            continue

        try:
            yield shlex.split(comp, posix=True)
        except ValueError as e:
            click.secho(f"Line {i}: {e}", err=True, fg="red")


def parse_fish_document(fish_completes: str) -> Specification:
    names = []
    options: Dict[str, List[Union[GroupPattern, CommandPattern, ArgumentPattern, OptionPattern]]] = defaultdict(list)

    for comp in iter_completes(fish_completes):
        command, x = parse_complete(comp)
        names += [command]

        if isinstance(x, OptionPattern):
            options[""].append(x)

    cli_obj = Cli(name=names[0], pattern_groups=[GroupPattern(type="group", patterns=options[""])])

    return Specification(openautocomplete=OpenAutoComplete(version="1.0"), components=Components(), cli=cli_obj)
