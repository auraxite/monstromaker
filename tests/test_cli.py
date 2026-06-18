"""Тесты CLI."""

from unittest.mock import patch

import pytest

from monstromaker.cards import get_card_by_key
from monstromaker.cli import TurnCLI, _pick_number, _safe_input, prompt_player_names
from tests.conftest import make_game


def test_safe_input() -> None:
	with patch("builtins.input", return_value="  x  "):
		assert _safe_input("> ") == "x"
	with patch("builtins.input", side_effect=EOFError):
		with pytest.raises(SystemExit):
			_safe_input("> ")


@pytest.mark.parametrize(
	"answer,expected",
	[("2", 1), ("0", None), ("н", None), ("1", 0), ("5", 4)],
)
def test_pick_number(answer, expected) -> None:
	with patch("builtins.input", return_value=answer):
		assert _pick_number("> ", 1, 5) == expected


def test_pick_number_retries() -> None:
	with patch("builtins.input", side_effect=["9", "1"]):
		with patch("builtins.print"):
			assert _pick_number("> ", 1, 3) == 0


def test_prompt_player_names() -> None:
	inputs = iter(["0", "2", "", "Аня", "Боря"])
	with patch("builtins.input", side_effect=inputs):
		with patch("monstromaker.cli.clear_screen"), patch("builtins.print"):
			assert prompt_player_names() == ["Аня", "Боря"]


def test_turn_cli_helpers() -> None:
	game = make_game(["Аня", "Боря"])
	cli = TurnCLI(game)
	expected = game.players.index(game.players[1])
	with patch("monstromaker.cli._pick_number", return_value=0):
		with patch("monstromaker.cli.render_player_list", return_value=""), patch("builtins.print"):
			assert cli._choose_opponent("?", exclude=game.current_player) == expected
	with patch("monstromaker.cli._pick_number", return_value=None):
		with patch("monstromaker.cli.render_player_list", return_value=""), patch("builtins.print"):
			assert cli._choose_opponent("?", exclude=game.current_player) is None

	target = game.players[1]
	target.monster.append(get_card_by_key("krilya").copy())
	with patch("monstromaker.cli._pick_number", return_value=0), patch("builtins.print"):
		assert cli._choose_monster_card(target, "?") == 0

	assert cli._gather_params(0, get_card_by_key("evolve").copy()) == {"discard_idx": None}
	with patch.object(game.deck, "peek_discard", return_value=[]), patch("builtins.print"):
		assert cli._gather_params(0, get_card_by_key("steal_discard").copy()) is None
