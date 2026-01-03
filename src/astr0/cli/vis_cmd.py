"""
Visibility CLI commands.
"""

from __future__ import annotations

import click
import json
from typing import Optional

from astr0.core.visibility import (
    airmass, target_altitude, target_azimuth,
    transit_time, transit_altitude_calc, target_rise_set,
    moon_target_separation, is_night, compute_visibility
)
from astr0.core.coords import ICRSCoord
from astr0.core.time import JulianDate, jd_now
from astr0.core.observer import Observer, OBSERVERS
from astr0.verbose import VerboseContext


def _get_observer_from_options(lat: Optional[float], lon: Optional[float],
                                observer_name: Optional[str]) -> Observer:
    """Get observer from command options."""
    if observer_name:
        obs = OBSERVERS.get(observer_name)
        if obs is None:
            raise click.ClickException(f"Observer '{observer_name}' not found. Use 'astr0 observer list'")
        return obs
    elif lat is not None and lon is not None:
        return Observer.from_degrees(
            name="CLI",
            latitude=lat,
            longitude=lon
        )
    else:
        # Try default observer
        obs = OBSERVERS.get_default()
        if obs is None:
            raise click.ClickException(
                "No location specified. Use --lat/--lon, --observer, or set a default observer."
            )
        return obs


@click.group(name='vis')
def vis_group():
    """
    Target visibility calculations.
    
    \b
    Calculate when and how well celestial objects can be observed.
    
    \b
    Examples:
        astr0 vis altitude "00h42m +41d16m" --observer greenwich
        astr0 vis airmass "12h30m +45d" --lat 34.05 --lon -118.25
        astr0 vis transit "06h45m -16d43m" --observer home
    """
    pass


@vis_group.command()
@click.argument('coords')
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: now)')
@click.pass_context
def altitude(ctx, coords: str, lat: Optional[float], lon: Optional[float],
             observer_name: Optional[str], jd: Optional[float]):
    """Calculate target altitude."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    try:
        target = ICRSCoord.parse(coords)
    except ValueError as e:
        raise click.ClickException(f"Cannot parse coordinates: {e}")
    
    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()
    
    alt = target_altitude(target, observer, jd_val, vctx)
    az = target_azimuth(target, observer, jd_val, vctx)
    X = airmass(alt, vctx)
    
    if output_fmt == 'json':
        data = {
            'target': {'ra_deg': target.ra.degrees, 'dec_deg': target.dec.degrees},
            'observer': observer.name,
            'jd': jd_val.jd,
            'altitude_deg': alt.degrees,
            'azimuth_deg': az.degrees,
            'airmass': X,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        status = "above horizon" if alt.degrees > 0 else "below horizon"
        airmass_str = f"{X:.3f}" if X else "N/A"
        
        # Direction labels
        if az.degrees < 22.5 or az.degrees >= 337.5:
            dir_label = "N"
        elif az.degrees < 67.5:
            dir_label = "NE"
        elif az.degrees < 112.5:
            dir_label = "E"
        elif az.degrees < 157.5:
            dir_label = "SE"
        elif az.degrees < 202.5:
            dir_label = "S"
        elif az.degrees < 247.5:
            dir_label = "SW"
        elif az.degrees < 292.5:
            dir_label = "W"
        else:
            dir_label = "NW"
        
        dt = jd_val.to_datetime()
        click.echo(f"""
  🎯 Target Position
  ─────────────────────────────────────────
  Time:       {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Observer:   {observer.name}
  Location:   {observer.lat_deg:.4f}°, {observer.lon_deg:.4f}°
  
  Target:     RA {target.ra.format_hms()}, Dec {target.dec.format_dms()}
  
  Altitude:   {alt.degrees:+.2f}° ({status})
  Azimuth:    {az.degrees:.2f}° ({dir_label})
  Airmass:    {airmass_str}
""")
        if vctx:
            click.echo(vctx.format_steps())


@vis_group.command()
@click.argument('coords')
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def transit(ctx, coords: str, lat: Optional[float], lon: Optional[float],
            observer_name: Optional[str], jd: Optional[float]):
    """Calculate target transit time."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    try:
        target = ICRSCoord.parse(coords)
    except ValueError as e:
        raise click.ClickException(f"Cannot parse coordinates: {e}")
    
    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()
    
    trans = transit_time(target, observer, jd_val, vctx)
    trans_alt = transit_altitude_calc(target, observer, vctx)
    trans_airmass = airmass(trans_alt, vctx)
    
    if output_fmt == 'json':
        data = {
            'target': {'ra_deg': target.ra.degrees, 'dec_deg': target.dec.degrees},
            'observer': observer.name,
            'transit_jd': trans.jd,
            'transit_utc': trans.to_datetime().isoformat(),
            'transit_altitude_deg': trans_alt.degrees,
            'transit_airmass': trans_airmass,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        dt = trans.to_datetime()
        airmass_str = f"{trans_airmass:.3f}" if trans_airmass else "N/A"
        
        click.echo(f"""
  🎯 Target Transit
  ─────────────────────────────────────────
  Observer:   {observer.name}
  Location:   {observer.lat_deg:.4f}°, {observer.lon_deg:.4f}°
  
  Target:     RA {target.ra.format_hms()}, Dec {target.dec.format_dms()}
  
  Transit:    {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  JD:         {trans.jd:.6f}
  
  Max altitude: {trans_alt.degrees:.2f}°
  Airmass:      {airmass_str}
""")
        if vctx:
            click.echo(vctx.format_steps())


@vis_group.command(name='riseset')
@click.argument('coords')
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.option('--horizon', type=float, default=0.0, help='Horizon altitude (degrees)')
@click.pass_context
def riseset_cmd(ctx, coords: str, lat: Optional[float], lon: Optional[float],
                observer_name: Optional[str], jd: Optional[float], horizon: float):
    """Calculate target rise and set times."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    try:
        target = ICRSCoord.parse(coords)
    except ValueError as e:
        raise click.ClickException(f"Cannot parse coordinates: {e}")
    
    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()
    
    rise, set_t = target_rise_set(target, observer, jd_val, horizon, vctx)
    trans = transit_time(target, observer, jd_val, vctx)
    trans_alt = transit_altitude_calc(target, observer, vctx)
    
    if output_fmt == 'json':
        data = {
            'target': {'ra_deg': target.ra.degrees, 'dec_deg': target.dec.degrees},
            'observer': observer.name,
            'horizon_altitude': horizon,
            'rise_jd': rise.jd if rise else None,
            'rise_utc': rise.to_datetime().isoformat() if rise else None,
            'set_jd': set_t.jd if set_t else None,
            'set_utc': set_t.to_datetime().isoformat() if set_t else None,
            'transit_jd': trans.jd,
            'transit_altitude': trans_alt.degrees,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        rise_str = rise.to_datetime().strftime('%H:%M:%S') if rise else "---"
        set_str = set_t.to_datetime().strftime('%H:%M:%S') if set_t else "---"
        trans_str = trans.to_datetime().strftime('%H:%M:%S')
        
        # Calculate up time
        if rise and set_t:
            if set_t.jd > rise.jd:
                up_hours = (set_t.jd - rise.jd) * 24
            else:
                up_hours = ((set_t.jd + 1) - rise.jd) * 24
            up_str = f"{up_hours:.1f} hours"
        else:
            if trans_alt.degrees > horizon:
                up_str = "circumpolar"
            else:
                up_str = "never rises"
        
        date_str = jd_val.to_datetime().strftime('%Y-%m-%d')
        
        click.echo(f"""
  🎯 Target Rise/Set — {date_str}
  ─────────────────────────────────────────
  Observer:   {observer.name}
  Location:   {observer.lat_deg:.4f}°, {observer.lon_deg:.4f}°
  Horizon:    {horizon}°
  
  Target:     RA {target.ra.format_hms()}, Dec {target.dec.format_dms()}
  
  Rise:       {rise_str} UTC
  Transit:    {trans_str} UTC (alt: {trans_alt.degrees:.1f}°)
  Set:        {set_str} UTC
  
  Up time:    {up_str}
""")
        if vctx:
            click.echo(vctx.format_steps())


@vis_group.command()
@click.argument('coords')
@click.option('--jd', type=float, help='Julian Date (default: now)')
@click.pass_context
def moonsep(ctx, coords: str, jd: Optional[float]):
    """Calculate angular separation from the Moon."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    try:
        target = ICRSCoord.parse(coords)
    except ValueError as e:
        raise click.ClickException(f"Cannot parse coordinates: {e}")
    
    jd_val = JulianDate(jd) if jd else jd_now()
    
    sep = moon_target_separation(target, jd_val, vctx)
    
    if output_fmt == 'json':
        data = {
            'target': {'ra_deg': target.ra.degrees, 'dec_deg': target.dec.degrees},
            'jd': jd_val.jd,
            'moon_separation_deg': sep.degrees,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        # Assess impact on observation
        if sep.degrees > 60:
            impact = "minimal impact"
        elif sep.degrees > 30:
            impact = "some scattered light"
        elif sep.degrees > 15:
            impact = "significant impact"
        else:
            impact = "severe contamination"
        
        click.echo(f"""
  🌙 Moon Separation
  ─────────────────────────────────────────
  Target:     RA {target.ra.format_hms()}, Dec {target.dec.format_dms()}
  
  Separation: {sep.degrees:.1f}°
  Assessment: {impact}
""")
        if vctx:
            click.echo(vctx.format_steps())


@vis_group.command()
@click.argument('alt', type=float)
@click.pass_context
def airmass_cmd(ctx, alt: float):
    """Calculate airmass for a given altitude."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    from astr0.core.angles import Angle
    altitude = Angle(degrees=alt)
    X = airmass(altitude, vctx)
    
    if output_fmt == 'json':
        data = {
            'altitude_deg': alt,
            'airmass': X,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        if X is None:
            click.echo(f"  Target at {alt}° is below the horizon (airmass undefined)")
        else:
            # Assess quality
            if X < 1.5:
                quality = "excellent"
            elif X < 2.0:
                quality = "good"
            elif X < 2.5:
                quality = "acceptable"
            elif X < 3.0:
                quality = "marginal"
            else:
                quality = "poor"
            
            click.echo(f"""
  Airmass Calculator
  ─────────────────────────────────────────
  Altitude:   {alt}°
  Airmass:    {X:.3f}
  Quality:    {quality}
""")
        if vctx:
            click.echo(vctx.format_steps())
