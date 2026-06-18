"""Тесты i18n."""

from monstromaker.i18n import _, get_translator, setup_i18n

_MSG = "Неизвестная команда. Введите число или букву."


def test_i18n_locales() -> None:
	setup_i18n("ru_RU")
	assert _("Привет!") == "Привет!"
	assert _(_MSG) == _MSG

	setup_i18n("en_US")
	assert _(_MSG) == "Unknown command. Enter a number or a letter."
	assert _("\n[Enter] — начать\n") == "\n[Enter] - start\n"
	assert _("Монстродел") == "Monstermaker"

	setup_i18n("zz_ZZ")
	assert _("Привет!") == "Привет!"

	assert callable(_) and callable(get_translator())
	setup_i18n("ru_RU")
	assert get_translator()("тест") == _("тест")
