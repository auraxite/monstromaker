"""Точка входа для ``python -m monstromaker`` и команды ``monstromaker``."""

import argparse
import random
import sys

from monstromaker.cli import prompt_player_names, run_game
from monstromaker.i18n import setup_i18n


def main() -> None:
	"""Разобрать аргументы, настроить локаль и запустить игру."""
	parser = argparse.ArgumentParser(
		prog="monstromaker",
		description="Монстродел — карточная игра на страшность монстров.",
	)
	parser.add_argument(
		"--lang",
		default="ru_RU",
		metavar="LOCALE",
		help="Язык интерфейса: ru_RU (по умолчанию) или en_US",
	)
	parser.add_argument(
		"--players",
		nargs="*",
		metavar="NAME",
		help="Имена игроков (2-4); пропусти для ввода вручную",
	)
	parser.add_argument(
		"--script",
		metavar="FILE",
		help="Файл с командами для автоматического ввода (stdin-редирект)",
	)
	parser.add_argument(
		"--seed",
		type=int,
		metavar="N",
		help="Зерно генератора случайных чисел (воспроизводимая раздача карт)",
	)

	args = parser.parse_args()
	setup_i18n(args.lang)

	if args.seed is not None:
		random.seed(args.seed)

	if args.script:
		sys.stdin = open(args.script, encoding="utf-8")  # noqa: WPS515

	if args.players and 2 <= len(args.players) <= 4:
		player_names = args.players
	else:
		player_names = prompt_player_names()

	run_game(player_names)


if __name__ == "__main__":
	main()
