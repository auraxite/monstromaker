"""Основная логика игры Монстродел.

Здесь живут все эффекты карт, управление ходами и проверка победы.
Класс Game не делает ввод-вывод; интерфейс CLI вызывает его методы и
показывает результаты.
"""

import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

from monstromaker.cards import (
	Card,
	CardType,
	INITIAL_HAND_SIZE,
	MAX_HAND_SIZE,
	WIN_THRESHOLD,
)
from monstromaker.deck import Deck
from monstromaker.i18n import _
from monstromaker.player import Player


@dataclass
class TurnResult:
	"""Описывает, что произошло при розыгрыше карты или пасе.

	Атрибуты:
		narrative: Понятное описание эффекта.
		drew_card: Карта, взятая в начале хода.
		overflow_discard: Карта, сброшенная из-за превышения лимита в 6 карт.
		needs_spy_reveal: Игрок, чью руку показать тайно (Шпион).
		game_over: True, когда условия победы выполнены.
		winner: Победитель, если game_over == True.
	"""

	narrative: str = ""
	drew_card: Optional[Card] = None
	overflow_discard: Optional[Card] = None
	needs_spy_reveal: Optional[Player] = None
	game_over: bool = False
	winner: Optional[Player] = None


class Game:
	"""Управляет полным состоянием одной партии Монстродела.

	Атрибуты:
		players: Упорядоченный список участников.
		deck: Общая колода и сброс.
		current_idx: Индекс игрока, чей сейчас ход.
		turn_number: Сколько ходов уже завершено.
		last_narrative: Текст с описанием последнего действия.
		game_over: True после окончания игры.
		winner: Победитель или None, пока игра идёт.
	"""

	def __init__(self, player_names: List[str]) -> None:
		"""Создать игру для заданных игроков.

		Аргументы:
			player_names: Список из 2–4 имён игроков.

		Исключения:
			ValueError: Если имён меньше 2 или больше 4.
		"""
		if not (2 <= len(player_names) <= 4):
			raise ValueError("Монстроделу нужно 2–4 игрока.")
		self.players: List[Player] = [Player(name=n) for n in player_names]
		self.deck: Deck = Deck()
		self.current_idx: int = 0
		self.turn_number: int = 0
		self.last_narrative: str = ""
		self.game_over: bool = False
		self.winner: Optional[Player] = None

	def setup(self) -> None:
		"""Собрать и перемешать колоду, раздать руки, выбрать первого игрока."""
		self.deck.build_and_shuffle()
		random.shuffle(self.players)
		for player in self.players:
			for _i in range(INITIAL_HAND_SIZE):
				card = self.deck.draw()
				if card:
					player.hand.append(card)
		self.current_idx = 0

	@property
	def current_player(self) -> Player:
		"""Вернуть игрока, чей сейчас ход."""
		return self.players[self.current_idx]

	def begin_turn(self) -> Tuple[Optional[Card], Optional[Card]]:
		"""Взять карту текущему игроку; обработать переполнение руки.

		Взятая карта автоматически добавляется в руку. Если в руке стало
		больше MAX_HAND_SIZE карт, первая карта (индекс 0) сбрасывается.

		Возвращает:
			Кортеж (взятая_карта, сброшенная_из_за_переполнения).
			Любой элемент может быть None.
		"""
		drew = self.deck.draw()
		if drew:
			self.current_player.hand.append(drew)

		overflow: Optional[Card] = None
		if len(self.current_player.hand) > MAX_HAND_SIZE:
			overflow = self.current_player.hand.pop(0)
			self.deck.discard_card(overflow)

		return drew, overflow

	def play_card(
		self,
		card_idx: int,
		target_player_idx: Optional[int] = None,
		target_card_idx: Optional[int] = None,
		discard_idx: Optional[int] = None,
		spy_acknowledge: bool = False,
	) -> TurnResult:
		"""Сыграть карту из руки текущего игрока и применить эффект.

		Разным картам нужны разные доп. параметры:
		- laser, hunt: target_player_idx + target_card_idx
		- evolve: discard_idx (какую карту руки сбросить после добора 2)
		- steal_discard: target_card_idx (индекс в сбросе)
		- spy: target_player_idx (чью руку подсмотреть)
		- roar, exam, peklo: автоматически (без доп. параметров)
		- enhance, карты облика: без доп. параметров

		Аргументы:
			card_idx: Индекс карты в руке (с нуля).
			target_player_idx: Индекс цели-оппонента, если нужен.
			target_card_idx: Индекс конкретной карты для кражи/сброса.
			discard_idx: Индекс карты для сброса из руки (evolve).
			spy_acknowledge: Неиспользуемый флаг; шпион обрабатывается извне.

		Возвращает:
			TurnResult с описанием произошедшего.

		Исключения:
			IndexError: Если card_idx вне диапазона.
		"""
		player = self.current_player
		if not (0 <= card_idx < len(player.hand)):
			raise IndexError(f"Индекс карты {card_idx} вне диапазона.")

		card = player.hand.pop(card_idx)
		result = TurnResult()

		dispatch = {
			CardType.OBLIK: self._play_oblik,
			CardType.ACTION: self._play_action,
		}
		handler = dispatch[card.card_type]
		narrative = handler(
			card,
			target_player_idx=target_player_idx,
			target_card_idx=target_card_idx,
			discard_idx=discard_idx,
			result=result,
		)
		result.narrative = narrative
		self.last_narrative = narrative
		player.passed_last = False

		self._check_win(result)
		return result

	def _play_oblik(
		self,
		card: Card,
		result: TurnResult,
		**kwargs,
	) -> str:
		"""Сыграть карту ОБЛИК: добавить её в зону облика."""
		player = self.current_player
		player.add_to_monster(card)
		if card.boost:
			return _(
				"%(player)s добавил к монстру: %(card)s"
				" (+%(stars)d★, +%(boost)d★ бонус!)"
			) % {
				"player": player.name,
				"card": _(card.name),
				"stars": card.stars,
				"boost": card.boost,
			}
		return _(
			"%(player)s добавил к монстру: %(card)s (+%(stars)d★)"
		) % {
			"player": player.name,
			"card": _(card.name),
			"stars": card.stars,
		}

	def _play_action(self, card: Card, result: TurnResult, **kwargs) -> str:
		"""Сбросить ДЕЙСТВИЕ и вызвать его обработчик эффекта."""
		return self._dispatch_effect(card, result, **kwargs)

	def _dispatch_effect(self, card: Card, result: TurnResult, **kwargs) -> str:
		"""Сбросить карту и вызвать обработчик эффекта по её ключу."""
		self.deck.discard_card(card)
		handler = self._EFFECTS.get(card.key)
		if handler is None:
			return _("%(player)s сыграл %(card)s.") % {
				"player": self.current_player.name,
				"card": _(card.name),
			}
		return handler(self, card, result=result, **kwargs)

	# ── Реализация эффектов карт ───────────────────────────────────────────

	def _steal_from_target_monster(
		self,
		actor: Player,
		target_player_idx: Optional[int],
		target_card_idx: Optional[int],
		no_target_message: str,
		no_card_message: str,
		success_message: str,
	) -> str:
		"""Общая логика для эффектов, крадущих карту из зоны облика цели."""
		if target_player_idx is None or target_card_idx is None:
			return no_target_message.format(actor=actor.name)
		target = self.players[target_player_idx]
		stolen = target.remove_from_monster(target_card_idx)
		if not stolen:
			return no_card_message.format(actor=actor.name, target=target.name)
		actor.add_to_monster(stolen)
		return success_message.format(
			actor=actor.name,
			target=target.name,
			card=_(stolen.name),
			stars=stolen.total_stars(),
		)

	def _effect_laser(
		self,
		card: Card,
		result: TurnResult,
		target_player_idx: Optional[int],
		target_card_idx: Optional[int],
		**kwargs,
	) -> str:
		"""Лазер: цель теряет одну облик-карту."""
		player = self.current_player
		if target_player_idx is None or target_card_idx is None:
			return _("%(player)s сыграл Лазер — но цель не выбрана.") % {
				"player": player.name,
			}
		target = self.players[target_player_idx]
		lost = target.remove_from_monster(target_card_idx)
		if lost:
			self.deck.discard_card(lost)
			return _(
				"%(player)s использовал Лазер!"
				" %(target)s теряет: %(card)s (-%(stars)d★)"
			) % {
				"player": player.name,
				"target": target.name,
				"card": _(lost.name),
				"stars": lost.total_stars(),
			}
		return _(
			"%(player)s использовал Лазер!"
			" У %(target)s нет облик-карт — эффект не сработал."
		) % {"player": player.name, "target": target.name}

	def _effect_hunt(
		self,
		card: Card,
		result: TurnResult,
		target_player_idx: Optional[int],
		target_card_idx: Optional[int],
		**kwargs,
	) -> str:
		"""Вор: украсть одну облик-карту у любого игрока."""
		player = self.current_player
		return self._steal_from_target_monster(
			actor=player,
			target_player_idx=target_player_idx,
			target_card_idx=target_card_idx,
			no_target_message=_("{actor} сыграл Вора — но цель не выбрана."),
			no_card_message=_("{actor} украл у {target}, но у того нет облик-карт."),
			success_message=_("{actor} украл у {target} карту {card}! (+{stars}★)"),
		)

	def _effect_enhance(
		self,
		card: Card,
		result: TurnResult,
		**kwargs,
	) -> str:
		"""Камень усиления: добавить +2★ к следующей сыгранной карте облика."""
		player = self.current_player
		player.pending_boost += 2
		return _(
			"%(player)s активировал Камень усиления — следующий облик +2★!"
		) % {"player": player.name}

	def _effect_evolve(
		self,
		card: Card,
		result: TurnResult,
		discard_idx: Optional[int],
		**kwargs,
	) -> str:
		"""Сделка: взять 2 карты, затем сбросить 1."""
		player = self.current_player
		drawn_names = []
		for _i in range(2):
			c = self.deck.draw()
			if c:
				player.hand.append(c)
				drawn_names.append(c.name)

		discarded_name = "—"
		if discard_idx is not None:
			discarded = player.remove_card_from_hand(discard_idx)
			if discarded:
				self.deck.discard_card(discarded)
				discarded_name = discarded.name

		drawn_str = ", ".join(_(n) for n in drawn_names) if drawn_names else _("нет карт в колоде")
		return _(
			"%(player)s заключил сделку: взял %(drawn)s; сбросил %(discarded)s."
		) % {
			"player": player.name,
			"drawn": drawn_str,
			"discarded": _(discarded_name) if discarded_name != "—" else discarded_name,
		}

	def _effect_roar(
		self,
		card: Card,
		result: TurnResult,
		**kwargs,
	) -> str:
		"""Рёв ужаса: все ДРУГИЕ игроки сбрасывают первую карту руки."""
		player = self.current_player
		losses = []
		for other in self.players:
			if other is player:
				continue
			if other.hand:
				lost = other.hand.pop(0)
				self.deck.discard_card(lost)
				losses.append(
					_("%(name)s сбросил %(card)s")
					% {"name": other.name, "card": _(lost.name)}
				)
			else:
				losses.append(_("%(name)s — карт нет") % {"name": other.name})
		summary = "; ".join(losses) if losses else _("никто не пострадал")
		return _("%(player)s взревел! %(summary)s.") % {
			"player": player.name,
			"summary": summary,
		}

	def _effect_spy(
		self,
		card: Card,
		result: TurnResult,
		target_player_idx: Optional[int],
		**kwargs,
	) -> str:
		"""Шпион: тайно подсмотреть руку выбранного игрока.

		Показ руки делает CLI (по выставленному result.needs_spy_reveal).
		"""
		player = self.current_player
		if target_player_idx is None:
			return _("%(player)s использовал Шпиона — цель не выбрана.") % {
				"player": player.name,
			}
		target = self.players[target_player_idx]
		result.needs_spy_reveal = target
		return _("%(player)s тайно изучает чью-то руку...") % {"player": player.name}

	def _effect_steal_discard(
		self,
		card: Card,
		result: TurnResult,
		target_card_idx: Optional[int],
		**kwargs,
	) -> str:
		"""Жулик: взять любую карту из сброса в руку."""
		player = self.current_player
		if target_card_idx is None:
			return _("%(player)s роется в сбросе — ничего не выбрано.") % {
				"player": player.name,
			}
		stolen = self.deck.take_from_discard(target_card_idx)
		if stolen is None:
			return _("%(player)s хотел взять из сброса — сброс пуст.") % {
				"player": player.name,
			}
		player.hand.append(stolen)
		return _("%(player)s достал из сброса: %(card)s.") % {
			"player": player.name,
			"card": _(stolen.name),
		}

	def _effect_peklo(
		self,
		card: Card,
		result: TurnResult,
		**kwargs,
	) -> str:
		"""Пекло: все без Бронечешуи теряют одну облик-карту."""
		player = self.current_player
		events = []
		for other in self.players:
			if other is player:
				continue
			if other.has_shield():
				other.burn_shield()
				events.append(
					_("%(name)s — БРОНЕЧЕШУЯ! Щит сработал, карта цела.")
					% {"name": other.name}
				)
			elif other.monster:
				lost = other.monster.pop(0)
				self.deck.discard_card(lost)
				events.append(
					_("%(name)s — нет щита! Теряет: %(card)s")
					% {"name": other.name, "card": _(lost.name)}
				)
			else:
				events.append(
					_("%(name)s — нет облик-карт, не пострадал.")
					% {"name": other.name}
				)
		summary = "; ".join(events) if events else _("никто не пострадал")
		return _("%(player)s сыграл Пекло! %(summary)s.") % {
			"player": player.name,
			"summary": summary,
		}

	def _effect_exam(
		self,
		card: Card,
		result: TurnResult,
		**kwargs,
	) -> str:
		"""Экзамен по ОКам: ВСЕ (включая сыгравшего) сбрасывают 1 карту."""
		player = self.current_player
		losses = []
		for p in self.players:
			if p.hand:
				lost = p.hand.pop(0)
				self.deck.discard_card(lost)
				losses.append(
					_("%(name)s сбросил %(card)s")
					% {"name": p.name, "card": _(lost.name)}
				)
			else:
				losses.append(_("%(name)s — карт нет") % {"name": p.name})
		summary = "; ".join(losses)
		return _("%(event)s от %(player)s! %(summary)s.") % {
			"event": _("Экзамен по ОКам"),
			"player": player.name,
			"summary": summary,
		}

	# Сопоставление ключа карты с обработчиком эффекта.
	_EFFECTS = {
		"laser": _effect_laser,
		"hunt": _effect_hunt,
		"enhance": _effect_enhance,
		"evolve": _effect_evolve,
		"roar": _effect_roar,
		"spy": _effect_spy,
		"steal_discard": _effect_steal_discard,
		"peklo": _effect_peklo,
		"exam": _effect_exam,
	}

	def pass_turn(self) -> str:
		"""Текущий игрок пасует, не разыгрывая карту.

		Возвращает:
			Строку с описанием паса.

		Исключения:
			ValueError: Если игрок пасовал и на прошлом ходу.
		"""
		player = self.current_player
		if player.passed_last:
			raise ValueError("Нельзя пасовать два хода подряд!")
		player.passed_last = True
		self.last_narrative = _("%(player)s пасует.") % {"player": player.name}
		return self.last_narrative

	def advance_turn(self) -> None:
		"""Перейти к следующему игроку и увеличить счётчик ходов."""
		self.turn_number += 1
		self.current_idx = (self.current_idx + 1) % len(self.players)

	def _check_win(self, result: TurnResult) -> None:
		"""Заполнить *result* данными о победителе, если победа достигнута.

		Игрок побеждает сразу при достижении WIN_THRESHOLD звёзд либо в конце
		раунда, когда колода пуста. Выигрывает игрок с наибольшим числом
		звёзд; при равенстве — по количеству облик-карт.

		Аргументы:
			result: TurnResult, который обновляется game_over и winner.
		"""
		for player in self.players:
			if player.scariness() >= WIN_THRESHOLD:
				result.game_over = True
				result.winner = player
				self.game_over = True
				self.winner = player
				return
		if self.deck.is_empty():
			result.game_over = True
			winner = max(
				self.players,
				key=lambda p: (p.scariness(), len(p.monster)),
			)
			result.winner = winner
			self.game_over = True
			self.winner = winner
