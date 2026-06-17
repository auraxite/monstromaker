"""Тесты игрока."""

from monstromaker.cards import get_card_by_key
from monstromaker.player import Player


def _card(key: str):
	return get_card_by_key(key).copy()


def _player(name: str = "Тест") -> Player:
	return Player(name=name)


def test_scariness_and_level() -> None:
	p = _player()
	assert p.scariness() == 0 and p.level_name() == "Пугало"
	p.monster.extend(_card(k) for k in ("krilya", "roga"))
	assert p.scariness() == 5
	boosted = _card("krilya")
	boosted.boost = 3
	p.monster.append(boosted)
	assert p.scariness() == 10


def test_monster_and_hand_ops() -> None:
	p = _player()
	c = _card("krilya")
	p.pending_boost = 2
	p.add_to_monster(c)
	assert c.boost == 2 and p.pending_boost == 0
	assert p.remove_from_monster(0) is c and p.remove_from_monster(5) is None
	p.hand.extend([_card("krilya"), _card("roga")])
	assert p.remove_card_from_hand(0).key == "krilya"
	assert p.remove_card_from_hand(99) is None


def test_shield_and_str() -> None:
	p = _player()
	p.monster.append(_card("bronya"))
	assert p.has_shield()
	p.burn_shield()
	assert not p.has_shield() and len(p.monster) == 1
	assert "★" in str(Player(name="Маша"))
