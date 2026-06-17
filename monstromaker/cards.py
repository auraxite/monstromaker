"""Каталог всех 32 карт игры Монстродел."""

from dataclasses import dataclass
from enum import Enum
from typing import List


class CardType(Enum):
	"""Тип игровой карты."""

	OBLIK = "ОБ"
	ACTION = "ДЕ"


@dataclass
class Card:
	"""Одна игровая карта.

	Атрибуты:
		key: Уникальный ключ для выбора эффекта.
		card_type: Категория карты (OBLIK или ACTION).
		name: Отображаемое имя на русском.
		description: Однострочное описание в списке руки.
		stars: Очки страшности (только для карт ОБЛИК).
		shield: True, если карта однократно блокирует Пекло.
		ascii_art: Небольшой ASCII-рисунок в подробностях карты.
		count: Сколько копий карты есть в колоде.
		boost: Доп. звёзды от эффекта Камня усиления.
	"""

	key: str
	card_type: CardType
	name: str
	description: str
	stars: int = 0
	shield: bool = False
	ascii_art: str = ""
	count: int = 1
	boost: int = 0

	def display_type(self) -> str:
		"""Вернуть сокращение типа в скобках, например [ОБ]."""
		if self.card_type == CardType.OBLIK:
			return "[ОБ]"
		return "[ДЕ]"

	def total_stars(self) -> int:
		"""Вернуть звёзды плюс активный бонус от Камня усиления."""
		return self.stars + self.boost

	def copy(self) -> "Card":
		"""Вернуть свежую копию карты без бонуса."""
		return Card(
			key=self.key,
			card_type=self.card_type,
			name=self.name,
			description=self.description,
			stars=self.stars,
			shield=self.shield,
			ascii_art=self.ascii_art,
			count=self.count,
			boost=0,
		)


_CATALOG: List[Card] = [
	# ── Карты ОБЛИК ───────────────────────────────────────────────────────────
	Card(
		key="krilya",
		card_type=CardType.OBLIK,
		name="Крылья",
		description="+2★ навсегда",
		stars=2,
		count=2,
	),
	Card(
		key="roga",
		card_type=CardType.OBLIK,
		name="Рога",
		description="+3★ навсегда",
		stars=3,
		count=2,
	),
	Card(
		key="hvost",
		card_type=CardType.OBLIK,
		name="Хвост",
		description="+1★ навсегда",
		stars=1,
		count=2,
	),
	Card(
		key="kogti",
		card_type=CardType.OBLIK,
		name="Ядовитые когти",
		description="+2★ навсегда",
		stars=2,
		count=2,
	),
	Card(
		key="bronya",
		card_type=CardType.OBLIK,
		name="Бронечешуя",
		description="+2★, щит от Пекла",
		stars=2,
		shield=True,
		count=2,
	),
	Card(
		key="glaza",
		card_type=CardType.OBLIK,
		name="Три глаза",
		description="+2★ навсегда",
		stars=2,
		count=2,
	),
	Card(
		key="shchupalca",
		card_type=CardType.OBLIK,
		name="Щупальца",
		description="+3★ навсегда",
		stars=3,
		count=2,
	),
	Card(
		key="klyki",
		card_type=CardType.OBLIK,
		name="Клыки",
		description="+2★ навсегда",
		stars=2,
		count=2,
	),
	Card(
		key="zhalo",
		card_type=CardType.OBLIK,
		name="Жало",
		description="+1★ навсегда",
		stars=1,
		count=2,
	),
	# ── ДЕЙСТВИЕ ──────────────────────────────────────────────────────────────
	Card(
		key="laser",
		card_type=CardType.ACTION,
		name="Лазер",
		description="выбери игрока: он теряет 1 облик",
		ascii_art="  O===>>~~~*\n  O===>>~~~*",
		count=2,
	),
	Card(
		key="hunt",
		card_type=CardType.ACTION,
		name="Вор",
		description="укради 1 облик у любого игрока",
		ascii_art="  --> (хвать)\n  <-- (тащу!)",
		count=2,
	),
	Card(
		key="enhance",
		card_type=CardType.ACTION,
		name="Камень усиления",
		description="следующий облик +2★ дополнительно",
		ascii_art="   /~~~~\\\n  | *+2★ |\n   \\____/",
		count=2,
	),
	Card(
		key="evolve",
		card_type=CardType.ACTION,
		name="Сделка",
		description="+2 карты, сброси 1 из руки",
		ascii_art="  +++>>>\n  ++карты",
		count=2,
	),
	Card(
		key="roar",
		card_type=CardType.ACTION,
		name="Рёв ужаса",
		description="все другие сбрасывают 1 карту из руки",
		ascii_art="   (((!!!\n  )))!!!)))\n   ~~БУ!~~",
		count=1,
	),
	Card(
		key="spy",
		card_type=CardType.ACTION,
		name="Шпион",
		description="тайно посмотри руку любого игрока",
		ascii_art="  (~_eye_~)\n  (слежка)",
		count=1,
	),
	Card(
		key="steal_discard",
		card_type=CardType.ACTION,
		name="Жулик",
		description="возьми любую карту из сброса",
		ascii_art="  [/////]\n    <---\n  (нашёл!)",
		count=1,
	),
	Card(
		key="peklo",
		card_type=CardType.ACTION,
		name="Пекло",
		description="остальные без Бронечешуи теряют 1 облик",
		ascii_art="   /\\  /\\  /\\\n  /  \\/  \\/  \\\n   (жарко!!!)",
		count=2,
	),
	Card(
		key="exam",
		card_type=CardType.ACTION,
		name="Экзамен по ОКам",
		description="все сбрасывают 1 карту из руки",
		ascii_art="  [?! ТЕСТ !?]\n   !!  !!  !!\n  (сдавай!!!)",
		count=1,
	),
]


def build_deck() -> List[Card]:
	"""Вернуть свежий неперемешанный список всех 32 карт.

	Каждая карта — свежая копия, поэтому изменения во время игры
	не влияют на каталог.

	Возвращает:
		Список из 32 карт, по одной на каждую копию в колоде.
	"""
	deck: List[Card] = []
	for template in _CATALOG:
		for _i in range(template.count):
			deck.append(template.copy())
	return deck


def get_card_by_key(key: str) -> Card:
	"""Вернуть шаблон карты из каталога по ключу.

	Аргументы:
		key: Уникальный ключ, например ``"peklo"`` или ``"krilya"``.

	Возвращает:
		Подходящий шаблон карты.

	Исключения:
		KeyError: Если карты с таким ключом нет.
	"""
	for card in _CATALOG:
		if card.key == key:
			return card
	raise KeyError(f"Неизвестный ключ карты: {key!r}")


LEVEL_NAMES = [
	(0, 3, "Пугало"),
	(4, 6, "Страшилка"),
	(7, 10, "Кошмарик"),
	(11, 9999, "Ужастик"),
]


def level_name(stars: int) -> str:
	"""Вернуть название уровня страшности по числу звёзд.

	Аргументы:
		stars: Текущий счёт страшности.

	Возвращает:
		Название уровня на русском.
	"""
	for low, high, name in LEVEL_NAMES:
		if low <= stars <= high:
			return name
	return "Ужастик"


WIN_THRESHOLD = 15
MAX_HAND_SIZE = 6
INITIAL_HAND_SIZE = 4
