from pathlib import Path

__PROJECT_ROOT__ = Path(__file__).parent.parent


def path_from_root(*args):
    return __PROJECT_ROOT__.joinpath(*args)
