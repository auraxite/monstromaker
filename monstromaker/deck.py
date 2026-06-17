"""Управление колодой и сбросом для Монстродела."""

import random
from typing import List, Optional

from monstromaker.cards import Card, build_deck


class Deck:
	"""Управляет колодой добора и стопкой сброса.

	Атрибуты:
		cards: Колода добора; последний элемент — верхняя карта.
		discard: Сброс; последний элемент — недавно сброшенная карта.
	"""

	def __init__(self) -> None:
		"""Создать пустую колоду и сброс."""
		self.cards: List[Card] = []
		self.discard: List[Card] = []

	def build_and_shuffle(self) -> None:
		"""Заполнить колоду всеми 40 картами и перемешать."""
		self.cards = build_deck()
		random.shuffle(self.cards)

	def draw(self) -> Optional[Card]:
		"""Снять и вернуть верхнюю карту колоды.

		Возвращает:
			Снятую карту или None, если колода пуста.
		"""
		if not self.cards:
			return None
		return self.cards.pop()

	def discard_card(self, card: Card) -> None:
		"""Положить карту в сброс.

		Аргументы:
			card: Карта для сброса.
		"""
		self.discard.append(card)

	def peek_discard(self) -> List[Card]:
		"""Вернуть весь сброс, не меняя его.

		Возвращает:
			Список сброшенных карт (старые первыми).
		"""
		return list(self.discard)

	def take_from_discard(self, idx: int) -> Optional[Card]:
		"""Снять и вернуть карту из сброса по индексу.

		Аргументы:
			idx: Индекс в стопке сброса (с нуля).

		Возвращает:
			Взятую карту или None, если индекс вне диапазона.
		"""
		if 0 <= idx < len(self.discard):
			return self.discard.pop(idx)
		return None

	def remaining(self) -> int:
		"""Вернуть число оставшихся в колоде карт.

		Возвращает:
			Количество карт для добора.
		"""
		return len(self.cards)

	def is_empty(self) -> bool:
		"""Вернуть True, если колода добора пуста.

		Возвращает:
			Признак пустой колоды.
		"""
		return len(self.cards) == 0
