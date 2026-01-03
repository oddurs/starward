"""
Output formatters for different display modes.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from astr0.verbose import VerboseContext


@dataclass
class Result:
    """A calculation result with metadata."""
    value: Any
    label: str = ""
    unit: str = ""
    verbose: Optional[VerboseContext] = None
    extra: dict = None
    
    def __post_init__(self):
        if self.extra is None:
            self.extra = {}


class Formatter(ABC):
    """Base class for output formatters."""
    
    @abstractmethod
    def format(self, result: Result) -> str:
        """Format a result for display."""
        pass


class PlainFormatter(Formatter):
    """Plain text formatter with optional verbose output."""
    
    def __init__(self, show_verbose: bool = False, unicode: bool = True):
        self.show_verbose = show_verbose
        self.unicode = unicode
    
    def format(self, result: Result) -> str:
        lines = []
        
        # Main result
        if result.label:
            lines.append(f"{result.label}: {result.value}{' ' + result.unit if result.unit else ''}")
        else:
            lines.append(f"{result.value}{' ' + result.unit if result.unit else ''}")
        
        # Extra info
        for key, value in result.extra.items():
            lines.append(f"  {key}: {value}")
        
        # Verbose steps
        if self.show_verbose and result.verbose:
            lines.append("")
            lines.append("═" * 50)
            lines.append("  Calculation Steps")
            lines.append("═" * 50)
            lines.append(result.verbose.format_steps())
        
        return '\n'.join(lines)


class JSONFormatter(Formatter):
    """JSON formatter for machine-readable output."""
    
    def __init__(self, pretty: bool = True):
        self.pretty = pretty
    
    def format(self, result: Result) -> str:
        data = {
            'result': self._serialize(result.value),
            'label': result.label,
            'unit': result.unit,
            **{k: self._serialize(v) for k, v in result.extra.items()}
        }
        
        if result.verbose:
            data['steps'] = result.verbose.to_dict()
        
        if self.pretty:
            return json.dumps(data, indent=2, default=str)
        return json.dumps(data, default=str)
    
    def _serialize(self, value: Any) -> Any:
        """Serialize a value for JSON."""
        if hasattr(value, 'degrees'):
            return {'degrees': value.degrees, 'formatted': str(value)}
        if hasattr(value, 'jd'):
            return {'jd': value.jd, 'formatted': str(value)}
        if hasattr(value, '__dict__'):
            return {k: self._serialize(v) for k, v in value.__dict__.items() if not k.startswith('_')}
        return value


class RichFormatter(Formatter):
    """Rich console formatter with colors and styling."""
    
    def __init__(self, show_verbose: bool = False):
        self.show_verbose = show_verbose
    
    def format(self, result: Result) -> str:
        # For now, delegate to plain formatter
        # TODO: Add rich console output
        return PlainFormatter(self.show_verbose).format(result)


class LaTeXFormatter(Formatter):
    """LaTeX formatter for mathematical output.
    
    Produces LaTeX code suitable for inclusion in documents.
    """
    
    def __init__(self, 
                 show_verbose: bool = False,
                 document_class: bool = False,
                 siunitx: bool = True):
        """
        Initialize LaTeX formatter.
        
        Args:
            show_verbose: Whether to include calculation steps
            document_class: Whether to include full document wrapper
            siunitx: Whether to use siunitx package for units
        """
        self.show_verbose = show_verbose
        self.document_class = document_class
        self.siunitx = siunitx
    
    def format(self, result: Result) -> str:
        lines = []
        
        if self.document_class:
            lines.extend([
                r"\documentclass{article}",
                r"\usepackage{amsmath}",
                r"\usepackage{amssymb}",
                r"\usepackage{siunitx}" if self.siunitx else "",
                r"\begin{document}",
                ""
            ])
        
        # Format the main result
        latex_value = self._to_latex(result.value)
        if result.label:
            lines.append(f"\\textbf{{{result.label}:}} ${latex_value}${self._format_unit(result.unit)}")
        else:
            lines.append(f"${latex_value}${self._format_unit(result.unit)}")
        
        # Extra info as a description list
        if result.extra:
            lines.append("")
            lines.append(r"\begin{description}")
            for key, value in result.extra.items():
                latex_val = self._to_latex(value)
                lines.append(f"  \\item[{key}] ${latex_val}$")
            lines.append(r"\end{description}")
        
        # Verbose steps as an align environment
        if self.show_verbose and result.verbose:
            lines.append("")
            lines.append(r"\subsection*{Calculation Steps}")
            lines.append(r"\begin{align*}")
            
            for i, step in enumerate(result.verbose._steps):
                label, formula = step.label, step.value
                # Clean up the formula for LaTeX
                latex_formula = self._formula_to_latex(str(formula))
                lines.append(f"  \\text{{{label}}} &= {latex_formula} \\\\")
            
            lines.append(r"\end{align*}")
        
        if self.document_class:
            lines.extend([
                "",
                r"\end{document}"
            ])
        
        return '\n'.join(lines)
    
    def _to_latex(self, value: Any) -> str:
        """Convert a value to LaTeX representation."""
        if hasattr(value, 'degrees'):
            # Angle - format in degrees by default
            deg = value.degrees
            if hasattr(value, 'to_dms'):
                d, m, s = value.to_dms()
                sign = "-" if deg < 0 else ""
                return f"{sign}{abs(d)}^\\circ{m}'{s:.2f}\""
            return f"{deg:.6f}^\\circ"
        
        if hasattr(value, 'jd'):
            return f"\\mathrm{{JD}}\\,{value.jd:.6f}"
        
        if isinstance(value, float):
            if abs(value) < 0.001 or abs(value) > 10000:
                # Scientific notation
                exp = int(f"{value:e}".split('e')[1])
                mantissa = value / (10 ** exp)
                return f"{mantissa:.4f} \\times 10^{{{exp}}}"
            return f"{value:.6f}"
        
        if isinstance(value, (int, str)):
            return str(value)
        
        # Fallback
        return str(value).replace('_', r'\_')
    
    def _format_unit(self, unit: str) -> str:
        """Format a unit string for LaTeX."""
        if not unit:
            return ""
        
        if self.siunitx:
            # Map common units to siunitx
            unit_map = {
                'deg': r'\si{\degree}',
                '°': r'\si{\degree}',
                'rad': r'\si{\radian}',
                'arcsec': r'\si{\arcsecond}',
                'arcmin': r'\si{\arcminute}',
                'AU': r'\si{\astronomicalunit}',
                'km': r'\si{\kilo\meter}',
                'km/s': r'\si{\kilo\meter\per\second}',
            }
            return " " + unit_map.get(unit, f"\\,\\mathrm{{{unit}}}")
        
        return f" \\,\\mathrm{{{unit}}}"
    
    def _formula_to_latex(self, formula: str) -> str:
        """Convert a formula string to proper LaTeX."""
        # Replace common patterns
        replacements = [
            ('sin', r'\sin'),
            ('cos', r'\cos'),
            ('tan', r'\tan'),
            ('arcsin', r'\arcsin'),
            ('arccos', r'\arccos'),
            ('arctan', r'\arctan'),
            ('sqrt', r'\sqrt'),
            ('**2', '^{2}'),
            ('**3', '^{3}'),
            ('*', r' \times '),
            ('/', r' / '),
            ('pi', r'\pi'),
            ('alpha', r'\alpha'),
            ('delta', r'\delta'),
            ('theta', r'\theta'),
            ('lambda', r'\lambda'),
            ('phi', r'\phi'),
            ('°', r'^\circ'),
        ]
        
        result = formula
        for old, new in replacements:
            result = result.replace(old, new)
        
        return result


def format_angle_latex(angle, mode: str = 'dms') -> str:
    """
    Format an angle for LaTeX output.
    
    Args:
        angle: An Angle object
        mode: 'dms' for degrees/arcmin/arcsec, 'hms' for hours/min/sec, 'deg' for decimal
        
    Returns:
        LaTeX string
    """
    if mode == 'hms':
        h, m, s = angle.to_hms()
        return f"${h}^{{\\mathrm{{h}}}}{m}^{{\\mathrm{{m}}}}{s:.2f}^{{\\mathrm{{s}}}}$"
    elif mode == 'dms':
        d, m, s = angle.to_dms()
        sign = "-" if angle.degrees < 0 else "+"
        return f"${sign}{abs(d)}°{m}'{s:.2f}\"$"
    else:  # deg
        return f"${angle.degrees:.6f}°$"


def format_coordinate_latex(coord) -> str:
    """
    Format a coordinate for LaTeX output.
    
    Args:
        coord: An ICRSCoord or similar coordinate object
        
    Returns:
        LaTeX string
    """
    ra_h, ra_m, ra_s = coord.ra.to_hms()
    dec_d, dec_m, dec_s = coord.dec.to_dms()
    dec_sign = "-" if coord.dec.degrees < 0 else "+"
    
    return (f"$\\alpha = {ra_h}^{{\\mathrm{{h}}}}{ra_m}^{{\\mathrm{{m}}}}{ra_s:.2f}^{{\\mathrm{{s}}}}$, "
            f"$\\delta = {dec_sign}{abs(dec_d)}°{dec_m}'{dec_s:.2f}\"$")


def format_table_latex(headers: list, rows: list, caption: str = None) -> str:
    """
    Format a table for LaTeX output.
    
    Args:
        headers: Column headers
        rows: List of row data (lists)
        caption: Optional table caption
        
    Returns:
        LaTeX table string
    """
    n_cols = len(headers)
    col_spec = '|' + '|'.join(['c'] * n_cols) + '|'
    
    lines = [
        r"\begin{table}[h]",
        r"\centering",
        f"\\begin{{tabular}}{{{col_spec}}}",
        r"\hline",
        " & ".join(f"\\textbf{{{h}}}" for h in headers) + r" \\",
        r"\hline",
    ]
    
    for row in rows:
        lines.append(" & ".join(str(cell) for cell in row) + r" \\")
    
    lines.extend([
        r"\hline",
        r"\end{tabular}",
    ])
    
    if caption:
        lines.append(f"\\caption{{{caption}}}")
    
    lines.append(r"\end{table}")
    
    return '\n'.join(lines)


def format_output(
    result: Result,
    output_format: str = 'plain',
    verbose: bool = False
) -> str:
    """
    Format a result using the specified formatter.
    
    Args:
        result: The result to format
        output_format: One of 'plain', 'json', 'rich', 'latex'
        verbose: Whether to show verbose output
    
    Returns:
        Formatted string
    """
    formatters = {
        'plain': PlainFormatter(show_verbose=verbose),
        'json': JSONFormatter(),
        'rich': RichFormatter(show_verbose=verbose),
        'latex': LaTeXFormatter(show_verbose=verbose),
    }
    
    formatter = formatters.get(output_format, PlainFormatter(show_verbose=verbose))
    return formatter.format(result)
