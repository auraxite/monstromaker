"""Настройка интернационализации для Монстродела.

Пример::

	from monstromaker.i18n import setup_i18n, _

	setup_i18n("en_US")
	print(_("Игра окончена!"))  # На en_US будет "Game over!"
"""

import gettext
import os
from typing import Callable

_LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locales")
_DOMAIN = "monstromaker"

_translator: gettext.NullTranslations = gettext.NullTranslations()


def setup_i18n(locale: str = "ru_RU") -> None:
	"""Настроить активную локаль для всех дальнейших вызовов ``_()``.

	Если каталог перевода для запрошенной локали не найден, возвращает
	исходную строку (на русском).

	Аргументы:
		locale: POSIX-локаль, например ``"ru_RU"`` или ``"en_US"``.
	"""
	global _translator
	try:
		_translator = gettext.translation(
			_DOMAIN,
			localedir=_LOCALE_DIR,
			languages=[locale],
		)
	except FileNotFoundError:
		_translator = gettext.NullTranslations()


def _(message: str) -> str:
	"""Вернуть перевод *message* в активной локали.

	Аргументы:
		message: Исходная строка (по умолчанию на русском).

	Возвращает:
		Переведённую строку или исходную, если перевода нет.
	"""
	return _translator.gettext(message)


def get_translator() -> Callable[[str], str]:
	"""Вернуть текущий вызываемый ``_()`` для других модулей.

	Возвращает:
		Функцию, переводящую строку.
	"""
	return _
