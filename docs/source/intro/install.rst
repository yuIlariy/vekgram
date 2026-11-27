Install Guide
=============

Import ``vekgram``:

.. code-block:: python

    from vekgram import Client, filters

``pyrogram`` still imports, and resolves to the same module rather than a second copy of it,
so ``vekgram.types.Message is pyrogram.types.Message`` and an existing Pyrogram codebase runs
unchanged. Use it only for that — new code should say ``vekgram``.

.. note::

    The *package* is still ``pyrogram``, and that is deliberate: it is what makes vekgram a
    drop-in replacement. Tracebacks, ``repr()`` and the ``.. module::`` targets in this
    documentation all name ``pyrogram``, because that is where the classes live.

vekgram requires **Python 3.10 or newer**. Nothing else has to be installed by hand: the Rust
crypto backend and the SQLite driver come with it as wheels.


-----

Install
-------

.. code-block:: bash

    $ pip install vekgram

That is the whole thing. Verify it:

.. code-block:: bash

    $ python3 -c "import vekgram; print(vekgram.__version__)"

If a version number prints, you are done.

.. note::

    ``pip install "vekgram[fast]"`` additionally installs uvloop on Linux and macOS (CPython).
    ``warpcrypto`` is a core dependency, so ``vekgram[fast]`` automatically installs **both
    uvloop and warpcrypto**. See :doc:`/topics/speedups` for how to enable uvloop.

.. note::

    Do not install ``pyrogram`` and ``vekgram`` side by side. They provide the same
    ``pyrogram`` module and whichever was installed last wins, which is a confusing way to
    find out. Run ``pip uninstall pyrogram`` first if it is already there.

Use a virtual environment
-------------------------

Installing into the system Python works until two projects want different versions. A virtual
environment per project avoids that entirely:

.. code-block:: bash

    $ python3 -m venv venv
    $ source venv/bin/activate        # Windows: venv\Scripts\activate
    $ pip install vekgram

Everything installed while it is active stays inside ``venv/``. Deleting that directory
uninstalls it.

Upgrading
---------

.. code-block:: bash

    $ pip install -U vekgram

Telegram's API moves — new layers, new methods, new fields on existing types. Upgrading is
how you get them, and how you get fixes to the transfer and reconnection paths.

Development version
-------------------

The ``vek`` branch is the default branch where work lands before a release:

.. code-block:: bash

    $ pip install -U git+https://github.com/yuIlariy/vekgram.git@vek

It is generally usable and occasionally not. Pin a release for anything you cannot babysit.

Building from source
--------------------

Working *on* vekgram needs one extra step, because ``pyrogram/raw/`` is generated from the TL
schema and is not committed:

.. code-block:: bash

    $ git clone https://github.com/yuIlariy/vekgram.git
    $ cd vekgram
    $ pip install uv
    $ uv sync --frozen --extra dev
    $ uv run poe api            # generates pyrogram/raw/** and the error classes
    $ uv run poe test

``poe api`` is required before anything imports ``pyrogram`` from a fresh checkout. A wheel
built with ``uv run poe build`` runs the generators itself, so an installed vekgram never
needs this.

Troubleshooting
---------------

**"No module named 'pyrogram'" right after installing**
    The install went into a different Python than the one you are running. Check with
    ``python3 -m pip install vekgram`` — that form always matches the interpreter.

**"No module named 'pyrogram.raw'" from a git checkout**
    ``poe api`` has not been run. See above.

**pip starts compiling Rust**
    vekgram itself is pure Python, but its ``warpcrypto`` dependency is a Rust extension. pip
    falls back to building it from source when no wheel matches your Python version, platform
    or libc — which then needs a Rust toolchain. Upgrading pip first is usually enough, since
    an old pip rejects wheel tags it does not understand.

**A ``pyrogram`` install shadowing vekgram**
    See the note above — uninstall it.
