"""ArchitecturalComponent model for system components described in documentation."""
from dataclasses import dataclass
from typing import List


@dataclass
class ArchitecturalComponent:
    """Represents system components described across TRANSRAPPORT.md and ARCHITECTURE.md."""
    
    component_name: str
    description: str
    source_files: List[str]
    dependencies: List[str]
    cli_commands: List[str]
    
    def __post_init__(self) -> None:
        """Ensure lists are initialized."""
        if self.source_files is None:
            self.source_files = []
        if self.dependencies is None:
            self.dependencies = []
        if self.cli_commands is None:
            self.cli_commands = []
    
    @classmethod
    def create_engine_component(cls, name: str, description: str) -> "ArchitecturalComponent":
        """Create an architectural component for engine parts (ATO-Engine, SEM-Engine, etc.)."""
        return cls(
            component_name=name,
            description=description,
            source_files=[],
            dependencies=[],
            cli_commands=[]
        )
    
    @classmethod
    def create_cli_component(cls, name: str, description: str, commands: List[str]) -> "ArchitecturalComponent":
        """Create an architectural component for CLI parts."""
        return cls(
            component_name=name,
            description=description,
            source_files=[],
            dependencies=[],
            cli_commands=commands
        )
    
    def add_source_file(self, file_path: str) -> None:
        """Add a source file where this component is described."""
        if file_path not in self.source_files:
            self.source_files.append(file_path)
    
    def add_dependency(self, component_name: str) -> None:
        """Add a dependency to another component."""
        if component_name not in self.dependencies:
            self.dependencies.append(component_name)
    
    def add_cli_command(self, command: str) -> None:
        """Add a CLI command associated with this component."""
        if command not in self.cli_commands:
            self.cli_commands.append(command)
    
    def is_mentioned_in_file(self, file_path: str) -> bool:
        """Check if this component is mentioned in the given file."""
        return file_path in self.source_files
    
    def get_summary(self) -> str:
        """Get a summary of this component for display."""
        summary = f"{self.component_name}: {self.description}"
        
        if self.cli_commands:
            commands_str = ", ".join(self.cli_commands)
            summary += f" (Commands: {commands_str})"
            
        if self.dependencies:
            deps_str = ", ".join(self.dependencies)
            summary += f" (Depends on: {deps_str})"
            
        return summary