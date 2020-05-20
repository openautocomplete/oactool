# oactool

A tool to manipulate [OpenAutoComplete](https://github.com/openautocomplete/openautocomplete) definitions.

## Installation

Using pip:

    pip install oactool

Using [poetry](https://python-poetry.org/):

    poetry add oactool

## Validation

Validate OpenAutoComplete definition:

    oactool validate <file>
    
Export JSON Schema for OpenAutoComplete:

    oactool jsonschema
    
Export Docopt usages (works on a subset of definitions):
    
    oactool make-docopt
    
Export fish autocomplete file (highly experimental!):
    
    oactool make-fish
