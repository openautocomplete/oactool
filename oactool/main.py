#! /usr/bin/env python3
import json
import sys

import click
import pydantic

from oactool.renderers.docopt import render_docopt
from oactool.renderers.fish import render_fish
from oactool.schema import Components, Specification
from oactool.spec_parse import unref_spec


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--openautocomplete", flag_value=True)
def cli(ctx, openautocomplete):
    if ctx.invoked_subcommand is None and openautocomplete:
        click.secho(
            "\U0001F605 Well, not yet!\nWe use Click for handling CLI arguments, so we need a module, that could"
            "extract command line info using Click introspection",
            fg="yellow",
        )
        exit(1)


@cli.command()
@click.argument("specification", required=True, type=click.File("rb"))
def make_docopt(specification):
    try:
        spec = Specification.parse_obj(unref_spec(json.loads(specification.read())))
        print(render_docopt(spec))
    except (pydantic.ValidationError, json.JSONDecodeError) as e:
        print(e, file=sys.stderr)
        exit(1)


@cli.command()
@click.argument("specification", required=True, type=click.File("rb"))
def make_fish(specification):
    try:
        spec = Specification.parse_obj(unref_spec(json.loads(specification.read())))
        print(render_fish(spec))
    except (pydantic.ValidationError, json.JSONDecodeError) as e:
        print(e, file=sys.stderr)
        exit(1)


@cli.command()
@click.argument("specifications", nargs=-1, type=click.File("rb"))
def validate(specifications):
    fail = False

    for specification in specifications:
        try:
            Specification.parse_obj(unref_spec(json.loads(specification.read())))
            click.secho(f"[{specification.name}] Specification is correct!", fg="green")
        except (pydantic.ValidationError, json.JSONDecodeError) as e:
            click.secho(f"[{specification.name}] {e}", fg="red")
            fail = True

    if fail:
        exit(1)


@cli.command()
@click.argument("specification", required=True, type=click.File("rb"))
def simplify(specification):
    try:
        spec = Specification.parse_obj(unref_spec(json.loads(specification.read())))
        spec.components = Components()
        print(Specification.validate(spec).json(exclude_unset=True))
    except (pydantic.ValidationError, json.JSONDecodeError) as e:
        print(e, file=sys.stderr)
        exit(1)


@cli.command()
def jsonschema():
    print(Specification.schema_json())


def main():
    cli()


if __name__ == "__main__":
    main()
