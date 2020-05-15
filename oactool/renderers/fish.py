import secrets
import shlex
import sys
from typing import Iterable, List, Optional

from more_itertools import unique_everseen

from oactool.schema import Cli, CommandPattern, OptionPattern, Specification


def fishize_option(option_p: OptionPattern, cli: Cli, cond: Optional[str]):
    comp: List[str] = ["complete", "-c", cli.name]
    if cond:
        comp += ["-n", cond]
    if option_p.option.description:
        comp += ["-d", option_p.option.description]

    if cli.option_prefix_short == "-":
        for x in option_p.option.names_short:
            comp += ["-s", x]
    else:
        print("Short options, defined in spec are not supported by fish completions right now", file=sys.stderr)

    if cli.option_prefix_long == "--":
        for x in option_p.option.names_long:
            comp += ["-l", x]
    elif cli.option_prefix_long == "-":
        for x in option_p.option.names_long:
            comp += ["-o", x]
    else:
        print("Long options, defined in spec are not supported by fish completions right now", file=sys.stderr)

    if option_p.argument:
        comp += ["-r"]

    return shlex.join(comp)


def fishize_subcommand(command_p: CommandPattern, cli: Cli, cond: Optional[str]):
    comp = ["complete", "-c", cli.name]
    if cond:
        comp += ["-n", cond]
    if command_p.command.description:
        comp += ["-d", command_p.command.description]

    for x in command_p.command.names:
        comp += ["-a", x]

    return shlex.join(comp)


def make_no_subcommand_function(no_subcommand_name: str, commands: Iterable[str]):
    commands_serialized = " ".join(commands)
    if len(commands_serialized) == 0:
        return ""

    return """function {no_subcommand_name}
    for i in (commandline -opc)
        if contains -- $i {commands}
            return 1
        end
    end
    return 0
end""".format(
        no_subcommand_name=no_subcommand_name, commands=commands_serialized
    )


def render_fish(spec: Specification):
    rand = secrets.token_hex(4)

    function_prefix = f"__fish_{spec.cli.name}_{rand}_"
    no_subcommand_name = f"{function_prefix}complete_no_subcommand"

    completes: List[str] = []
    root_commands: List[str] = []

    for pattern_group in spec.cli.pattern_groups or []:
        last_command_seen = no_subcommand_name
        for pattern in pattern_group.patterns:
            if isinstance(pattern, CommandPattern):
                if last_command_seen == no_subcommand_name:
                    root_commands += pattern.command.names

                completes += [fishize_subcommand(pattern, spec.cli, last_command_seen)]
                last_command_seen = f"__fish_seen_subcommand_from {pattern.command.names[0]}"
            if isinstance(pattern, OptionPattern):
                completes += [fishize_option(pattern, spec.cli, last_command_seen)]

    return "\n".join(
        [
            "# Generated using OpenAutoComplete specification",
            make_no_subcommand_function(no_subcommand_name, commands=unique_everseen(root_commands)),
            *unique_everseen(completes),
        ]
    )
