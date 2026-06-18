Справочник API
==============

Описание публичных классов и функций пакета ``monstromaker``.

Запуск
------

.. autofunction:: monstromaker.__main__.main

.. autofunction:: monstromaker.cli.run_game

.. autofunction:: monstromaker.cli.prompt_player_names

Карты
-----

.. autoclass:: monstromaker.cards.CardType
   :members:

.. autoclass:: monstromaker.cards.Card
   :members: display_type, total_stars, copy

.. autofunction:: monstromaker.cards.build_deck

.. autofunction:: monstromaker.cards.get_card_by_key

.. autofunction:: monstromaker.cards.level_name

.. py:data:: monstromaker.cards.WIN_THRESHOLD

.. py:data:: monstromaker.cards.INITIAL_HAND_SIZE

.. py:data:: monstromaker.cards.MAX_HAND_SIZE

Игрок и колода
--------------

.. autoclass:: monstromaker.player.Player
   :members:

.. autoclass:: monstromaker.deck.Deck
   :members:

Игровая логика
--------------

.. autoclass:: monstromaker.game.TurnResult
   :members:

.. autoclass:: monstromaker.game.Game
   :members: setup, current_player, begin_turn, play_card, pass_turn, advance_turn

Локализация
-----------

.. autofunction:: monstromaker.i18n.setup_i18n

.. autofunction:: monstromaker.i18n.get_translator

Отображение
-----------

.. automodule:: monstromaker.display
   :members:
