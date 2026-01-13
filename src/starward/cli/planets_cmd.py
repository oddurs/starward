"""
Planet-related CLI commands.
"""

from __future__ import annotations

import click
from typing import Optional

from starward.core.planets import (
    Planet, PlanetPosition, PLANET_SYMBOLS,
    planet_position, all_planet_positions,
    planet_altitude, planet_rise, planet_set, planet_transit,
)
from starward.core.observer import Observer, get_observer
from starward.core.time import JulianDate, jd_now
from starward.verbose import VerboseContext


# Valid planet names for CLI
PLANET_NAMES = [p.value.lower() for p in Planet]


def _get_planet(name: str) -> Planet:
    """Convert string to Planet enum."""
    name_lower = name.lower()
    for p in Planet:
        if p.value.lower() == name_lower:
            return p
    raise click.ClickException(f"Unknown planet: {name}. Valid planets: {', '.join(PLANET_NAMES)}")


def _get_observer_from_options(lat: Optional[float], lon: Optional[float],
                                observer_name: Optional[str]) -> Optional[Observer]:
    """Get observer from CLI options."""
    if lat is not None and lon is not None:
        return Observer.from_degrees("CLI", lat, lon)
    elif observer_name:
        obs = get_observer(observer_name)
        if obs is None:
            raise click.ClickException(f"Observer '{observer_name}' not found. Use 'starward observer list' to see available observers.")
        return obs
    else:
        obs = get_observer()  # Default observer
        if obs is None:
            raise click.ClickException(
                "No observer specified. Use --lat/--lon or --observer, "
                "or add a default observer with 'starward observer add'"
            )
        return obs


@click.group(name='planets')
def planets_group():
    """
    Planetary positions and events.

    \b
    Calculate positions of Mercury, Venus, Mars, Jupiter,
    Saturn, Uranus, and Neptune.

    \b
    Examples:
        starward planets position mars           # Mars position
        starward planets all                     # All planet positions
        starward planets rise jupiter --lat 40.7 --lon -74.0
    """
    pass


@planets_group.command()
@click.argument('planet_name', type=click.Choice(PLANET_NAMES, case_sensitive=False))
@click.option('--jd', type=float, help='Julian Date (default: now)')
@click.pass_context
def position(ctx, planet_name: str, jd: Optional[float]):
    """Show position of a planet."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    planet = _get_planet(planet_name)
    jd_val = JulianDate(jd) if jd else jd_now()
    pos = planet_position(planet, jd_val, vctx)

    if output_fmt == 'json':
        import json
        data = {
            'planet': planet.value,
            'jd': jd_val.jd,
            'ra_hours': pos.ra.hours,
            'ra_degrees': pos.ra.degrees,
            'dec_degrees': pos.dec.degrees,
            'distance_au': pos.distance_au,
            'helio_distance_au': pos.helio_distance,
            'magnitude': pos.magnitude,
            'elongation_degrees': pos.elongation.degrees,
            'phase_angle_degrees': pos.phase_angle.degrees,
            'angular_diameter_arcsec': pos.angular_diameter.degrees * 3600,
            'illumination': pos.illumination,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    elif output_fmt == 'rich':
        from starward.output.console import print_planet_position
        dt = jd_val.to_datetime()
        symbol = PLANET_SYMBOLS.get(planet, "")
        print_planet_position(
            symbol=symbol,
            name=planet.value,
            time_str=dt.strftime('%Y-%m-%d %H:%M:%S'),
            jd=jd_val.jd,
            ra=pos.ra.format_hms(),
            dec=pos.dec.format_dms(),
            distance_au=pos.distance_au,
            helio_distance=pos.helio_distance,
            magnitude=pos.magnitude,
            elongation=pos.elongation.degrees,
            illumination=pos.illumination,
            angular_diameter=pos.angular_diameter.degrees * 3600,
            vctx=vctx,
        )
    else:
        dt = jd_val.to_datetime()
        symbol = PLANET_SYMBOLS.get(planet, "")
        click.echo(f"""
  {symbol}  {planet.value}
  ─────────────────────────────────────────
  Time:       {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  JD:         {jd_val.jd:.6f}

  Equatorial:
    RA:       {pos.ra.format_hms()}
    Dec:      {pos.dec.format_dms()}

  Distance:
    From Earth: {pos.distance_au:.6f} AU
    From Sun:   {pos.helio_distance:.6f} AU

  Visual:
    Magnitude:  {pos.magnitude:+.2f}
    Elongation: {pos.elongation.degrees:.1f}°
    Phase:      {pos.illumination * 100:.1f}% illuminated
    Diameter:   {pos.angular_diameter.degrees * 3600:.2f}\"
""")
        if vctx:
            click.echo(vctx.format_steps())


@planets_group.command(name='all')
@click.option('--jd', type=float, help='Julian Date (default: now)')
@click.pass_context
def all_cmd(ctx, jd: Optional[float]):
    """Show positions of all planets."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    jd_val = JulianDate(jd) if jd else jd_now()
    positions = all_planet_positions(jd_val, vctx)

    if output_fmt == 'json':
        import json
        data = {
            'jd': jd_val.jd,
            'planets': {}
        }
        for planet, pos in positions.items():
            data['planets'][planet.value.lower()] = {
                'ra_degrees': pos.ra.degrees,
                'dec_degrees': pos.dec.degrees,
                'distance_au': pos.distance_au,
                'magnitude': pos.magnitude,
                'elongation_degrees': pos.elongation.degrees,
            }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    elif output_fmt == 'rich':
        from starward.output.console import print_all_planets_table
        dt = jd_val.to_datetime()
        planets_data = []
        for planet in Planet:
            pos = positions[planet]
            symbol = PLANET_SYMBOLS.get(planet, " ")
            dec = pos.dec.format_dms()
            if pos.dec.degrees >= 0:
                dec = " " + dec
            planets_data.append({
                'symbol': symbol,
                'name': planet.value,
                'ra': pos.ra.format_hms(),
                'dec': dec,
                'distance': pos.distance_au,
                'magnitude': pos.magnitude,
                'elongation': pos.elongation.degrees,
            })
        print_all_planets_table(
            time_str=dt.strftime('%Y-%m-%d %H:%M:%S'),
            jd=jd_val.jd,
            planets_data=planets_data,
            vctx=vctx,
        )
    else:
        dt = jd_val.to_datetime()
        click.echo(f"""
  Planetary Positions
  ─────────────────────────────────────────
  Time: {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  JD:   {jd_val.jd:.6f}

  Planet       RA               Dec            Dist    Mag   Elong
  ───────────────────────────────────────────────────────────────────""")

        for planet in Planet:
            pos = positions[planet]
            symbol = PLANET_SYMBOLS.get(planet, " ")
            name = f"{symbol} {planet.value:<7}"
            ra = pos.ra.format_hms()
            dec = pos.dec.format_dms()
            # Add leading space for positive Dec to align with negative
            if pos.dec.degrees >= 0:
                dec = " " + dec
            click.echo(f"  {name}  {ra:<16} {dec:<16} {pos.distance_au:6.3f}  {pos.magnitude:+5.1f}  {pos.elongation.degrees:5.1f}°")

        click.echo()
        if vctx:
            click.echo(vctx.format_steps())


@planets_group.command(name='rise')
@click.argument('planet_name', type=click.Choice(PLANET_NAMES, case_sensitive=False))
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def rise_cmd(ctx, planet_name: str, lat: Optional[float], lon: Optional[float],
             observer_name: Optional[str], jd: Optional[float]):
    """Calculate planet rise time."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    planet = _get_planet(planet_name)
    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()

    rise_time = planet_rise(planet, observer, jd_val, vctx)

    if output_fmt == 'json':
        import json
        data = {
            'planet': planet.value,
            'observer': observer.name,
            'date_jd': jd_val.jd,
            'rise_jd': rise_time.jd if rise_time else None,
            'rise_utc': rise_time.to_datetime().isoformat() if rise_time else None,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        symbol = PLANET_SYMBOLS.get(planet, "")
        if rise_time:
            dt = rise_time.to_datetime()
            click.echo(f"""
  {symbol}  {planet.value} Rise
  ─────────────────────────────────────────
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  Rise Time:  {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Rise JD:    {rise_time.jd:.6f}
""")
        else:
            click.echo(f"""
  {symbol}  {planet.value} Rise
  ─────────────────────────────────────────
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  {planet.value} does not rise from this location on this date.
""")
        if vctx:
            click.echo(vctx.format_steps())


@planets_group.command(name='set')
@click.argument('planet_name', type=click.Choice(PLANET_NAMES, case_sensitive=False))
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def set_cmd(ctx, planet_name: str, lat: Optional[float], lon: Optional[float],
            observer_name: Optional[str], jd: Optional[float]):
    """Calculate planet set time."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    planet = _get_planet(planet_name)
    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()

    set_time = planet_set(planet, observer, jd_val, vctx)

    if output_fmt == 'json':
        import json
        data = {
            'planet': planet.value,
            'observer': observer.name,
            'date_jd': jd_val.jd,
            'set_jd': set_time.jd if set_time else None,
            'set_utc': set_time.to_datetime().isoformat() if set_time else None,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        symbol = PLANET_SYMBOLS.get(planet, "")
        if set_time:
            dt = set_time.to_datetime()
            click.echo(f"""
  {symbol}  {planet.value} Set
  ─────────────────────────────────────────
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  Set Time:   {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Set JD:     {set_time.jd:.6f}
""")
        else:
            click.echo(f"""
  {symbol}  {planet.value} Set
  ─────────────────────────────────────────
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  {planet.value} does not set from this location on this date.
""")
        if vctx:
            click.echo(vctx.format_steps())


@planets_group.command(name='transit')
@click.argument('planet_name', type=click.Choice(PLANET_NAMES, case_sensitive=False))
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def transit_cmd(ctx, planet_name: str, lat: Optional[float], lon: Optional[float],
                observer_name: Optional[str], jd: Optional[float]):
    """Calculate planet meridian transit time."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    planet = _get_planet(planet_name)
    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()

    transit_time = planet_transit(planet, observer, jd_val, vctx)
    pos = planet_position(planet, transit_time)
    alt = planet_altitude(planet, observer, transit_time)

    if output_fmt == 'json':
        import json
        data = {
            'planet': planet.value,
            'observer': observer.name,
            'date_jd': jd_val.jd,
            'transit_jd': transit_time.jd,
            'transit_utc': transit_time.to_datetime().isoformat(),
            'transit_altitude_degrees': alt.degrees,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        symbol = PLANET_SYMBOLS.get(planet, "")
        dt = transit_time.to_datetime()
        click.echo(f"""
  {symbol}  {planet.value} Transit
  ─────────────────────────────────────────
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  Transit:    {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Transit JD: {transit_time.jd:.6f}
  Altitude:   {alt.degrees:.1f}°
""")
        if vctx:
            click.echo(vctx.format_steps())


@planets_group.command(name='altitude')
@click.argument('planet_name', type=click.Choice(PLANET_NAMES, case_sensitive=False))
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: now)')
@click.pass_context
def altitude_cmd(ctx, planet_name: str, lat: Optional[float], lon: Optional[float],
                 observer_name: Optional[str], jd: Optional[float]):
    """Calculate current altitude of a planet."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    planet = _get_planet(planet_name)
    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()

    alt = planet_altitude(planet, observer, jd_val, vctx)
    pos = planet_position(planet, jd_val)

    if output_fmt == 'json':
        import json
        data = {
            'planet': planet.value,
            'observer': observer.name,
            'jd': jd_val.jd,
            'altitude_degrees': alt.degrees,
            'is_visible': alt.degrees > 0,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        symbol = PLANET_SYMBOLS.get(planet, "")
        dt = jd_val.to_datetime()
        visibility = "Above horizon" if alt.degrees > 0 else "Below horizon"
        click.echo(f"""
  {symbol}  {planet.value} Altitude
  ─────────────────────────────────────────
  Time:       {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  Altitude:   {alt.degrees:+.2f}°
  Status:     {visibility}
""")
        if vctx:
            click.echo(vctx.format_steps())
