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


def format_output(
    result: Result,
    output_format: str = 'plain',
    verbose: bool = False
) -> str:
    """
    Format a result using the specified formatter.
    
    Args:
        result: The result to format
        output_format: One of 'plain', 'json', 'rich'
        verbose: Whether to show verbose output
    
    Returns:
        Formatted string
    """
    formatters = {
        'plain': PlainFormatter(show_verbose=verbose),
        'json': JSONFormatter(),
        'rich': RichFormatter(show_verbose=verbose),
    }
    
    formatter = formatters.get(output_format, PlainFormatter(show_verbose=verbose))
    return formatter.format(result)
