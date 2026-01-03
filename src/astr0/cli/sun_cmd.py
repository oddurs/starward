"""
Sun-related CLI commands.
"""

from __future__ import annotations

import click
from datetime import datetime, timezone
from typing import Optional

from astr0.core.sun import (
    sun_position, sunrise, sunset, solar_noon,
    civil_twilight, nautical_twilight, astronomical_twilight,
    solar_altitude, day_length
)
from astr0.core.observer import Observer, get_observer, OBSERVERS
from astr0.core.time import JulianDate, jd_now
from astr0.verbose import VerboseContext


def _get_observer_from_options(lat: Optional[float], lon: Optional[float], 
                                observer_name: Optional[str]) -> Optional[Observer]:
    """Get observer from CLI options."""
    if lat is not None and lon is not None:
        return Observer.from_degrees("CLI", lat, lon)
    elif observer_name:
        obs = get_observer(observer_name)
        if obs is None:
            raise click.ClickException(f"Observer '{observer_name}' not found. Use 'astr0 observer list' to see available observers.")
        return obs
    else:
        obs = get_observer()  # Default observer
        if obs is None:
            raise click.ClickException(
                "No observer specified. Use --lat/--lon or --observer, "
                "or add a default observer with 'astr0 observer add'"
            )
        return obs


@click.group(name='sun')
def sun_group():
    """
    Solar position and events.
    
    \b
    Calculate the Sun's position, sunrise, sunset, and twilight times.
    
    \b
    Examples:
        astr0 sun position                    # Current solar position
        astr0 sun rise --lat 34.05 --lon -118.25
        astr0 sun twilight --observer home
    """
    pass


@sun_group.command()
@click.option('--jd', type=float, help='Julian Date (default: now)')
@click.pass_context
def position(ctx, jd: Optional[float]):
    """Show current solar position."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    jd_val = JulianDate(jd) if jd else jd_now()
    sun = sun_position(jd_val, vctx)
    
    if output_fmt == 'json':
        import json
        data = {
            'jd': jd_val.jd,
            'ra_hours': sun.ra.hours,
            'ra_degrees': sun.ra.degrees,
            'dec_degrees': sun.dec.degrees,
            'ecliptic_longitude': sun.longitude.degrees,
            'distance_au': sun.distance_au,
            'equation_of_time_minutes': sun.equation_of_time,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        dt = jd_val.to_datetime()
        click.echo(f"""
  ☀️  Solar Position
  ─────────────────────────────────────────
  Time:       {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  JD:         {jd_val.jd:.6f}
  
  Equatorial:
    RA:       {sun.ra.format_hms()}
    Dec:      {sun.dec.format_dms()}
  
  Ecliptic:
    λ:        {sun.longitude.degrees:.6f}°
  
  Distance:   {sun.distance_au:.6f} AU
  Eq. Time:   {sun.equation_of_time:+.2f} min
""")
        if vctx:
            click.echo(vctx.format_steps())


@sun_group.command(name='rise')
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def rise_cmd(ctx, lat: Optional[float], lon: Optional[float], 
             observer_name: Optional[str], jd: Optional[float]):
    """Calculate sunrise time."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()
    
    rise_jd = sunrise(observer, jd_val, vctx)
    
    if output_fmt == 'json':
        import json
        data = {
            'observer': observer.to_dict(),
            'date_jd': jd_val.jd,
            'sunrise_jd': rise_jd.jd if rise_jd else None,
            'sunrise_utc': rise_jd.to_datetime().isoformat() if rise_jd else None,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"""
  ☀️ Sunrise
  ─────────────────────────────────────────
  Observer:   {observer.name}
  Location:   {observer.lat_deg:.4f}°, {observer.lon_deg:.4f}°
""")
        if rise_jd:
            dt = rise_jd.to_datetime()
            click.echo(f"  Sunrise:    {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            click.echo(f"  JD:         {rise_jd.jd:.6f}")
        else:
            click.echo("  Sunrise:    Sun does not rise on this date")
        click.echo()
        
        if vctx:
            click.echo(vctx.format_steps())


@sun_group.command(name='set')
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def set_cmd(ctx, lat: Optional[float], lon: Optional[float],
            observer_name: Optional[str], jd: Optional[float]):
    """Calculate sunset time."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()
    
    set_jd = sunset(observer, jd_val, vctx)
    
    if output_fmt == 'json':
        import json
        data = {
            'observer': observer.to_dict(),
            'date_jd': jd_val.jd,
            'sunset_jd': set_jd.jd if set_jd else None,
            'sunset_utc': set_jd.to_datetime().isoformat() if set_jd else None,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"""
  🌅 Sunset
  ─────────────────────────────────────────
  Observer:   {observer.name}
  Location:   {observer.lat_deg:.4f}°, {observer.lon_deg:.4f}°
""")
        if set_jd:
            dt = set_jd.to_datetime()
            click.echo(f"  Sunset:     {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            click.echo(f"  JD:         {set_jd.jd:.6f}")
        else:
            click.echo("  Sunset:     Sun does not set on this date")
        click.echo()
        
        if vctx:
            click.echo(vctx.format_steps())


@sun_group.command()
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def twilight(ctx, lat: Optional[float], lon: Optional[float],
             observer_name: Optional[str], jd: Optional[float]):
    """Calculate twilight times (civil, nautical, astronomical)."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()
    
    # Calculate all twilight times
    rise_jd = sunrise(observer, jd_val)
    set_jd = sunset(observer, jd_val)
    civil_m, civil_e = civil_twilight(observer, jd_val)
    naut_m, naut_e = nautical_twilight(observer, jd_val)
    astro_m, astro_e = astronomical_twilight(observer, jd_val)
    noon_jd = solar_noon(observer, jd_val)
    length = day_length(observer, jd_val)
    
    def fmt_time(jd_time):
        if jd_time is None:
            return "—"
        return jd_time.to_datetime().strftime('%H:%M:%S')
    
    if output_fmt == 'json':
        import json
        data = {
            'observer': observer.to_dict(),
            'date_jd': jd_val.jd,
            'astronomical_dawn_utc': astro_m.to_datetime().isoformat() if astro_m else None,
            'nautical_dawn_utc': naut_m.to_datetime().isoformat() if naut_m else None,
            'civil_dawn_utc': civil_m.to_datetime().isoformat() if civil_m else None,
            'sunrise_utc': rise_jd.to_datetime().isoformat() if rise_jd else None,
            'solar_noon_utc': noon_jd.to_datetime().isoformat(),
            'sunset_utc': set_jd.to_datetime().isoformat() if set_jd else None,
            'civil_dusk_utc': civil_e.to_datetime().isoformat() if civil_e else None,
            'nautical_dusk_utc': naut_e.to_datetime().isoformat() if naut_e else None,
            'astronomical_dusk_utc': astro_e.to_datetime().isoformat() if astro_e else None,
            'day_length_hours': length,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        date_str = jd_val.to_datetime().strftime('%Y-%m-%d')
        click.echo(f"""
  🌅 Solar Events — {date_str}
  ─────────────────────────────────────────
  Observer:   {observer.name}
  Location:   {observer.lat_deg:.4f}°, {observer.lon_deg:.4f}°
  
  Morning                     Evening
  ───────────────────────────────────────
  Astro. twilight  {fmt_time(astro_m)}    {fmt_time(astro_e)}  (-18°)
  Naut. twilight   {fmt_time(naut_m)}    {fmt_time(naut_e)}  (-12°)
  Civil twilight   {fmt_time(civil_m)}    {fmt_time(civil_e)}  (-6°)
  Sunrise/Sunset   {fmt_time(rise_jd)}    {fmt_time(set_jd)}
  
  Solar noon:      {fmt_time(noon_jd)} UTC
  Day length:      {length:.2f} hours
""")
        if vctx:
            click.echo(vctx.format_steps())


@sun_group.command()
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: now)')
@click.pass_context
def altitude(ctx, lat: Optional[float], lon: Optional[float],
             observer_name: Optional[str], jd: Optional[float]):
    """Show current solar altitude."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()
    
    alt = solar_altitude(observer, jd_val, vctx)
    
    if output_fmt == 'json':
        import json
        data = {
            'observer': observer.to_dict(),
            'jd': jd_val.jd,
            'altitude_degrees': alt.degrees,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        status = "☀️ Above horizon" if alt.degrees > 0 else "🌙 Below horizon"
        click.echo(f"""
  Solar Altitude
  ─────────────────────────────────────────
  Observer:   {observer.name}
  Time:       {jd_val.to_datetime().strftime('%Y-%m-%d %H:%M:%S')} UTC
  
  Altitude:   {alt.degrees:+.4f}°
  Status:     {status}
""")
        if vctx:
            click.echo(vctx.format_steps())
