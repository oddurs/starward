"""
Coordinate-related CLI commands.
"""

import click
from typing import Optional

from astr0.core.coords import ICRSCoord, GalacticCoord, HorizontalCoord, transform_coords
from astr0.core.angles import Angle
from astr0.core.time import JulianDate, jd_now
from astr0.verbose import VerboseContext


@click.group(name='coords')
def coords_group():
    """
    Coordinate transformations.
    
    \b
    Transform between ICRS, Galactic, and Horizontal coordinate systems.
    
    \b
    Examples:
        astr0 coords transform "12h30m +45d" --to galactic
        astr0 coords parse "18h36m56s -26d54m32s"
    """
    pass


@coords_group.command()
@click.argument('coordinates')
@click.option('--from', 'from_sys', type=click.Choice(['icrs', 'galactic']), default='icrs',
              help='Input coordinate system')
@click.option('--to', 'to_sys', type=click.Choice(['icrs', 'galactic', 'altaz']), required=True,
              help='Output coordinate system')
@click.option('--lat', type=float, default=None, help='Observer latitude (for altaz)')
@click.option('--lon', type=float, default=None, help='Observer longitude (for altaz)')
@click.option('--jd', 'jd_value', type=float, default=None, help='Julian Date (for altaz, default: now)')
@click.pass_context
def transform(ctx, coordinates: str, from_sys: str, to_sys: str, 
              lat: Optional[float], lon: Optional[float], jd_value: Optional[float]):
    """
    Transform coordinates between systems.
    
    \b
    Input formats:
        "12h30m00s +45d30m00s"  — HMS/DMS
        "187.5 45.5"            — Decimal degrees
        "12:30:00 +45:30:00"    — Colon-separated
    
    \b
    For horizontal (altaz) output, you must specify:
        --lat: Observer latitude in degrees
        --lon: Observer longitude in degrees (positive East)
    
    \b
    Examples:
        astr0 coords transform "12h30m +45d" --to galactic
        astr0 coords transform "18h36m56s -26d54m32s" --to altaz --lat 34 --lon -118
        astr0 coords transform "l=0 b=0" --from galactic --to icrs
    """
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    # Parse input coordinates
    if from_sys == 'icrs':
        input_coord = ICRSCoord.parse(coordinates)
    elif from_sys == 'galactic':
        # Parse "l=X b=Y" format
        import re
        match = re.match(r'l=?([\d.+-]+)\s*[,;]?\s*b=?([\d.+-]+)', coordinates, re.I)
        if match:
            l_deg, b_deg = float(match.group(1)), float(match.group(2))
            input_coord = GalacticCoord.from_degrees(l_deg, b_deg)
        else:
            parts = coordinates.split()
            if len(parts) == 2:
                input_coord = GalacticCoord.from_degrees(float(parts[0]), float(parts[1]))
            else:
                raise click.BadParameter(f"Cannot parse galactic coordinates: {coordinates}")
    else:
        raise click.BadParameter(f"Unknown input system: {from_sys}")
    
    # Prepare kwargs for horizontal
    kwargs = {}
    if to_sys == 'altaz':
        if lat is None or lon is None:
            raise click.UsageError("--lat and --lon are required for altaz output")
        kwargs['lat'] = Angle(degrees=lat)
        kwargs['lon'] = Angle(degrees=lon)
        kwargs['jd'] = JulianDate(jd_value) if jd_value else jd_now()
    
    # Transform
    result = transform_coords(input_coord, to_sys, verbose=vctx, **kwargs)
    
    if output_fmt == 'json':
        import json
        data = {
            'input': {
                'system': from_sys,
                'coordinates': coordinates,
            },
            'output': {
                'system': to_sys,
            }
        }
        
        if isinstance(result, ICRSCoord):
            data['output']['ra_deg'] = result.ra.degrees
            data['output']['dec_deg'] = result.dec.degrees
            data['output']['formatted'] = result.format()
        elif isinstance(result, GalacticCoord):
            data['output']['l_deg'] = result.l.degrees
            data['output']['b_deg'] = result.b.degrees
            data['output']['formatted'] = result.format()
        elif isinstance(result, HorizontalCoord):
            data['output']['alt_deg'] = result.alt.degrees
            data['output']['az_deg'] = result.az.degrees
            data['output']['airmass'] = result.airmass
            data['output']['formatted'] = result.format()
        
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"\n  Input ({from_sys.upper()}): {coordinates}")
        click.echo("  ─────────────────────────────────────────────")
        
        if isinstance(result, ICRSCoord):
            click.echo(f"  Output (ICRS):")
            click.echo(f"    RA:   {result.ra.format_hms()} ({result.ra.degrees:.6f}°)")
            click.echo(f"    Dec:  {result.dec.format_dms()} ({result.dec.degrees:.6f}°)")
        elif isinstance(result, GalacticCoord):
            click.echo(f"  Output (Galactic):")
            click.echo(f"    l:  {result.l.degrees:.6f}°")
            click.echo(f"    b:  {result.b.degrees:.6f}°")
        elif isinstance(result, HorizontalCoord):
            click.echo(f"  Output (Horizontal) at JD {kwargs['jd'].jd:.4f}:")
            click.echo(f"    Alt:     {result.alt.format_dms()} ({result.alt.degrees:.4f}°)")
            click.echo(f"    Az:      {result.az.degrees:.4f}°")
            click.echo(f"    Airmass: {result.airmass:.3f}")
            if result.alt.degrees < 0:
                click.echo("    ⚠️  Object is below the horizon")
        
        click.echo()
        
        if vctx:
            click.echo(vctx.format_steps())


@coords_group.command()
@click.argument('coordinates')
@click.pass_context
def parse(ctx, coordinates: str):
    """
    Parse and display coordinate components.
    
    \b
    Examples:
        astr0 coords parse "12h30m45.6s +45d30m15.2s"
        astr0 coords parse "187.44 45.504"
    """
    output_fmt = ctx.obj.get('output', 'plain')
    
    coord = ICRSCoord.parse(coordinates)
    
    ra_h, ra_m, ra_s = coord.ra.to_hms()
    dec_d, dec_m, dec_s = coord.dec.to_dms()
    
    if output_fmt == 'json':
        import json
        data = {
            'input': coordinates,
            'ra': {
                'hours': coord.ra.hours,
                'degrees': coord.ra.degrees,
                'hms': {'h': ra_h, 'm': ra_m, 's': ra_s},
            },
            'dec': {
                'degrees': coord.dec.degrees,
                'dms': {'d': dec_d, 'm': dec_m, 's': dec_s},
            }
        }
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"""
  Input: {coordinates}
  ─────────────────────────────────────────────
  
  Right Ascension:
    Decimal hours:   {coord.ra.hours:.10f}h
    Decimal degrees: {coord.ra.degrees:.10f}°
    HMS:             {ra_h}h {ra_m}m {ra_s:.4f}s
  
  Declination:
    Decimal degrees: {coord.dec.degrees:.10f}°
    DMS:             {'+' if dec_d >= 0 else ''}{dec_d}° {dec_m}′ {dec_s:.4f}″
""")
