import logging
from subprocess import Popen, PIPE

import subprocess

import argparse


logging.basicConfig(encoding="utf-8", level=logging.DEBUG)


def main(paths: list[str], save: str | None) -> bytes:
    """Создаёт архив и помещает его содержимое в переменную archive

    Ключевые аргументы:
    paths -- список файлов и папок для архивации
    save -- имя файла архива, необязательный параметр
    """

    process = subprocess.check_output("pwd")
    logging.info("текущая папка %s", (process, ))

    process = Popen(["zip", "-r", "-", *paths], stdout=PIPE, stderr=None)
    archive, _ = process.communicate()
    logging.info("размер архива %.f байт" % (len(archive), ))

    if save is not None:
        with open(save, "wb") as fh:
            fh.write(archive)

    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Получение списка файлов/папок для архивации.')
    parser.add_argument('paths', metavar='N', type=str, nargs='+',
                        help='список файлов/папок')
    parser.add_argument('--save', type=str,
                        help='имя файла архива')

    args = parser.parse_args()

    _ = main(args.paths, args.save)
