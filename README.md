<div align="center">

<img src="https://raw.githubusercontent.com/yuIlariy/vekgram/vek/assets/png/vekgram-icon-256.png" alt="vekgram" width="160">

# vekgram

[![PyPI](https://img.shields.io/pypi/v/vekgram)](https://pypi.org/project/vekgram/)
[![Python](https://img.shields.io/pypi/pyversions/vekgram)](https://pypi.org/project/vekgram/)
[![Downloads](https://img.shields.io/pypi/dm/vekgram)](https://pypi.org/project/vekgram/)
[![License](https://img.shields.io/github/license/yuIlariy/vekgram)](https://github.com/yuIlariy/vekgram/blob/vek/COPYING.lesser)

**Elegant, modern and asynchronous Telegram MTProto API framework in Python for users and bots**

</div>

vekgram is a **drop-in replacement** for Pyrogram, with access to the latest Telegram features including **Gifts, Stories, Topics, Business Accounts**, and more. Import `vekgram`; `from pyrogram import ...` still resolves to the same module rather than a second copy of it, so an existing Pyrogram codebase runs unchanged.

```python
from vekgram import Client, filters

app = Client("my_account")


@app.on_message(filters.private)
async def hello(client, message):
    await message.reply("Hello from vekgram!")


app.run()
```

`from pyrogram import Client, filters` works too — both names are one module: `vekgram.types.Message is pyrogram.types.Message`.

### Key Features

- **Drop-in Replacement** — New code says `from vekgram import ...`; existing `from pyrogram import ...` codebases migrate with zero changes, since both names are one module.
- **Up-to-Date** — Supports Gifts, Stories, Topics, Business Accounts, Giveaways, and the latest Telegram layer.
- **Async Natively** — Fully `async`/`await` throughout. Also usable synchronously via `app.run()` for convenience.
- **Type-hinted** — Every type and method is annotated for excellent editor support.
- **Fast** — Boosted by [WarpCrypto](https://github.com/rjriajul/WarpCrypto), a high-performance cryptography library written in Rust. `warpcrypto` is a core dependency, so it is always installed with vekgram.
- **Powerful** — Full access to Telegram's API for any official client action and more.

### Example with Inline Keyboard

```python
from vekgram import Client, filters
from vekgram.types import InlineKeyboardMarkup, InlineKeyboardButton

app = Client("my_bot")


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "Choose an option:",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Website", url="https://example.com"),
                InlineKeyboardButton("Help", callback_data="help"),
            ],
            [InlineKeyboardButton("About", callback_data="about")],
        ])
    )


app.run()
```

### Installing

```bash
pip install vekgram
```

Or in `requirements.txt`:

```text
vekgram[fast]
```

Requires Python 3.10+. `vekgram[fast]` additionally pulls in [uvloop](https://github.com/MagicStack/uvloop) on Linux and macOS (CPython); call `uvloop.install()` yourself to use it (see the Speedups guide). Because `warpcrypto` is a core dependency, `vekgram[fast]` automatically installs **both uvloop and warpcrypto** — the same way `wzgram[fast]` did:

```bash
pip install "vekgram[fast]"
```

Do not install `pyrogram` and `vekgram` side by side: they provide the same `pyrogram` module and whichever was installed last wins. Run `pip uninstall pyrogram` first if it is already there.

### Development

```bash
# Clone the repo
git clone https://github.com/yuIlariy/vekgram.git
cd vekgram

# Install uv (if not already)
pip install uv

# Create virtual environment with dev dependencies
uv sync --frozen --extra dev

# Generate TL API types
uv run poe api

# Run tests
uv run poe test
```

### Publishing to PyPI

Releases are fully automatic and published with **PyPI Trusted Publishing (OIDC)** — no API token is stored anywhere. Push a version tag (`git tag v3.1.8 && git push origin v3.1.8`) and `.github/workflows/publish.yml` builds the package, runs `uv publish dist/*` (the `id-token: write` permission in the `vekgram` environment lets uv exchange the OIDC token automatically), and creates the GitHub release with the `dist/` assets. The trusted publisher on PyPI is registered for this repository (`yuIlariy/vekgram`), workflow `publish.yml`, environment `vekgram`, any ref. `pip install vekgram` always comes from **PyPI**, not from GitHub releases. One-click release: **Actions → Release → Run workflow** (`.github/workflows/release.yml` bumps `__version__` in `pyrogram/__init__.py`, commits, tags and pushes — which triggers the publish).

### Credits

- [Pyrogram](https://github.com/pyrogram/pyrogram) by **Dan** — the original MTProto framework.
- [wzgram](https://github.com/rjriajul/wzgram) by **rjriajul** — the base of this fork, including [WarpCrypto](https://github.com/rjriajul/WarpCrypto), the Rust crypto backend.
- **vekgram** by [yuIlariy](https://t.me/xspes) ([GitHub](https://github.com/yuIlariy)).

### Resources

- [Source code](https://github.com/yuIlariy/vekgram)
- [Issue tracker](https://github.com/yuIlariy/vekgram/issues)
- [Contributing guide](https://github.com/yuIlariy/vekgram/blob/vek/CONTRIBUTING.md)
- [Telegram channel](https://t.me/vekgram) — news, releases, announcements
- [Telegram group](https://t.me/vekgramchat) — questions and discussion
- [Maintainer on Telegram](https://t.me/xspes)
