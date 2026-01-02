"""
Command Line Interface for astr0.

Per aspera ad astra — Through hardships to the stars
"""

import click
from typing import Optional

from astr0 import __version__
from astr0.cli.time_cmd import time_group
from astr0.cli.coords_cmd import coords_group
from astr0.cli.angles_cmd import angles_group
from astr0.cli.constants_cmd import constants_group


class AliasedGroup(click.Group):
    """Click group with command aliases."""
    
    def get_command(self, ctx, cmd_name):
        # Try exact match first
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        
        # Try aliases
        aliases = {
            't': 'time',
            'c': 'coords',
            'coord': 'coords',
            'a': 'angles',
            'angle': 'angles',
            'const': 'constants',
        }
        
        if cmd_name in aliases:
            return click.Group.get_command(self, ctx, aliases[cmd_name])
        
        return None


@click.group(cls=AliasedGroup)
@click.option('--verbose', '-v', is_flag=True, help='Show calculation steps')
@click.option('--output', '-o', type=click.Choice(['plain', 'json']), default='plain', help='Output format')
@click.version_option(__version__, prog_name='astr0')
@click.pass_context
def main(ctx, verbose: bool, output: str):
    """
    astr0 — Astronomy Calculation Toolkit
    
    \b
    ✦ Per aspera ad astra ✦
    
    A professional toolkit for astronomical calculations.
    Use --verbose to see the math behind each calculation.
    
    \b
    Examples:
        astr0 time now
        astr0 coords transform "12h30m +45d" --to galactic
        astr0 angles sep "10h +30d" "11h +31d"
    
    \b
    Aliases:
        time → t | coords → c | angles → a | constants → const
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['output'] = output


# Register command groups
main.add_command(time_group)
main.add_command(coords_group)
main.add_command(angles_group)
main.add_command(constants_group)


@main.command()
def about():
    """Show information about astr0."""
    click.echo(r"""
    ╭─────────────────────────────────────────╮
    │                                         │
    │     ▄▀█ ▄▀▀ ▀█▀ █▀▄ ▄▀▄               │
    │     █▀█ ▀▄▄  █  █▀▄ ▀▄▀               │
    │                                         │
    │     Astronomy Calculation Toolkit       │
    │     ─────────────────────────────       │
    │                                         │
    │     Version: """ + __version__ + """                       │
    │     License: MIT                        │
    │                                         │
    │     "Per aspera ad astra"               │
    │     Through hardships to the stars      │
    │                                         │
    ╰─────────────────────────────────────────╯
    """)


if __name__ == '__main__':
    main()
