"""Командный интерфейс Монстродела."""

import cmd
import sys
from typing import List, Optional
from monstromaker.display import (
	clear_screen,
	render_card_detail,
	render_discard_pile,
	render_end_screen,
	render_hand,
	render_header,
	render_last_action,
	render_menu,
	render_monster_list,
	render_monster_zones,
	render_player_list,
	render_spy_reveal,
	render_turn_end,
	render_turn_intro,
	show_winner_cowsay,
)
from monstromaker.game import Game, TurnResult
from monstromaker.i18n import _
from monstromaker.player import Player


def _safe_input(prompt: str) -> str:
	"""Прочитать строку ввода; вернуть пустую строку при EOF.

	Аргументы:
		prompt: Текст-приглашение перед вводом.

	Возвращает:
		Очищенную от пробелов строку ввода.
	"""
	try:
		return input(prompt).strip()
	except EOFError:
		sys.exit(0)


def _pick_number(prompt: str, lo: int, hi: int) -> Optional[int]:
	"""Спрашивать число в [lo, hi], либо '0'/'н' для отмены.

	Аргументы:
		prompt: Вопрос игроку.
		lo: Минимальное допустимое значение.
		hi: Максимальное допустимое значение (включительно).

	Возвращает:
		Индекс с нуля (значение - 1) или None при отмене.
	"""
	while True:
		answer = _safe_input(prompt)
		if answer in ("0", "н", "n", ""):
			return None
		if answer.isdigit():
			val = int(answer)
			if lo <= val <= hi:
				return val - 1
		print(_("Введите число от %(lo)d до %(hi)d, или 0 для отмены.") % {
			"lo": lo, "hi": hi,
		})


class TurnCLI(cmd.Cmd):
	"""Интерфейс одного хода игрока."""

	prompt = "> "
	intro = ""
	use_rawinput = True
	# Разрешаем кириллицу в названии команды (т/п и т.п.).
	identchars = (
		cmd.Cmd.identchars
		+ "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
		+ "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
	)

	def __init__(self, game: Game) -> None:
		"""Инициализировать CLI для одного хода."""
		super().__init__()
		self.game = game
		self.drew: Optional[object] = None
		self.overflow: Optional[object] = None
		self._done: bool = False
		self.result: Optional[TurnResult] = None

	def preloop(self) -> None:
		"""В начале хода взять карту и отрисовать экран."""
		self.drew, self.overflow = self.game.begin_turn()
		self._render_screen()

	def postcmd(self, stop: bool, line: str) -> bool:
		"""Завершать цикл после валидного действия."""
		return self._done

	def parseline(self, line: str):
		"""Нормализовать команды: поддержать верхний регистр и кириллицу."""
		cmd_name, arg, parsed_line = super().parseline(line)
		if cmd_name:
			cmd_name = cmd_name.lower()
		return cmd_name, arg, parsed_line

	def _render_screen(self) -> None:
		"""Перерисовать текущий игровой экран."""
		clear_screen()
		player = self.game.current_player
		print(render_header(self.game.turn_number, self.game.deck.remaining()))
		print()
		print(render_monster_zones(self.game.players))
		print()
		print(render_last_action(self.game.last_narrative))
		print(render_turn_intro(player, self.drew))
		if self.overflow:
			from monstromaker.cards import Card as CardCls
			assert isinstance(self.overflow, CardCls)
			print(
				_("  [Переполнение] Сброшена карта: %(name)s")
				% {"name": _(self.overflow.name)}
			)
		print(render_hand(player))
		can_pass = not player.passed_last
		print(render_menu(len(player.hand), can_pass))

	def default(self, line: str) -> None:
		"""Обработать число карты или '?'."""
		stripped = line.strip()
		if stripped.isdigit():
			self._handle_play(int(stripped))
		elif stripped in ("?", "help"):
			self.do_help("")
		else:
			print(_("Неизвестная команда. Введите число или букву."))

	def do_help(self, arg: str) -> None:
		"""Показать подробности выбранной карты."""
		hand = self.game.current_player.hand
		if not hand:
			print(_("В руке нет карт."))
			return
		n = len(hand)
		idx = _pick_number(
			_("Описание какой карты? [1-%(n)d] или [0] отмена\n> ") % {"n": n},
			1, n,
		)
		if idx is None:
			self._render_screen()
			return
		clear_screen()
		print(render_card_detail(hand[idx]))
		_safe_input(_("\n[Enter] — вернуться"))
		self._render_screen()

	def do_п(self, arg: str) -> None:
		"""Пас без розыгрыша карты."""
		player = self.game.current_player
		if player.passed_last:
			print(_("Нельзя пасовать два хода подряд!"))
			return
		self.game.pass_turn()
		self._done = True

	do_p = do_п  # Псевдоним для латинской 'p'

	def do_EOF(self, arg: str) -> bool:  # noqa: N802
		"""Корректно завершить по Ctrl-D."""
		print()
		sys.exit(0)

	def do_q(self, arg: str) -> None:
		"""Выйти из игры (псевдоним Ctrl-D)."""
		sys.exit(0)

	do_выход = do_q

	def _handle_play(self, number: int) -> None:
		"""Сыграть карту по 1-based номеру."""
		player = self.game.current_player
		idx = number - 1
		if not (0 <= idx < len(player.hand)):
			print(_("Нет карты с номером %(n)d.") % {"n": number})
			return

		card = player.hand[idx]
		kwargs = self._gather_params(idx, card)
		if kwargs is None:
			self._render_screen()
			return

		try:
			result = self.game.play_card(idx, **kwargs)
		except (IndexError, ValueError) as exc:
			print(f"  {exc}")
			return

		self.result = result
		print(f"\n  {result.narrative}")

		if result.needs_spy_reveal:
			target = result.needs_spy_reveal
			print()
			print(render_spy_reveal(target))
			_safe_input(_("\n[Enter] — продолжить"))

		self._done = True

	def _gather_params(self, card_idx: int, card: object) -> Optional[dict]:
		"""Собрать дополнительные параметры для эффекта карты."""
		from monstromaker.cards import Card as CardType_check
		assert isinstance(card, CardType_check)

		key = card.key
		player = self.game.current_player

		params: dict = {}

		if key in ("laser", "hunt", "spy"):
			target_idx = self._choose_opponent(
				_("  Выбери игрока:"), exclude=player
			)
			if target_idx is None:
				return None
			params["target_player_idx"] = target_idx

			if key in ("laser", "hunt"):
				target = self.game.players[target_idx]
				if not target.monster:
					print(
						_("  У %(name)s нет облик-карт.")
						% {"name": target.name}
					)
					return None
				card_choice = self._choose_monster_card(
					target, _("  Какую облик-карту?")
				)
				if card_choice is None:
					return None
				params["target_card_idx"] = card_choice

		elif key == "evolve":
			params["discard_idx"] = None

		elif key == "steal_discard":
			discard = self.game.deck.peek_discard()
			if not discard:
				print(_("  Сброс пуст — нечего брать."))
				return None
			clear_screen()
			print(render_discard_pile(discard))
			choice = _pick_number(
				_("  Какую карту взять? [1-%(n)d] или [0] отмена\n> ")
				% {"n": len(discard)},
				1, len(discard),
			)
			if choice is None:
				return None
			params["target_card_idx"] = choice

		return params

	def _choose_opponent(
		self, prompt: str, exclude: Player
	) -> Optional[int]:
		"""Выбрать другого игрока."""
		candidates = [
			(i, p)
			for i, p in enumerate(self.game.players)
			if p is not exclude
		]
		if not candidates:
			print(_("  Нет других игроков."))
			return None

		print(prompt)
		print(render_player_list(self.game.players, self.game.current_idx))

		raw = _pick_number("> ", 1, len(candidates))
		if raw is None:
			return None
		return candidates[raw][0]

	def _choose_monster_card(
		self, target: Player, prompt: str
	) -> Optional[int]:
		"""Выбрать карту из зоны облика."""
		print(prompt)
		print(render_monster_list(target))
		return _pick_number(
			_("[1-%(n)d] или [0] отмена\n> ") % {"n": len(target.monster)},
			1,
			len(target.monster),
		)


def run_game(player_names: List[str]) -> None:
	"""Запустить полную игру."""
	game = Game(player_names)
	game.setup()

	order = " → ".join(p.name for p in game.players)
	print(_("Порядок хода: %(order)s") % {"order": order})
	_safe_input(_("\n[Enter] — начать\n"))

	while not game.game_over:
		cli = TurnCLI(game)
		cli.cmdloop()

		if game.game_over:
			break

		next_player = game.players[
			(game.current_idx + 1) % len(game.players)
		]
		clear_screen()
		print(render_turn_end(game.current_player.name, next_player.name))
		_safe_input(_("\n[Enter] — передать ход\n"))
		game.advance_turn()

	clear_screen()
	assert game.winner is not None
	print(render_end_screen(game.players, game.winner))
	print()
	show_winner_cowsay(game.winner)


def prompt_player_names() -> List[str]:
	"""Запросить количество игроков и их имена."""
	clear_screen()
	print(_("Монстродел"))

	while True:
		raw = _safe_input(_("Сколько игроков? (2-4): ")).strip()
		if raw.isdigit() and 2 <= int(raw) <= 4:
			count = int(raw)
			break
		print(_("Введите число от 2 до 4."))

	names: List[str] = []
	for i in range(1, count + 1):
		while True:
			name = _safe_input(
				_("Имя игрока %(n)d: ") % {"n": i}
			).strip()
			if name:
				names.append(name)
				break
			print(_("Имя не может быть пустым."))

	return names
