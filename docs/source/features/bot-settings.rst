Bot Settings
============

*Bot API 10.5 — November 22, 2026*

Bot API 10.5 gives bots control over their own settings from code instead of @BotFather:
inline mode, privacy mode, group joins, forum topics in private chats, the topic sidebar,
and how callback queries arrive. It also splits the bot-only fields out of ``User`` into
``BotFullInfo``, and lets bot owners invite up to 10 users at once through a
``https://t.me/botinvite/<bot_username>`` link.


-----

Changing bot settings
---------------------

:meth:`~pyrogram.Client.set_my_settings` maps to Bot API ``setMySettings``. Every parameter
is optional; the ones you omit keep their current value:

.. code-block:: python

    await app.set_my_settings(
        supports_inline_queries=True,
        inline_query_placeholder="Search…",
        can_join_groups=False,               # privacy mode
        has_topics_enabled=True,             # forum topics in private chats
        has_topic_sidebar=True,              # topics in a sidebar
        callback_query_mode="inline",        # "default" | "auto" | "inline"
    )

``callback_query_mode`` decides how callback queries from buttons in messages sent by the
bot arrive: ``"default"`` always fills ``CallbackQuery.message``, ``"inline"`` always fills
``CallbackQuery.inline_message_id``, and ``"auto"`` uses ``inline_message_id`` when the
message is inaccessible to the bot.

Invalid values are rejected before anything is sent: ``callback_query_mode`` must be one of
``"default"``, ``"auto"``, ``"inline"`` and ``inline_feedback_share_denominator`` must be one
of 0, 1, 10, 100, 1000.


-----

Reading the bot's own identity
------------------------------

``getMe`` now returns the bot-only fields on the user object. In vekgram they live on
:obj:`~pyrogram.types.User`:

.. code-block:: python

    me = await app.get_me()

    me.usernames                   # all active usernames of the bot
    me.inline_query_placeholder    # placeholder for inline queries
    me.needs_inline_query_location # whether every inline query asks for the location
    me.has_topic_sidebar           # whether topics show in a sidebar

For another bot's public info, :meth:`~pyrogram.Client.get_bot_info` maps to
``bots.getBotInfo``.


-----

Bot-owner invites
-----------------

A bot owner can invite up to 10 users at once to the private chat with the bot by opening
``https://t.me/botinvite/<bot_username>``. The invited users get a service message whose
:obj:`~pyrogram.types.WriteAccessAllowed` carries the ``inviter``:

.. code-block:: python

    if message.service_type == enums.MessageServiceType.WRITE_ACCESS_ALLOWED:
        inviter = message.write_access_allowed.inviter


-----

Expandable quotations hold blocks
---------------------------------

In 10.5 the ``text`` field of ``RichBlockExpandableBlockQuotation`` (and its input twin) is
replaced by ``blocks``, so an expandable quotation can contain arbitrary blocks:

.. code-block:: python

    await app.send_rich_message(
        chat_id,
        rich_text=types.InputRichMessage(
            blocks=[
                types.InputRichBlockExpandableBlockQuotation(
                    blocks=[types.InputRichBlockParagraph(text="full text")]
                )
            ]
        ),
    )

Passing ``text=`` still works but is deprecated — it is sent as a single paragraph block.
