"""
Observer management CLI commands.
"""

from __future__ import annotations

import click
from typing import Optional

from astr0.core.observer import Observer, OBSERVERS, get_config_file


@click.group(name='observer')
def observer_group():
    """
    Manage observer profiles.
    
    \b
    Save and manage observer locations for convenient use
    with sun, moon, and visibility commands.
    
    \b
    Profiles are stored in: ~/.astr0/observers.toml
    
    \b
    Examples:
        astr0 observer add "Home" --lat 34.05 --lon -118.25
        astr0 observer list
        astr0 observer default home
    """
    pass


@observer_group.command()
@click.argument('name')
@click.option('--lat', required=True, type=float, help='Latitude (degrees, + North)')
@click.option('--lon', required=True, type=float, help='Longitude (degrees, + East)')
@click.option('--elev', default=0.0, type=float, help='Elevation (meters)')
@click.option('--timezone', 'tz', type=str, help='Timezone (e.g., America/Los_Angeles)')
@click.pass_context
def add(ctx, name: str, lat: float, lon: float, elev: float, tz: Optional[str]):
    """Add or update an observer profile."""
    observer = Observer.from_degrees(
        name=name,
        latitude=lat,
        longitude=lon,
        elevation=elev,
        timezone=tz
    )
    
    OBSERVERS.add(observer)
    
    output_fmt = ctx.obj.get('output', 'plain')
    
    if output_fmt == 'json':
        import json
        click.echo(json.dumps({
            'action': 'added',
            'observer': observer.to_dict()
        }, indent=2))
    else:
        click.echo(f"✓ Added observer: {observer}")
        click.echo(f"  Config: {get_config_file()}")


@observer_group.command(name='list')
@click.pass_context
def list_cmd(ctx):
    """List all observer profiles."""
    output_fmt = ctx.obj.get('output', 'plain')
    
    observers = OBSERVERS.list_all()
    default = OBSERVERS.default_name
    
    if output_fmt == 'json':
        import json
        data = {
            'default': default,
            'observers': [obs.to_dict() for obs in observers]
        }
        click.echo(json.dumps(data, indent=2))
    else:
        if not observers:
            click.echo("No observers configured.")
            click.echo(f"Add one with: astr0 observer add \"Name\" --lat LAT --lon LON")
            return
        
        click.echo("\n  Observer Profiles")
        click.echo("  ─────────────────────────────────────────")
        
        for obs in observers:
            key = obs.name.lower().replace(' ', '_')
            marker = "★" if key == default else " "
            lat_dir = "N" if obs.lat_deg >= 0 else "S"
            lon_dir = "E" if obs.lon_deg >= 0 else "W"
            click.echo(f"  {marker} {obs.name}")
            click.echo(f"      {abs(obs.lat_deg):.4f}°{lat_dir}, {abs(obs.lon_deg):.4f}°{lon_dir}, {obs.elevation:.0f}m")
            if obs.timezone:
                click.echo(f"      Timezone: {obs.timezone}")
        
        click.echo(f"\n  Config: {get_config_file()}")
        click.echo()


@observer_group.command()
@click.argument('name')
@click.pass_context
def show(ctx, name: str):
    """Show details for an observer profile."""
    output_fmt = ctx.obj.get('output', 'plain')
    
    observer = OBSERVERS.get(name)
    
    if observer is None:
        raise click.ClickException(f"Observer '{name}' not found")
    
    if output_fmt == 'json':
        import json
        click.echo(json.dumps(observer.to_dict(), indent=2))
    else:
        lat_dir = "N" if observer.lat_deg >= 0 else "S"
        lon_dir = "E" if observer.lon_deg >= 0 else "W"
        
        click.echo(f"""
  Observer: {observer.name}
  ─────────────────────────────────────────
  Latitude:   {abs(observer.lat_deg):.6f}° {lat_dir}
  Longitude:  {abs(observer.lon_deg):.6f}° {lon_dir}
  Elevation:  {observer.elevation:.0f} m
""")
        if observer.timezone:
            click.echo(f"  Timezone:   {observer.timezone}")
        click.echo()


@observer_group.command()
@click.argument('name')
@click.pass_context
def default(ctx, name: str):
    """Set the default observer."""
    output_fmt = ctx.obj.get('output', 'plain')
    
    if OBSERVERS.set_default(name):
        if output_fmt == 'json':
            import json
            click.echo(json.dumps({'default': name}, indent=2))
        else:
            click.echo(f"✓ Default observer set to: {name}")
    else:
        raise click.ClickException(f"Observer '{name}' not found")


@observer_group.command()
@click.argument('name')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@click.pass_context
def remove(ctx, name: str, yes: bool):
    """Remove an observer profile."""
    output_fmt = ctx.obj.get('output', 'plain')
    
    observer = OBSERVERS.get(name)
    if observer is None:
        raise click.ClickException(f"Observer '{name}' not found")
    
    if not yes:
        click.confirm(f"Remove observer '{observer.name}'?", abort=True)
    
    OBSERVERS.remove(name)
    
    if output_fmt == 'json':
        import json
        click.echo(json.dumps({'action': 'removed', 'name': name}, indent=2))
    else:
        click.echo(f"✓ Removed observer: {observer.name}")
