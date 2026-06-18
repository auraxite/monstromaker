"""Тесты __main__."""

from unittest.mock import patch

import pytest

from monstromaker.__main__ import main


def test_main() -> None:
	with pytest.raises(SystemExit):
		with patch("sys.argv", ["monstromaker", "--help"]):
			with patch("sys.stdout"):
				main()

	with patch("sys.argv", ["monstromaker", "--players", "Аня", "Боря"]):
		with patch("monstromaker.__main__.run_game") as run:
			main()
			run.assert_called_once_with(["Аня", "Боря"])

	argv = ["monstromaker", "--lang", "en_US", "--players", "А", "Б"]
	with patch("sys.argv", argv):
		with patch("monstromaker.__main__.setup_i18n") as i18n:
			with patch("monstromaker.__main__.run_game"):
				main()
				i18n.assert_called_once_with("en_US")

	for argv in (["monstromaker"], ["monstromaker", "--players", "Аня"]):
		with patch("sys.argv", argv):
			with patch("monstromaker.__main__.prompt_player_names", return_value=["А", "Б"]) as p:
				with patch("monstromaker.__main__.run_game"):
					main()
					p.assert_called_once()
