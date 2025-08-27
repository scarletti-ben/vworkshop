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
import subprocess
import traceback
import yaml
from argparse import (
    ArgumentParser, 
    Namespace
)
from pathlib import Path

# < =======================================================
# < Declarations
# < =======================================================

# - =========================
# - Constants
# - =========================

LOCAL: Path = Path(__file__).parent
BLUEPRINTS: Path = LOCAL / "blueprints"
PIECES: Path = LOCAL / "pieces"

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

    def preview(self, indent: int = 0) -> None:
        """Print a tree-style preview of the blueprint"""

        prefix: str = " " * indent

        def walk(d: dict, prefix: str = "") -> None:
            """Recursively print tree structure"""
            for i, (key, val) in enumerate(d.items()):
                connector = "└── " if i == len(d) - 1 else "├── "
                print(prefix + connector + key)
                if isinstance(val, dict):
                    extension = "    " if i == len(d) - 1 else "│   "
                    walk(val, prefix + extension)

        print(prefix + "Default:")
        walk(self.default, prefix + "  ")
        if self.optional:
            print(prefix + "Optional:")
            walk(self.optional, prefix + "  ")

# - =========================
# - Functions
# - =========================

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

def open_vscode() -> None:
    """Open VSCode to the vworkshop directory"""
    directory_path: Path = LOCAL
    subprocess.run(["code.cmd", directory_path])

def load_blueprint(code: str) -> Blueprint:
    """Create a Blueprint instance from YAML"""

    blueprint_path: Path = BLUEPRINTS / f"blueprint_{code}.yaml"

    if not blueprint_path.exists():
        print(f"Error: Blueprint '{code}' not found at {blueprint_path}")
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
        base_path: Path
    ) -> None:
    """Recursively create files from blueprint dictionary"""

    for name, source in blueprint.items():
        if isinstance(source, dict):
            # Handle directory
            dir_path = base_path / name
            dir_path.mkdir(exist_ok = True)
            create_files_from_blueprint(source, dir_path)
        else:
            # Handle file
            source_path = PIECES / source
            target_path = base_path / name
            
            if not source_path.exists():
                print(f"Warning: Piece {source_path} not found, skipping...")
                continue
            
            # Ensure target directory exists
            target_path.parent.mkdir(parents = True, exist_ok = True)
            
            try:
                # content = source_path.read_text(encoding = 'utf-8')
                # target_path.write_text(content, encoding = 'utf-8')
                content = source_path.read_bytes()
                target_path.write_bytes(content) 
                print(f"Created: {target_path}")

            except Exception as e:
                print(f"Error creating {target_path}: {e}")
                traceback.print_exc()

def create_template(
        code: str, 
        target_dir: Optional[str] = None,
        repository: bool = False,
        skipping: bool = False
    ) -> None:
    """Create template from a YAML blueprint"""

    blueprint = load_blueprint(code)
    
    print(f"Template: {blueprint.name}")
    print(f"Description: {blueprint.description}")
    # print(f"Preview: ")
    # blueprint.preview(2)
    
    # Determine target directory
    if target_dir is None:
        if skipping:
            target_dir = blueprint.name
        else:
            target_dir = input(f"Enter target directory name (default: {blueprint.name}): ").strip()
            if target_dir == '':
                target_dir = blueprint.name
    
    target_path = Path(target_dir)
    
    if target_path.exists() and not skipping:
        if not confirmation(f"Directory '{target_dir}' exists. Continue?"):
            print("Cancelled")
            return
    
    target_path.mkdir(exist_ok = True)
    # print(f"Target directory: {target_path.absolute()}")
    
    # Create default files
    print("\nCreating default files...")
    for section_name, section_dict in blueprint.default.items():
        base_path = target_path if section_name == 'root' else target_path / section_name
        create_files_from_blueprint(section_dict, base_path)
    
    # Handle optional files
    if blueprint.optional: 
        print("\nProcessing optional files...")

        for option_name, option_data in blueprint.optional.items():
            should_include = False

            if skipping:
                should_include = True
            elif option_name == "repository" and repository:
                should_include = True
            else:
                should_include = confirmation(f"Include optional section '{option_name}'?")
            
            if should_include:
                print(f"Including optional section: {option_name}")
                for section_name, section_dict in option_data.items():
                    base_path = target_path if section_name == 'root' else target_path / section_name
                    create_files_from_blueprint(section_dict, base_path)
    
    print(f"\nTemplate created at '/{target_dir}'")

# ~ =======================================================
# ~ Entry Point
# ~ =======================================================

def main() -> None:
    """Entry point function for vworkshop"""

    # ~ =========================
    # ~ Argument Setup
    # ~ =========================

    # Create an ArgumentParser instance and add help text for -h
    parser = ArgumentParser(
        prog = "vworkshop",
        description = "Create template folders from YAML blueprints"
    )

    # Add optional positonal argument 'blueprint', with default
    parser.add_argument(
        "blueprint",
        nargs = "?",
        default = None,
        help = "Blueprint code [optional] ('001' => 'blueprint_001.yaml)"
    )

    # Add optional positonal argument 'target'
    parser.add_argument(
        "target",
        nargs = "?",
        help = "Target directory name [optional]"
    )

    # Add optional flag '--skip'
    parser.add_argument(
        "-s", "--skip",
        action = "store_true",
        help = "skip all confirmations"
    )

    # Add optional flag '--repository'
    parser.add_argument(
        "-r", "--repository",
        action = "store_true",
        help = "include repository files"
    )

    # ! =========================
    # ! Experimental Flags
    # ! =========================

    # Add experimental flag '--code'
    parser.add_argument(
        "-vs", "--code",
        action = "store_true",
        help = "open VSCode"
    )

    # Add experimental flag '--favourite'
    parser.add_argument(
        "-f", "--favourite",
        action = "store_true",
        help = "generate favourite"
    )

    # ~ =========================
    # ~ Argument Parsing
    # ~ =========================

    # Parse known arguments, raise an error for unknown arguments
    args: Namespace = parser.parse_args()

    # - =========================
    # - Argument Checking
    # - =========================

    if args.code:
        open_vscode()
        sys.exit(0)

    if args.favourite:
        create_template('002', 'favourite', False, True)
        sys.exit(0)

    if args.blueprint is None:
        print("\nBlueprint is None")
        sys.exit(0)

    # > =========================
    # > Execution
    # > =========================

    print('\n' * 4)

    try:
        create_template(args.blueprint, args.target, args.repository, args.skip)

    except KeyboardInterrupt:
        print("\nCancelled by user")
        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)

# > =======================================================
# > Execution
# > =======================================================

if __name__ == "__main__":
    main()