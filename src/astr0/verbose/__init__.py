"""
Verbose output system for showing calculation steps.

The "show your work" engine that makes astr0 educational and debuggable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Callable
from contextlib import contextmanager


@dataclass
class Step:
    """A single calculation step."""
    title: str
    content: str
    level: int = 0


@dataclass
class VerboseContext:
    """
    Context for collecting verbose output.
    
    Use as a context manager to enable verbose mode:
    
        with VerboseContext() as ctx:
            result = some_calculation(verbose=ctx)
            ctx.print_steps()
    """
    
    steps: list[Step] = field(default_factory=list)
    enabled: bool = True
    _level: int = 0
    
    def add_step(self, title: str, content: str) -> None:
        """Add a calculation step."""
        if self.enabled:
            self.steps.append(Step(title, content, self._level))
    
    @contextmanager
    def section(self, name: str):
        """Create a nested section."""
        if self.enabled:
            self.add_step(f"── {name} ──", "")
        self._level += 1
        try:
            yield
        finally:
            self._level -= 1
    
    def print_steps(self, printer: Optional[Callable[[str], None]] = None) -> None:
        """Print all steps."""
        if printer is None:
            printer = print
        
        for step in self.steps:
            indent = "  " * step.level
            printer(f"{indent}┌─ {step.title}")
            if step.content:
                for line in step.content.split('\n'):
                    printer(f"{indent}│  {line}")
            printer(f"{indent}└{'─' * 40}")
    
    def format_steps(self) -> str:
        """Format all steps as a string."""
        lines = []
        
        for step in self.steps:
            indent = "  " * step.level
            lines.append(f"{indent}┌─ {step.title}")
            if step.content:
                for line in step.content.split('\n'):
                    lines.append(f"{indent}│  {line}")
            lines.append(f"{indent}└{'─' * 40}")
        
        return '\n'.join(lines)
    
    def to_dict(self) -> list[dict]:
        """Convert steps to list of dicts (for JSON output)."""
        return [
            {
                'title': s.title,
                'content': s.content,
                'level': s.level
            }
            for s in self.steps
        ]
    
    def clear(self) -> None:
        """Clear all steps."""
        self.steps.clear()
    
    def __enter__(self) -> VerboseContext:
        return self
    
    def __exit__(self, *args) -> None:
        pass


def step(ctx: Optional[VerboseContext], title: str, content: str) -> None:
    """
    Add a calculation step to the verbose context.
    
    This is the main function used by calculation modules to record
    their work.
    
    Args:
        ctx: Verbose context (if None, does nothing)
        title: Step title
        content: Step content (can be multiline)
    """
    if ctx is not None:
        ctx.add_step(title, content)


# Global verbose context for simple use cases
_global_context: Optional[VerboseContext] = None


def get_global_context() -> Optional[VerboseContext]:
    """Get the global verbose context."""
    return _global_context


def set_global_context(ctx: Optional[VerboseContext]) -> None:
    """Set the global verbose context."""
    global _global_context
    _global_context = ctx


@contextmanager
def verbose_mode():
    """
    Context manager for global verbose mode.
    
    Usage:
        with verbose_mode() as ctx:
            # All calculations in this block will record steps
            result = some_calculation()  # Uses global context
            ctx.print_steps()
    """
    ctx = VerboseContext()
    set_global_context(ctx)
    try:
        yield ctx
    finally:
        set_global_context(None)
