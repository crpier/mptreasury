from pathlib import Path
from icecream import sys

from result import Ok, Err, Result, as_result

from loguru import logger

from mptreasury.utils import raise_err, ic

logger.configure()

@as_result(OSError)
def scan_folder(folder: Path) -> int:
    count = 0
    for dirpath, dirnames, filenames in folder.walk(on_error=raise_err):
        count += 1
    return count


@logger.catch
def main():
    match scan_folder(Path(".")):
        case Ok(count):
            logger.info(f"There are %s places to check", count)
        case Err(err):
            ic(err)


if __name__ == "__main__":
    main()
