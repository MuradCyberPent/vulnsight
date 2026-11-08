"""Finds every module and plugs it into the app.

Walks backend/app/modules/**, imports each file, and includes every `router` it finds.
Importing a file is also what registers its checks and hooks.
"""
import importlib
import pkgutil

from fastapi import APIRouter, FastAPI


def load_modules(app: FastAPI) -> list[str]:
    import app.modules as modules_pkg

    routers = []
    for info in pkgutil.walk_packages(modules_pkg.__path__, "app.modules."):
        module = importlib.import_module(info.name)
        router = getattr(module, "router", None)
        if isinstance(router, APIRouter):
            routers.append((info.name, router))
    for name, router in sorted(routers, key=lambda item: item[0]):
        app.include_router(router)
    return [name for name, _ in routers]
