"""
Moon CLI commands.
"""

from __future__ import annotations

import click
import json
from datetime import datetime
from typing import Optional

from astr0.core.moon import (
    moon_position, moon_phase, moon_altitude,
    moonrise, moonset, next_phase,
    MoonPhase, PHASE_EMOJI
)
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


@click.group(name='moon')
def moon_group():
    """
    Lunar position and events.
    
    \b
    Calculate the Moon's position, phase, rise/set times.
    
    \b
    Examples:
        astr0 moon position                    # Current lunar position
        astr0 moon phase                       # Current phase
        astr0 moon rise --lat 34.05 --lon -118.25
    """
    pass


@moon_group.command()
@click.option('--jd', type=float, help='Julian Date (default: now)')
@click.pass_context
def position(ctx, jd: Optional[float]):
    """Show current lunar position."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    jd_val = JulianDate(jd) if jd else jd_now()
    moon = moon_position(jd_val, vctx)
    
    if output_fmt == 'json':
        data = {
            'jd': jd_val.jd,
            'ra_hours': moon.ra.hours,
            'ra_degrees': moon.ra.degrees,
            'dec_degrees': moon.dec.degrees,
            'ecliptic_longitude': moon.longitude.degrees,
            'ecliptic_latitude': moon.latitude.degrees,
            'distance_km': moon.distance_km,
            'distance_earth_radii': moon.distance_earth_radii,
            'angular_diameter_degrees': moon.angular_diameter.degrees,
            'parallax_degrees': moon.parallax.degrees,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        dt = jd_val.to_datetime()
        click.echo(f"""
  🌙 Lunar Position
  ─────────────────────────────────────────
  Time:       {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  JD:         {jd_val.jd:.6f}
  
  Equatorial:
    RA:       {moon.ra.format_hms()}
    Dec:      {moon.dec.format_dms()}
  
  Ecliptic:
    λ:        {moon.longitude.degrees:.4f}°
    β:        {moon.latitude.degrees:.4f}°
  
  Distance:   {moon.distance_km:.0f} km ({moon.distance_earth_radii:.2f} R⊕)
  Angular ⌀:  {moon.angular_diameter.degrees * 60:.2f}′
  Parallax:   {moon.parallax.degrees:.4f}°
""")
        if vctx:
            click.echo(vctx.format_steps())


@moon_group.command()
@click.option('--jd', type=float, help='Julian Date (default: now)')
@click.pass_context
def phase(ctx, jd: Optional[float]):
    """Show current lunar phase."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    jd_val = JulianDate(jd) if jd else jd_now()
    phase_info = moon_phase(jd_val, vctx)
    
    if output_fmt == 'json':
        data = {
            'jd': jd_val.jd,
            'phase_angle': phase_info.phase_angle,
            'illumination': phase_info.illumination,
            'percent_illuminated': phase_info.percent_illuminated,
            'phase_name': phase_info.phase_name.value,
            'age_days': phase_info.age_days,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        dt = jd_val.to_datetime()
        emoji = PHASE_EMOJI.get(phase_info.phase_name, "🌙")
        
        # Create illumination bar
        bar_len = 20
        filled = int(phase_info.illumination * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        
        click.echo(f"""
  {emoji} Lunar Phase
  ─────────────────────────────────────────
  Time:         {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  
  Phase:        {phase_info.phase_name.value}
  Illumination: {phase_info.percent_illuminated:.1f}%
                [{bar}]
  
  Phase angle:  {phase_info.phase_angle:.2f}°
  Moon age:     {phase_info.age_days:.1f} days
""")
        if vctx:
            click.echo(vctx.format_steps())


@moon_group.command(name='rise')
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def rise_cmd(ctx, lat: Optional[float], lon: Optional[float],
             observer_name: Optional[str], jd: Optional[float]):
    """Calculate moonrise time."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()
    
    rise_jd = moonrise(observer, jd_val, vctx)
    
    if rise_jd is None:
        if output_fmt == 'json':
            click.echo(json.dumps({'error': 'Moon does not rise on this date'}))
        else:
            click.echo("  Moon does not rise on this date at this location")
        return
    
    if output_fmt == 'json':
        data = {
            'observer': observer.name,
            'latitude': observer.lat_deg,
            'longitude': observer.lon_deg,
            'moonrise_jd': rise_jd.jd,
            'moonrise_utc': rise_jd.to_datetime().isoformat(),
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        dt = rise_jd.to_datetime()
        click.echo(f"""
  🌙 Moonrise
  ─────────────────────────────────────────
  Observer:   {observer.name}
  Location:   {observer.lat_deg:.4f}°, {observer.lon_deg:.4f}°

  Moonrise:   {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  JD:         {rise_jd.jd:.6f}
""")
        if vctx:
            click.echo(vctx.format_steps())


@moon_group.command(name='set')
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def set_cmd(ctx, lat: Optional[float], lon: Optional[float],
            observer_name: Optional[str], jd: Optional[float]):
    """Calculate moonset time."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()
    
    set_jd = moonset(observer, jd_val, vctx)
    
    if set_jd is None:
        if output_fmt == 'json':
            click.echo(json.dumps({'error': 'Moon does not set on this date'}))
        else:
            click.echo("  Moon does not set on this date at this location")
        return
    
    if output_fmt == 'json':
        data = {
            'observer': observer.name,
            'latitude': observer.lat_deg,
            'longitude': observer.lon_deg,
            'moonset_jd': set_jd.jd,
            'moonset_utc': set_jd.to_datetime().isoformat(),
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        dt = set_jd.to_datetime()
        click.echo(f"""
  🌙 Moonset
  ─────────────────────────────────────────
  Observer:   {observer.name}
  Location:   {observer.lat_deg:.4f}°, {observer.lon_deg:.4f}°

  Moonset:    {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  JD:         {set_jd.jd:.6f}
""")
        if vctx:
            click.echo(vctx.format_steps())


@moon_group.command()
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: now)')
@click.pass_context
def altitude(ctx, lat: Optional[float], lon: Optional[float],
             observer_name: Optional[str], jd: Optional[float]):
    """Show current lunar altitude."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()
    
    alt = moon_altitude(observer, jd_val, vctx)
    
    if output_fmt == 'json':
        data = {
            'observer': observer.name,
            'latitude': observer.lat_deg,
            'longitude': observer.lon_deg,
            'jd': jd_val.jd,
            'altitude_degrees': alt.degrees,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        dt = jd_val.to_datetime()
        status = "above horizon" if alt.degrees > 0 else "below horizon"
        click.echo(f"""
  🌙 Lunar Altitude
  ─────────────────────────────────────────
  Time:       {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Observer:   {observer.name}
  Location:   {observer.lat_deg:.4f}°, {observer.lon_deg:.4f}°

  Altitude:   {alt.degrees:+.2f}° ({status})
""")
        if vctx:
            click.echo(vctx.format_steps())


@moon_group.command(name='next')
@click.argument('phase_name', type=click.Choice(['new', 'first', 'full', 'last'], case_sensitive=False))
@click.option('--jd', type=float, help='Starting Julian Date (default: now)')
@click.pass_context
def next_cmd(ctx, phase_name: str, jd: Optional[float]):
    """Find next occurrence of a lunar phase."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    jd_val = JulianDate(jd) if jd else jd_now()
    
    # Map names to phases
    phase_map = {
        'new': MoonPhase.NEW_MOON,
        'first': MoonPhase.FIRST_QUARTER,
        'full': MoonPhase.FULL_MOON,
        'last': MoonPhase.LAST_QUARTER,
    }
    
    target_phase = phase_map[phase_name.lower()]
    result_jd = next_phase(jd_val, target_phase, vctx)
    
    if output_fmt == 'json':
        data = {
            'phase': target_phase.value,
            'jd': result_jd.jd,
            'utc': result_jd.to_datetime().isoformat(),
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        dt = result_jd.to_datetime()
        emoji = PHASE_EMOJI.get(target_phase, "🌙")
        
        # Calculate days until
        days_until = result_jd.jd - jd_val.jd
        
        click.echo(f"""
  {emoji} Next {target_phase.value}
  ─────────────────────────────────────────
  Date:       {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  JD:         {result_jd.jd:.6f}
  
  In:         {days_until:.1f} days
""")
        if vctx:
            click.echo(vctx.format_steps())
