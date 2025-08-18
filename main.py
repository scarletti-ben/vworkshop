"""Entry point script for vworkshop, invoked from batch"""
# < =======================================================
# < Typing Imports
# < =======================================================

from __future__ import annotations
from abc import (
    ABC, 
    abstractmethod
)
from dataclasses import (
    dataclass, 
    field
)
from typing import (
    TYPE_CHECKING,
    Any,
    Union,
    Optional,
    Literal,
    LiteralString,
    TypedDict, 
    Iterable,
    Callable,
    TypeVar,
    Dict
)
if TYPE_CHECKING:
    pass

# < =======================================================
# < General Imports
# < =======================================================

import sys
import os
import argparse
import yaml
from pathlib import Path

# < =======================================================
# < Declarations
# < =======================================================

@dataclass
class WorkshopConfig:
    """Configuration for workshop template"""

    name: str
    description: str
    default: Dict[str, Any]
    optional: Optional[Dict[str, Any]] = None

# < =======================================================
# < Utility Functions
# < =======================================================

def load_structure(structure_name: str) -> WorkshopConfig:
    """Load structure YAML file"""

    structure_path = Path(f"structures/structure_{structure_name}.yaml")
    
    if not structure_path.exists():
        print(f"Error: Structure '{structure_name}' not found at {structure_path}")
        sys.exit(1)
    
    with open(structure_path, 'r') as f:
        data = yaml.safe_load(f)
    
    return WorkshopConfig(
        name = data['name'],
        description = data['description'],
        default = data['default'],
        optional = data.get('optional', {})
    )

def create_files_from_structure(structure: Dict[str, Any], base_path: Path, pieces_dir: Path):
    """Recursively create files from structure"""

    for name, source in structure.items():
        if isinstance(source, dict):
            # Handle directory
            dir_path = base_path / name
            dir_path.mkdir(exist_ok = True)
            create_files_from_structure(source, dir_path, pieces_dir)
        else:
            # Handle file
            source_path = pieces_dir / source
            target_path = base_path / name
            
            if not source_path.exists():
                print(f"Warning: Template file {source_path} not found, skipping...")
                continue
            
            # Ensure target directory exists
            target_path.parent.mkdir(parents = True, exist_ok = True)
            
            try:
                content = source_path.read_text(encoding = 'utf-8')
                target_path.write_text(content, encoding = 'utf-8')
                print(f"Created: {target_path}")

            except Exception as e:
                print(f"Error creating {target_path}: {e}")

def confirmation(message: str) -> bool:
    """Prompt user for yes / no input"""
    while True:
        response = input(f"{message} (y/n): ").lower().strip()
        if response in ('y', 'yes'):
            return True
        elif response in ('n', 'no'):
            return False
        else:
            print("Please enter 'y' or 'n'")

def create_workshop(structure_name: str, enabled_options: list[str], target_dir: Optional[str] = None):
    """Create workshop from structure"""
    config = load_structure(structure_name)
    
    print(f"Creating workshop: {config.name}")
    print(f"Description: {config.description}")
    
    # Determine target directory
    if target_dir is None:
        target_dir = input(f"Enter target directory name (default: {config.name}): ").strip()
        if not target_dir:
            target_dir = config.name
    
    target_path = Path(target_dir)
    pieces_dir = Path("pieces")
    
    if target_path.exists():
        if not confirmation(f"Directory '{target_dir}' exists. Continue?"):
            print("Cancelled")
            return
    
    target_path.mkdir(exist_ok=True)
    print(f"Target directory: {target_path.absolute()}")
    
    # Create default files
    print("\nCreating default files...")
    for section_name, structure in config.default.items():
        base_path = target_path if section_name == 'root' else target_path / section_name
        create_files_from_structure(structure, base_path, pieces_dir)
    
    # Handle optional files
    if config.optional:
        print("\nProcessing optional files...")
        for option_name, option_data in config.optional.items():
            should_include = False
            
            # Check if option was passed as argument
            if f"-{option_name}" in enabled_options:
                should_include = True
                print(f"Including optional section: {option_name}")
            else:
                # Ask user
                should_include = confirmation(f"Include optional section '{option_name}'?")
            
            if should_include:
                for section_name, structure in option_data.items():
                    base_path = target_path if section_name == 'root' else target_path / section_name
                    create_files_from_structure(structure, base_path, pieces_dir)
    
    print(f"\nWorkshop '{config.name}' created successfully in '{target_dir}'!")

# < =======================================================
# < Entry Point
# < =======================================================

def main() -> None:
    """Entry point function for vworkshop"""

    parser = argparse.ArgumentParser(description="Create workshop projects from templates")
    parser.add_argument("structure", help = "Structure name (e.g., '001')")
    parser.add_argument("target", nargs = "?", help = "Target directory name (optional)")
    
    # Parse known args to handle optional flags like -repository
    args, unknown = parser.parse_known_args()
    
    # Extract optional flags (anything starting with -)
    enabled_options = [arg for arg in unknown if arg.startswith('-')]
    
    if not args.structure:
        print("Error: Structure name is required")
        print("Usage: vworkshop <structure_name> [target_dir] [-option1] [-option2]")
        sys.exit(1)
    
    try:
        create_workshop(args.structure, enabled_options, args.target)

    except KeyboardInterrupt:
        print("\nCancelled by user")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

# < =======================================================
# < Execution
# < =======================================================

if __name__ == "__main__":
    main()