"""Тесты display."""

from unittest.mock import patch

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
from tests.conftest import card, player


def test_render_header_and_turn() -> None:
	assert "МОНСТРОДЕЛ" in render_header(0, 26) and "Номер хода: 1" in render_header(0, 26)
	p = player("Вася")
	assert "Вася" in render_turn_intro(p, card("krilya"))
	assert "пуста" in render_turn_intro(p, None).lower()
	assert "событие" in render_last_action("событие")
	assert "Боря" in render_turn_end("Аня", "Боря")


def test_render_monster_zones_and_lists() -> None:
	p = player("Петя")
	p.monster.append(card("krilya"))
	assert "Крылья" in render_monster_zones([p])
	assert "нет" in render_monster_zones([player("Коля")])
	players = [player("Аня"), player("Боря"), player("Вася")]
	assert "Аня" in render_player_list(players) and "Боря" in render_player_list(players)
	assert "Аня" not in render_player_list(players, exclude_idx=0)
	assert "нет" in render_player_list([player("Аня")], exclude_idx=0)
	assert "Крылья" in render_monster_list(p)
	assert "нет" in render_monster_list(player("Маша"))


def test_render_hand_menu_discard() -> None:
	p = player("Маша")
	p.hand.append(card("krilya"))
	assert "Крылья" in render_hand(p) and "пуста" in render_hand(player("X"))
	p.hand.append(card("laser"))
	assert "выбери" in render_hand(p).lower()
	assert "4" in render_menu(4, True) and "п" in render_menu(2, True)
	assert "нет карт" in render_menu(0, True)
	assert "пуст" in render_discard_pile([])
	assert "Лазер" in render_discard_pile([card("laser")])


def test_render_card_detail() -> None:
	assert "ОБЛИК" in render_card_detail(card("krilya"))
	assert "ДЕЙСТВИЕ" in render_card_detail(card("laser"))
	assert "ДЕЙСТВИЕ" in render_card_detail(card("peklo"))
	assert "щит" in render_card_detail(card("bronya")).lower()


def test_render_end_and_spy() -> None:
	p1, p2 = player("Петя"), player("Маша")
	p1.monster.append(card("roga"))
	assert "Петя" in render_end_screen([p1, p2], p1) and "ПОБЕДИЛ" in render_end_screen([p1, p2], p1)
	target = player("Цель")
	target.hand.append(card("krilya"))
	assert "Крылья" in render_spy_reveal(target) and "+2★" in render_spy_reveal(target)
	assert "пуста" in render_spy_reveal(player("X"))


def test_clear_screen_and_winner() -> None:
	with patch("monstromaker.display.os.system") as mock_sys, \
			patch("monstromaker.display.sys.stdin") as mock_stdin:
		mock_stdin.isatty.return_value = True
		clear_screen()
		mock_sys.assert_called_once_with("clear")
	p = player("Победитель")
	p.monster.append(card("roga"))
	with patch("builtins.print") as mock_print:
		show_winner_cowsay(p)
	output = "\n".join(str(c.args[0]) for c in mock_print.call_args_list)
	assert "ПОБЕДИТЕЛЬ: Победитель" in output and "Страшность:" in output
