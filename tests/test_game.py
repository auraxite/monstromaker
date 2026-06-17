"""Тесты Game."""

import pytest

from tests.conftest import card, make_game, play


def test_setup() -> None:
	g = make_game(["А", "Б"])
	assert len(g.players) == 2 and all(len(p.hand) == 4 for p in g.players)
	assert make_game(["А", "Б", "В", "Г"]).deck.remaining() == 16
	with pytest.raises(ValueError):
		make_game(["Solo"], setup=False)
	with pytest.raises(ValueError):
		make_game(["A", "B", "C", "D", "E"], setup=False)
	firsts = {make_game(["А", "Б", "В", "Г"]).current_player.name for _ in range(30)}
	assert len(firsts) > 1


def test_turn_flow() -> None:
	g = make_game(["А", "Б"])
	p = g.current_player
	n = len(p.hand)
	drew, overflow = g.begin_turn()
	assert len(p.hand) == n + 1 and overflow is None
	for _ in range(6 - len(p.hand)):
		if c := g.deck.draw():
			p.hand.append(c)
	_, overflow = g.begin_turn()
	assert overflow is not None and len(p.hand) == 6
	g.pass_turn()
	assert p.passed_last
	with pytest.raises(ValueError):
		g.pass_turn()
	g.advance_turn()
	assert g.turn_number == 1


def test_oblik_and_win() -> None:
	g = make_game(["А", "Б"])
	p = g.current_player
	c = card("krilya")
	p.hand = [c]
	g.play_card(0)
	assert c in p.monster
	p.pending_boost = 2
	p.hand = [card("krilya")]
	g.play_card(0)
	assert p.monster[-1].boost == 2
	for _ in range(4):
		p.monster.append(card("roga"))
	p.monster.append(card("krilya"))
	p.hand = [card("hvost")]
	r = g.play_card(0)
	assert r.game_over and r.winner is p


def test_effects_on_opponents() -> None:
	g = make_game(["А", "Б", "В"])
	target = g.players[1]
	target.monster.append(card("krilya"))
	play(g, "laser", target_player_idx=1, target_card_idx=0)
	assert len(target.monster) == 0
	assert play(g, "laser").narrative
	target.monster.append(card("krilya"))
	play(g, "hunt", target_player_idx=1, target_card_idx=0)
	assert len(target.monster) == 0 and len(g.players[0].monster) == 1
	assert play(g, "hunt").narrative


def test_peklo_roar_exam() -> None:
	g = make_game(["А", "Б", "В"])
	g.players[1].monster.append(card("krilya"))
	play(g, "peklo", actor=0)
	assert len(g.players[1].monster) == 0
	g.players[1].monster = [card("bronya")]
	play(g, "peklo", actor=0)
	assert g.players[1].monster[0].shield is False
	g.players[1].hand = [card("krilya")]
	g.players[2].hand = [card("roga")]
	r = play(g, "roar", actor=0)
	assert len(g.players[1].hand) == len(g.players[2].hand) == 0
	g.players[1].hand.clear()
	r = play(g, "roar", actor=0)
	assert "нет" in r.narrative
	g.players[0].hand = [card("exam"), card("krilya")]
	g.players[1].hand = [card("roga")]
	g.current_idx = 0
	g.play_card(0)
	assert len(g.players[0].hand) == len(g.players[1].hand) == 0


def test_enhance_spy_steal_evolve() -> None:
	g = make_game(["А", "Б"])
	play(g, "enhance")
	assert g.players[0].pending_boost == 2
	assert "+2★" in play(g, "enhance").narrative
	r = play(g, "spy", target_player_idx=1)
	assert r.needs_spy_reveal is g.players[1]
	assert play(g, "spy").narrative
	g2 = make_game(["А", "Б"])
	discarded = card("krilya")
	g2.deck.discard = [discarded]
	play(g2, "steal_discard", target_card_idx=0)
	assert discarded in g2.players[0].hand
	assert play(g2, "steal_discard", target_card_idx=0).narrative
	assert play(g2, "steal_discard").narrative
	p = g2.players[0]
	p.hand = [card("evolve"), card("krilya")]
	before = len(g2.deck.discard)
	g2.play_card(0, discard_idx=0)
	assert len(g2.deck.discard) > before


def test_win_on_empty_deck_and_errors() -> None:
	g = make_game(["А", "Б"])
	g.players[1].monster.append(card("roga"))
	while not g.deck.is_empty():
		g.deck.draw()
	g.players[0].hand = [card("hvost")]
	r = g.play_card(0)
	assert r.game_over and r.winner is g.players[1]
	g.players[0].hand.clear()
	with pytest.raises(IndexError):
		g.play_card(99)
	g.players[1].hand.clear()
	r = play(g, "exam", actor=0)
	assert r.narrative
	g.players[1].monster.clear()
	g.players[0].hand = [card("peklo")]
	r = play(g, "peklo", actor=0)
	assert "не пострадал" in r.narrative
