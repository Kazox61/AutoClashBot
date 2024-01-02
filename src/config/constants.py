from pathlib import Path
import os

MAIN_DIR = Path(os.curdir).joinpath("..").absolute() if os.path.basename(
    os.path.abspath(os.curdir)) == "src" else Path(os.curdir).absolute()
ASSETS_DIR = MAIN_DIR.joinpath("assets")
TEMPLATE_DIR = ASSETS_DIR.joinpath("templates")
