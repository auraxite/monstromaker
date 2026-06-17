"""Оркестрация сборки через doit для Монстродела.

Запустить все задачи:  doit
Запустить одну задачу:  doit <задача>

Граф зависимостей задач:
  style ──┐
  pot ────┼──> po ──> mo ──> test ──> sphinx ──> wheel
		   │                      └──────> html (xdg-open)
		   └──────────────────────────────────> sdist
"""

import glob

DOIT_CONFIG = {"default_tasks": ["wheel"]}

_SOURCES = glob.glob("monstromaker/**/*.py", recursive=True)
_POT = "monstromaker/locales/monstromaker.pot"
_PO_RU = "monstromaker/locales/ru_RU/LC_MESSAGES/monstromaker.po"
_PO_EN = "monstromaker/locales/en_US/LC_MESSAGES/monstromaker.po"
_MO_RU = "monstromaker/locales/ru_RU/LC_MESSAGES/monstromaker.mo"
_MO_EN = "monstromaker/locales/en_US/LC_MESSAGES/monstromaker.mo"
_DOC_INDEX = "doc/_build/html/index.html"


def task_style():
	"""Проверить стиль кода через flake8 и pydocstyle."""
	return {
		"actions": [
			"flake8 monstromaker/ tests/",
			"pydocstyle monstromaker/",
		],
		"file_dep": _SOURCES,
		"verbosity": 2,
	}


def task_pot():
	"""Извлечь переводимые строки в шаблон .pot."""
	return {
		"actions": [
			f"pybabel extract -o {_POT} monstromaker/",
		],
		"file_dep": _SOURCES,
		"targets": [_POT],
		"verbosity": 1,
	}


def task_po():
	"""Обновить .po-файлы из шаблона .pot (msgstr не затирается)."""
	return {
		"actions": [
			f"pybabel update -i {_POT} -d monstromaker/locales -D monstromaker",
		],
		"file_dep": [_POT],
		"targets": [_PO_RU, _PO_EN],
		"verbosity": 1,
	}


def task_mo():
	"""Скомпилировать .po-переводы в бинарный формат .mo."""
	return {
		"actions": [
			"pybabel compile -d monstromaker/locales -D monstromaker",
		],
		"file_dep": [_PO_RU, _PO_EN],
		"targets": [_MO_RU, _MO_EN],
		"verbosity": 1,
	}


def task_test():
	"""Запустить тесты."""
	return {
		"task_dep": ["style", "mo"],
		"actions": ["pytest tests/"],
		"verbosity": 2,
	}


def task_sphinx():
	"""Собрать HTML-документацию Sphinx."""
	return {
		"task_dep": ["test"],
		"actions": ["sphinx-build -M html doc doc/_build"],
		"targets": [_DOC_INDEX],
		"verbosity": 1,
	}


def task_html():
	"""Собрать документацию и открыть в браузере (xdg-open)."""
	return {
		"task_dep": ["sphinx"],
		"actions": [f"xdg-open {_DOC_INDEX}"],
		"verbosity": 1,
	}


def task_wheel():
	"""Собрать пакет-колесо (wheel)."""
	return {
		"task_dep": ["sphinx", "mo"],
		"actions": [
			"rm -rf build",
			"python3 -m build -w",
		],
		"verbosity": 1,
	}


def task_sdist():
	"""Собрать дистрибутив исходников (sdist)."""
	return {
		"task_dep": ["sphinx", "mo"],
		"actions": [
			"rm -rf build",
			"python3 -m build -s",
		],
		"verbosity": 1,
	}


def task_erase():
	"""Удалить созданные артефакты (.mo, dist/, build/, doc/_build/)."""
	return {
		"actions": [
			f"rm -f {_MO_RU} {_MO_EN} {_POT}",
			"rm -rf dist/ build/ doc/_build/ *.egg-info",
		],
		"verbosity": 1,
	}
