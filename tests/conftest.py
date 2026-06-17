"""Общие фикстуры и хелперы для тестов."""

import pytest

from monstromaker.cards import get_card_by_key
from monstromaker.deck import Deck
from monstromaker.game import Game
from monstromaker.player import Player


def card(key: str):
	return get_card_by_key(key).copy()


def player(name: str = "Тест") -> Player:
	return Player(name=name)


def make_game(names=("А", "Б"), setup: bool = True) -> Game:
	g = Game(list(names))
	if setup:
		g.setup()
	return g


def play(g: Game, key: str, actor: int = 0, **kwargs):
	g.current_idx = actor
	p = g.players[actor]
	p.hand.clear()
	p.hand.append(card(key))
	return g.play_card(0, **kwargs)


@pytest.fixture
def deck() -> Deck:
	d = Deck()
	d.build_and_shuffle()
	return d
