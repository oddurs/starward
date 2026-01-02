"""
Constants-related CLI commands.
"""

import click

from astr0.core.constants import CONSTANTS


@click.group(name='constants')
def constants_group():
    """
    Astronomical constants.
    
    \b
    Browse and search astronomical constants with references.
    
    \b
    Examples:
        astr0 constants list
        astr0 constants search solar
        astr0 constants show AU
    """
    pass


@constants_group.command(name='list')
@click.pass_context
def list_constants(ctx):
    """List all available constants."""
    output_fmt = ctx.obj.get('output', 'plain')
    
    constants = CONSTANTS.list_all()
    
    if output_fmt == 'json':
        import json
        data = [
            {
                'name': c.name,
                'value': c.value,
                'unit': c.unit,
                'uncertainty': c.uncertainty,
                'reference': c.reference,
            }
            for c in constants
        ]
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo("\n  Astronomical Constants")
        click.echo("  " + "═" * 60)
        
        for c in constants:
            if c.uncertainty:
                val_str = f"{c.value:.6g} ± {c.uncertainty:.2g}"
            else:
                val_str = f"{c.value:.10g}"
            
            click.echo(f"\n  {c.name}")
            click.echo(f"    Value:     {val_str} {c.unit}")
            click.echo(f"    Reference: {c.reference}")
        
        click.echo()


@constants_group.command()
@click.argument('query')
@click.pass_context
def search(ctx, query: str):
    """Search constants by name."""
    output_fmt = ctx.obj.get('output', 'plain')
    
    results = CONSTANTS.search(query)
    
    if output_fmt == 'json':
        import json
        data = [
            {
                'name': c.name,
                'value': c.value,
                'unit': c.unit,
                'uncertainty': c.uncertainty,
                'reference': c.reference,
            }
            for c in results
        ]
        click.echo(json.dumps(data, indent=2))
    else:
        if not results:
            click.echo(f"\n  No constants found matching '{query}'")
            return
        
        click.echo(f"\n  Constants matching '{query}':")
        click.echo("  " + "─" * 50)
        
        for c in results:
            if c.uncertainty:
                val_str = f"{c.value:.6g} ± {c.uncertainty:.2g}"
            else:
                val_str = f"{c.value:.10g}"
            
            click.echo(f"\n  {c.name}")
            click.echo(f"    Value:     {val_str} {c.unit}")
            click.echo(f"    Reference: {c.reference}")
        
        click.echo()


@constants_group.command()
@click.argument('name')
@click.pass_context
def show(ctx, name: str):
    """Show a specific constant by attribute name."""
    output_fmt = ctx.obj.get('output', 'plain')
    
    # Try to get the constant
    try:
        const = getattr(CONSTANTS, name.upper())
    except AttributeError:
        # Try searching
        results = CONSTANTS.search(name)
        if len(results) == 1:
            const = results[0]
        elif len(results) > 1:
            click.echo(f"\n  Multiple matches for '{name}':")
            for c in results:
                click.echo(f"    - {c.name}")
            return
        else:
            click.echo(f"\n  Unknown constant: {name}")
            click.echo("  Use 'astr0 constants list' to see all constants.")
            return
    
    if output_fmt == 'json':
        import json
        data = {
            'name': const.name,
            'value': const.value,
            'unit': const.unit,
            'uncertainty': const.uncertainty,
            'reference': const.reference,
        }
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"""
  ╭────────────────────────────────────────────────────╮
  │  {const.name:^48}  │
  ├────────────────────────────────────────────────────┤
  │  Value:       {const.value:<36}  │
  │  Unit:        {const.unit:<36}  │
  │  Uncertainty: {str(const.uncertainty or 'exact'):<36}  │
  │  Reference:   {const.reference:<36}  │
  ╰────────────────────────────────────────────────────╯
""")
