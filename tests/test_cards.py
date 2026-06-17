"""Тесты каталога карт."""

import pytest

from monstromaker.cards import (
	CardType,
	INITIAL_HAND_SIZE,
	MAX_HAND_SIZE,
	WIN_THRESHOLD,
	build_deck,
	get_card_by_key,
	level_name,
)


@pytest.mark.parametrize("key,tag", [("krilya", "[ОБ]"), ("laser", "[ДЕ]")])
def test_display_type(key, tag) -> None:
	assert get_card_by_key(key).display_type() == tag


def test_card_stars_copy_shield() -> None:
	k = get_card_by_key("krilya").copy()
	k.boost = 2
	assert k.total_stars() == 4
	fresh = k.copy()
	assert fresh.boost == 0 and fresh.stars == 2
	assert get_card_by_key("bronya").shield is True
	assert get_card_by_key("krilya").shield is False


def test_build_deck() -> None:
	deck = build_deck()
	assert len(deck) == 32
	assert sum(c.card_type == CardType.OBLIK for c in deck) == 18
	assert sum(c.card_type == CardType.ACTION for c in deck) == 14
	krily = [c for c in deck if c.key == "krilya"]
	krily[0].boost = 99
	assert krily[1].boost == 0


@pytest.mark.parametrize(
	"stars,name",
	[(0, "Пугало"), (4, "Страшилка"), (10, "Кошмарик"), (15, "Ужастик"), (100, "Ужастик")],
)
def test_level_name(stars, name) -> None:
	assert level_name(stars) == name


def test_constants_and_get_card_by_key() -> None:
	assert (INITIAL_HAND_SIZE, MAX_HAND_SIZE, WIN_THRESHOLD) == (4, 6, 15)
	assert get_card_by_key("peklo").name == "Пекло"
	with pytest.raises(KeyError):
		get_card_by_key("nope")
