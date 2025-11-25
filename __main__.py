"""Example entrypoint that ensures Advent Calendar models are loaded in Tortoise."""

from copy import deepcopy

try:
    # Re-use the bot's existing Tortoise ORM settings when available.
    from ballsdex.__main__ import TORTOISE_ORM as BASE_TORTOISE_ORM  # type: ignore
except Exception:  # pragma: no cover - fallback for package-only environments
    BASE_TORTOISE_ORM = {
        "connections": {"default": "postgres://user:pass@localhost:5432/ballsdex"},
        "apps": {"models": {"models": ["ballsdex.core.models"], "default_connection": "default"}},
    }

TORTOISE_ORM = deepcopy(BASE_TORTOISE_ORM)
models_app = TORTOISE_ORM.setdefault("apps", {}).setdefault("models", {})
modules = list(models_app.get("models", []))
if "ballsdex.packages.adventcalendar.models" not in modules:
    modules.append("ballsdex.packages.adventcalendar.models")
models_app["models"] = modules

if __name__ == "__main__":
    import asyncio

    from tortoise import Tortoise

    async def init():
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.close_connections()

    asyncio.run(init())
