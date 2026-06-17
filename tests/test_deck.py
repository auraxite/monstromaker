"""Тесты колоды."""

from monstromaker.deck import Deck


def _deck() -> Deck:
	d = Deck()
	d.build_and_shuffle()
	return d


def test_build_and_draw() -> None:
	deck = _deck()
	assert deck.remaining() == 32 and deck.discard == [] and not deck.is_empty()
	drawn = deck.draw()
	assert drawn is not None and deck.remaining() == 31
	for _ in range(31):
		deck.draw()
	assert deck.is_empty() and deck.draw() is None


def test_discard_ops() -> None:
	deck = _deck()
	c = deck.draw()
	deck.discard_card(c)
	assert len(deck.peek_discard()) == len(deck.discard) == 1
	assert deck.take_from_discard(0) is c
	assert deck.take_from_discard(99) is None


def test_fresh_deck_empty() -> None:
	d = Deck()
	assert d.remaining() == 0 and d.is_empty()
