"""Entry point script for vworkshop, invoked from batch"""
# < =======================================================
# < Imports
# < =======================================================

# - =========================
# - Typing
# - =========================

from __future__ import annotations
from dataclasses import dataclass
from typing import (
    Any,
    Optional,
    Dict
)

# - =========================
# - General
# - =========================

import sys
import yaml
from argparse import ArgumentParser
from pathlib import Path

# < =======================================================
# < Declarations
# < =======================================================

# - =========================
# - Constants
# - =========================

BLUEPRINTS_DIR: Path = Path("blueprints")
PIECES_DIR: Path = Path("pieces")

# - =========================
# - Classes
# - =========================

@dataclass
class Blueprint:
    """Blueprint for a vworkshop template"""

    name: str
    description: str
    default: Dict[str, Any]
    optional: Optional[Dict[str, Any]] = None

# - =========================
# - Functions
# - =========================

def load_blueprint(blueprint_name: str) -> Blueprint:
    """Load YAML file to Blueprint instance"""

    blueprint_path: Path = BLUEPRINTS_DIR / f"blueprint_{blueprint_name}.yaml"

    if not blueprint_path.exists():
        print(f"Error: Blueprint '{blueprint_name}' not found at {blueprint_path}")
        sys.exit(1)
    
    with open(blueprint_path, 'r') as f:
        data: Any = yaml.safe_load(f)
    
    return Blueprint(
        name = data['name'],
        description = data['description'],
        default = data['default'],
        optional = data.get('optional', {})
    )

def create_files_from_blueprint(
        blueprint: Dict[str, Any], 
        base_path: Path, 
        pieces_dir: Path
    ) -> None:
    """Recursively create files from blueprint dictionary"""

    for name, source in blueprint.items():
        if isinstance(source, dict):
            # Handle directory
            dir_path = base_path / name
            dir_path.mkdir(exist_ok = True)
            create_files_from_blueprint(source, dir_path, pieces_dir)
        else:
            # Handle file
            source_path = pieces_dir / source
            target_path = base_path / name
            
            if not source_path.exists():
                print(f"Warning: Piece {source_path} not found, skipping...")
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

def create_template(
        blueprint_name: str, 
        enabled_options: list[str], 
        target_dir: Optional[str] = None
    ) -> None:
    """Create template from a YAML blueprint"""

    blueprint = load_blueprint(blueprint_name)
    
    print(f"Creating template: {blueprint.name}")
    print(f"Description: {blueprint.description}")
    
    # Determine target directory
    if target_dir is None:
        target_dir = input(f"Enter target directory name (default: {blueprint.name}): ").strip()
        if not target_dir:
            target_dir = blueprint.name
    
    target_path = Path(target_dir)
    pieces_dir = Path("pieces")
    
    if target_path.exists():
        if not confirmation(f"Directory '{target_dir}' exists. Continue?"):
            print("Cancelled")
            return
    
    target_path.mkdir(exist_ok = True)
    print(f"Target directory: {target_path.absolute()}")
    
    # Create default files
    print("\nCreating default files...")
    for section_name, blueprint in blueprint.default.items():
        base_path = target_path if section_name == 'root' else target_path / section_name
        create_files_from_blueprint(blueprint, base_path, pieces_dir)
    
    # Handle optional files
    if blueprint.optional:
        print("\nProcessing optional files...")
        for option_name, option_data in blueprint.optional.items():
            should_include = False
            
            # Check if option was passed as argument
            if f"-{option_name}" in enabled_options:
                should_include = True
                print(f"Including optional section: {option_name}")
            else:
                # Ask user
                should_include = confirmation(f"Include optional section '{option_name}'?")
            
            if should_include:
                for section_name, blueprint in option_data.items():
                    base_path = target_path if section_name == 'root' else target_path / section_name
                    create_files_from_blueprint(blueprint, base_path, pieces_dir)
    
    print(f"\nTemplate '{blueprint.name}' created successfully in '{target_dir}'!")

# ~ =======================================================
# ~ Entry Point
# ~ =======================================================

def main() -> None:
    """Entry point function for vworkshop"""

    # ? Note: Description is shown for python main.py -h

    parser = ArgumentParser(
        description = "Create template folders from YAML blueprints"
    )

    parser.add_argument(
        "blueprint", 
        help = "Blueprint name (e.g., '001')"
    )
    parser.add_argument(
        "target", 
        nargs = "?", 
        help = "Target directory name (optional)"
    )

    # parser.add_argument("-r", "--repository", action = "store_true")

    # Parse known arguments to handle optional flags like -repository
    args, unknown = parser.parse_known_args()
    
    # Extract optional flags
    enabled_options = [arg for arg in unknown if arg.startswith('-')]
    
    if not args.blueprint:
        print("Error: Blueprint name is required")
        print("Usage: vworkshop <blueprint_name> [target_dir] [-option1] [-option2]")
        sys.exit(1)
    
    try:
        create_template(args.blueprint, enabled_options, args.target)

    except KeyboardInterrupt:
        print("\nCancelled by user")
        sys.exit(130)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

# > =======================================================
# > Execution
# > =======================================================

if __name__ == "__main__":
    main()