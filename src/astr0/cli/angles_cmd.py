"""
Angle-related CLI commands.
"""

import click
from typing import Optional

from astr0.core.angles import Angle, angular_separation, position_angle
from astr0.core.coords import ICRSCoord
from astr0.verbose import VerboseContext


@click.group(name='angles')
def angles_group():
    """
    Angular calculations.
    
    \b
    Calculate angular separations, position angles, and conversions.
    
    \b
    Examples:
        astr0 angles sep "10h30m +30d" "10h35m +31d"
        astr0 angles convert 45.5
        astr0 angles pa "10h +30d" "11h +31d"
    """
    pass


@angles_group.command()
@click.argument('coord1')
@click.argument('coord2')
@click.pass_context
def sep(ctx, coord1: str, coord2: str):
    """
    Calculate angular separation between two points.
    
    Uses the Vincenty formula for accuracy at all distances.
    
    \b
    Examples:
        astr0 angles sep "10h30m +30d" "10h35m +31d"
        astr0 angles sep "Polaris" "Vega"  # Future: catalog lookup
    """
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    # Parse coordinates
    c1 = ICRSCoord.parse(coord1)
    c2 = ICRSCoord.parse(coord2)
    
    # Calculate separation
    sep_angle = angular_separation(c1.ra, c1.dec, c2.ra, c2.dec, verbose=vctx)
    
    if output_fmt == 'json':
        import json
        data = {
            'point1': {
                'input': coord1,
                'ra_deg': c1.ra.degrees,
                'dec_deg': c1.dec.degrees,
            },
            'point2': {
                'input': coord2,
                'ra_deg': c2.ra.degrees,
                'dec_deg': c2.dec.degrees,
            },
            'separation': {
                'degrees': sep_angle.degrees,
                'arcminutes': sep_angle.arcminutes,
                'arcseconds': sep_angle.arcseconds,
                'formatted': sep_angle.format_dms(),
            }
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"""
  Point 1: {c1.format()}
  Point 2: {c2.format()}
  ─────────────────────────────────────────────
  
  Angular Separation:
    {sep_angle.format_dms()}
    = {sep_angle.degrees:.10f}°
    = {sep_angle.arcminutes:.6f}′
    = {sep_angle.arcseconds:.4f}″
""")
        if vctx:
            click.echo(vctx.format_steps())


@angles_group.command()
@click.argument('coord1')
@click.argument('coord2')
@click.pass_context
def pa(ctx, coord1: str, coord2: str):
    """
    Calculate position angle from point 1 to point 2.
    
    Position angle is measured from North through East.
    
    \b
    Examples:
        astr0 angles pa "10h +30d" "11h +31d"
    """
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    # Parse coordinates
    c1 = ICRSCoord.parse(coord1)
    c2 = ICRSCoord.parse(coord2)
    
    # Calculate position angle
    pa_angle = position_angle(c1.ra, c1.dec, c2.ra, c2.dec, verbose=vctx)
    
    # Describe direction
    pa_deg = pa_angle.degrees
    if pa_deg < 22.5 or pa_deg >= 337.5:
        direction = "N"
    elif pa_deg < 67.5:
        direction = "NE"
    elif pa_deg < 112.5:
        direction = "E"
    elif pa_deg < 157.5:
        direction = "SE"
    elif pa_deg < 202.5:
        direction = "S"
    elif pa_deg < 247.5:
        direction = "SW"
    elif pa_deg < 292.5:
        direction = "W"
    else:
        direction = "NW"
    
    if output_fmt == 'json':
        import json
        data = {
            'from': {
                'input': coord1,
                'ra_deg': c1.ra.degrees,
                'dec_deg': c1.dec.degrees,
            },
            'to': {
                'input': coord2,
                'ra_deg': c2.ra.degrees,
                'dec_deg': c2.dec.degrees,
            },
            'position_angle': {
                'degrees': pa_angle.degrees,
                'direction': direction,
            }
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"""
  From: {c1.format()}
  To:   {c2.format()}
  ─────────────────────────────────────────────
  
  Position Angle: {pa_angle.degrees:.4f}° ({direction})
  
  (Measured from North through East)
""")
        if vctx:
            click.echo(vctx.format_steps())


@angles_group.command()
@click.argument('value', type=float)
@click.option('--unit', '-u', type=click.Choice(['deg', 'rad', 'arcmin', 'arcsec', 'hours']),
              default='deg', help='Input unit')
@click.pass_context
def convert(ctx, value: float, unit: str):
    """
    Convert an angle between different units.
    
    \b
    Examples:
        astr0 angles convert 45.5
        astr0 angles convert 3.14159 --unit rad
        astr0 angles convert 12.5 --unit hours
    """
    output_fmt = ctx.obj.get('output', 'plain')
    
    # Create angle from input
    if unit == 'deg':
        angle = Angle(degrees=value)
    elif unit == 'rad':
        angle = Angle(radians=value)
    elif unit == 'arcmin':
        angle = Angle(arcminutes=value)
    elif unit == 'arcsec':
        angle = Angle(arcseconds=value)
    elif unit == 'hours':
        angle = Angle(hours=value)
    else:
        raise click.BadParameter(f"Unknown unit: {unit}")
    
    if output_fmt == 'json':
        import json
        data = {
            'input': {'value': value, 'unit': unit},
            'degrees': angle.degrees,
            'radians': angle.radians,
            'hours': angle.hours,
            'arcminutes': angle.arcminutes,
            'arcseconds': angle.arcseconds,
            'dms': angle.format_dms(),
            'hms': angle.format_hms(),
        }
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"""
  Input: {value} {unit}
  ─────────────────────────────────────────────
  
  Degrees:     {angle.degrees:.10f}°
  Radians:     {angle.radians:.10f}
  Hours:       {angle.hours:.10f}h
  Arcminutes:  {angle.arcminutes:.10f}′
  Arcseconds:  {angle.arcseconds:.10f}″
  
  DMS: {angle.format_dms()}
  HMS: {angle.format_hms()}
""")
