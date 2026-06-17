"""Управление состоянием игрока для Монстродела."""

from dataclasses import dataclass, field
from typing import List, Optional

from monstromaker.cards import Card, level_name


@dataclass
class Player:
	"""Хранит состояние одного участника партии.

	Атрибуты:
		name: Имя игрока.
		hand: Карты в руке (скрыты от других).
		monster: Карты ОБЛИК в зоне облика (видны всем).
		passed_last: True, если игрок пасовал на прошлом ходу.
		pending_boost: Доп. звёзды от Камня усиления для следующей карты ОБЛИК.
	"""

	name: str
	hand: List[Card] = field(default_factory=list)
	monster: List[Card] = field(default_factory=list)
	passed_last: bool = False
	pending_boost: int = 0

	def scariness(self) -> int:
		"""Вернуть суммарную «страшность» всех карт зоны облика.

		Возвращает:
			Сумму звёзд по всем картам зоны облика.
		"""
		return sum(c.total_stars() for c in self.monster)

	def level_name(self) -> str:
		"""Вернуть прозвище уровня страшности.

		Возвращает:
			Строку вроде ``"Кошмарик"`` или ``"Ужастик"``.
		"""
		return level_name(self.scariness())

	def add_to_monster(self, card: Card) -> None:
		"""Положить карту ОБЛИК в зону облика.

		Применяет отложенный бонус от Камня усиления и сбрасывает его.

		Аргументы:
			card: Карта ОБЛИК для добавления.
		"""
		if self.pending_boost > 0:
			card.boost = self.pending_boost
			self.pending_boost = 0
		self.monster.append(card)

	def remove_from_monster(self, idx: int) -> Optional[Card]:
		"""Снять и вернуть карту ОБЛИК из зоны облика по индексу.

		Аргументы:
			idx: Индекс в списке зоны облика (с нуля).

		Возвращает:
			Снятую карту или None, если индекс вне диапазона.
		"""
		if 0 <= idx < len(self.monster):
			return self.monster.pop(idx)
		return None

	def remove_card_from_hand(self, idx: int) -> Optional[Card]:
		"""Снять и вернуть карту из руки по индексу.

		Аргументы:
			idx: Индекс в руке (с нуля).

		Возвращает:
			Снятую карту или None, если индекс вне диапазона.
		"""
		if 0 <= idx < len(self.hand):
			return self.hand.pop(idx)
		return None

	def has_shield(self) -> bool:
		"""Вернуть True, если у игрока есть активная Бронечешуя.

		Возвращает:
			Признак наличия карты-щита.
		"""
		return any(c.shield for c in self.monster)

	def burn_shield(self) -> None:
		"""Снять защиту одной Бронечешуи (карта остаётся, щит гаснет)."""
		for card in self.monster:
			if card.shield:
				card.shield = False
				return

	def __str__(self) -> str:
		"""Вернуть короткое описание состояния игрока.

		Возвращает:
			Строку вроде ``"Валя (8★ — Кошмарик)"``.
		"""
		return f"{self.name} ({self.scariness()}★ — {self.level_name()})"
