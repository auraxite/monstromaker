"""Простой вывод в терминал для Монстродела."""

import os
import sys
from typing import Optional

from monstromaker.cards import Card, CardType
from monstromaker.i18n import _
from monstromaker.player import Player


def clear_screen() -> None:
	"""Очистить экран терминала (пропустить, если stdin — не TTY)."""
	if sys.stdin.isatty():
		os.system("clear")


def render_header(turn: int, deck_remaining: int) -> str:
	"""Вернуть однострочный заголовок."""
	return _(
		"МОНСТРОДЕЛ | Номер хода: %(turn)d | Колода: %(deck)d"
	) % {"turn": turn + 1, "deck": deck_remaining}


def _monster_face(stars: int) -> list[str]:
	"""Вернуть простую ASCII-мордочку монстра по уровню страшности."""
	if stars <= 0:
		return [
			"  ____  ",
			" (    ) ",
			" ( .. ) ",
			" (____) ",
		]
	if stars <= 3:
		return [
			"  ^__^  ",
			" ( o o ) ",
			" (  --  ) ",
			"  \\____/ ",
		]
	if stars <= 6:
		return [
			" \\(^^)/ ",
			" ( O O ) ",
			" ( vvv ) ",
			"  \\__/  ",
		]
	if stars <= 10:
		return [
			" \\(##)/ ",
			" ( @ @ ) ",
			" }( WW )}",
			"  /||\\  ",
		]
	if stars <= 14:
		return [
			" >|##|< ",
			" ( X X ) ",
			"}((vWv))}",
			" /_||_\\ ",
		]
	return [
		"\\>|####|</",
		"((  @@  ))",
		"}(( WWWW ))}",
		" //_||_\\\\ ",
	]


def render_monster_zones(players: list[Player]) -> str:
	"""Вернуть зоны облика с ASCII-мордочкой на каждого игрока."""
	blocks: list[str] = []
	for player in players:
		stars = player.scariness()
		face = _monster_face(stars)
		if player.monster:
			cards_str = ", ".join(
				f"{_(c.name)}(+{c.total_stars()}★)" for c in player.monster
			)
		else:
			cards_str = _("(нет облик-карт)")
		block = list(face)
		block.append(
			_("%(name)s: %(stars)d★ «%(level)s»")
			% {"name": player.name, "stars": stars, "level": player.level_name()}
		)
		block.append(cards_str)
		blocks.append("\n".join(block))
	return "\n\n".join(blocks)


def render_last_action(narrative: str) -> str:
	"""Вернуть строку последнего действия."""
	return _("Последнее: %(text)s") % {"text": narrative}


def render_turn_intro(player: Player, drew: Optional[Card]) -> str:
	"""Вернуть текст начала хода."""
	stars = player.scariness()
	header = _("Ход: %(name)s (%(stars)d★)") % {
		"name": player.name,
		"stars": stars,
	}
	if drew:
		draw_line = _("Добор: %(name)s %(type)s") % {
			"name": _(drew.name),
			"type": drew.display_type(),
		}
	else:
		draw_line = _("Колода пуста — карта не взята")
	return f"{header}\n{draw_line}"


def render_hand(player: Player) -> str:
	"""Вернуть список карт руки."""
	lines = [_("ТВОИ КАРТЫ:")]
	if not player.hand:
		lines.append(_("(рука пуста)"))
		return "\n".join(lines)

	name_width = max(len(_(card.name)) for card in player.hand)
	for i, card in enumerate(player.hand, 1):
		if card.card_type == CardType.OBLIK:
			detail = f"+{card.stars}★"
		else:
			detail = _(card.description)
		lines.append(
			f"{i}. {_(card.name):<{name_width}} {card.display_type()} {detail}"
		)
	return "\n".join(lines)


def render_menu(hand_size: int, can_pass: bool) -> str:
	"""Вернуть компактное меню команд."""
	if hand_size:
		play_range = f"[1–{hand_size}]"
	else:
		play_range = _("[нет карт]")
	pass_hint = _("[п] Пас") if can_pass else _("[п] Пас ✗")
	return _("%(play)s Сыграть | [?] Описание | %(pass)s | [q] Выход") % {
		"play": play_range,
		"pass": pass_hint,
	}


def render_card_detail(card: Card) -> str:
	"""Вернуть упрощённое описание карты."""
	if card.card_type == CardType.OBLIK:
		type_label = _("ОБЛИК")
	else:
		type_label = _("ДЕЙСТВИЕ")
	lines = [f"{_(card.name).upper()} [{type_label}]"]
	if card.card_type == CardType.OBLIK:
		lines.append(_("Страшность: +%(stars)d★") % {"stars": card.stars})
		if card.shield:
			lines.append(_("Щит: блокирует Пекло"))
	else:
		lines.append(_(card.description))
	return "\n".join(lines)


def render_turn_end(current_name: str, next_name: str) -> str:
	"""Вернуть текст передачи хода."""
	return _(
		"Ход завершён: %(current)s. Далее ходит: %(next)s."
	) % {"current": current_name, "next": next_name}


def render_discard_pile(discard: list[Card]) -> str:
	"""Вернуть список сброса."""
	if not discard:
		return _("Сброс пуст.")
	lines = [_("СБРОС:")]
	for i, card in enumerate(discard, 1):
		lines.append(f"{i}. {_(card.name)} {card.display_type()}")
	return "\n".join(lines)


def render_end_screen(players: list[Player], winner: Player) -> str:
	"""Вернуть компактный итог окончания игры."""
	lines = [_("ИГРА ОКОНЧЕНА!"), _("Итог:")]
	sorted_players = sorted(
		players, key=lambda p: (p.scariness(), len(p.monster)), reverse=True
	)
	for i, player in enumerate(sorted_players, 1):
		win_tag = _(" ПОБЕДИЛ(А)!") if player is winner else ""
		lines.append(
			_("%(n)d. %(name)s — %(stars)d★ «%(level)s»%(win)s")
			% {
				"n": i,
				"name": player.name,
				"stars": player.scariness(),
				"level": player.level_name(),
				"win": win_tag,
			}
		)
	return "\n".join(lines)


def show_winner_cowsay(winner: Player) -> None:
	"""Показать победителя с ASCII-мордочкой монстра."""
	face = "\n".join(_monster_face(winner.scariness()))
	monster_names = ", ".join(_(c.name) for c in winner.monster) or _("(нет обликов)")
	print(face)
	print(_("ПОБЕДИТЕЛЬ: %(name)s") % {"name": winner.name})
	print(_("Страшность: %(stars)d★") % {"stars": winner.scariness()})
	print(_("Облик: %(cards)s") % {"cards": monster_names})


def render_spy_reveal(target: Player) -> str:
	"""Вернуть руку цели для эффекта шпиона."""
	lines = [_("[ШПИОН] Рука %(name)s:") % {"name": target.name}]
	if not target.hand:
		lines.append(_("(рука пуста)"))
		return "\n".join(lines)

	name_width = max(len(_(card.name)) for card in target.hand)
	for card in target.hand:
		if card.card_type == CardType.OBLIK:
			detail = f"+{card.stars}★"
		else:
			detail = _(card.description)
		lines.append(
			f"- {_(card.name):<{name_width}} {card.display_type()} {detail}"
		)
	return "\n".join(lines)


def render_player_list(
	players: list[Player],
	exclude_idx: Optional[int] = None,
) -> str:
	"""Вернуть нумерованный список игроков для выбора цели."""
	lines = []
	display_num = 1
	for i, player in enumerate(players):
		if i == exclude_idx:
			continue
		lines.append(
			_("%(n)d. %(name)s (%(stars)d★, %(cards)d карт)")
			% {
				"n": display_num,
				"name": player.name,
				"stars": player.scariness(),
				"cards": len(player.monster),
			}
		)
		display_num += 1
	return "\n".join(lines) if lines else _("(нет других игроков)")


def render_monster_list(player: Player) -> str:
	"""Вернуть карты облика выбранного игрока."""
	if not player.monster:
		return _("У %(name)s нет облик-карт.") % {"name": player.name}
	lines = []
	for i, card in enumerate(player.monster, 1):
		lines.append(
			_("%(n)d. %(name)s (+%(stars)d★)")
			% {"n": i, "name": _(card.name), "stars": card.total_stars()}
		)
	return "\n".join(lines)
