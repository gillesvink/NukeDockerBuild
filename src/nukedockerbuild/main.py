"""Script that executes the dockerfile creator.

@maintainer: Gilles Vink
"""

import argparse
import logging
import sys
from pathlib import Path

from nukedockerbuild.creator.collector import (
    fetch_json_data,
    get_dockerfiles,
)
from nukedockerbuild.creator.create_dockerfiles import write_dockerfiles

FORMAT = "[%(asctime)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)


def _generate_dockerfiles(dockerfiles_directory: Path) -> None:
    """Generate dockerfiles in directory.

    Args:
        dockerfiles_directory: directory to write dockerfiles to.
    """
    json_data = fetch_json_data()
    dockerfiles = get_dockerfiles(data=json_data)
    write_dockerfiles(
        directory=Path(dockerfiles_directory), dockerfiles=dockerfiles
    )


def _parse_args(args: list[str]) -> argparse.Namespace:
    """Parse provided arguments."""
    parser = argparse.ArgumentParser(
        prog="NukeVersionParser",
        description=("CLI to create dockerfiles for all Nuke versions."),
    )
    parser.add_argument("--write_dir", required=True)
    return parser.parse_args(args)


def main() -> None:
    """Main pytest bootstrap entrypoint"""
    parsed_arguments = _parse_args(sys.argv[1:])
    if parsed_arguments.write_dir is None:
        msg = (
            "Provide the path to write to. For example: "
            "nuke-dockerbuild ./ for the current directory."
        )
        raise ValueError(msg)
    json_directory = Path(parsed_arguments.write_dir)
    _generate_dockerfiles(json_directory)


if __name__ == "__main__":
    main()
