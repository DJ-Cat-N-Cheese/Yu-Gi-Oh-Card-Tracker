import importlib
import sys


_MISSING = object()


def import_with_module_mocks(module_name, module_mocks, purge=()):
    """Import a module with temporary sys.modules fakes and leave no global mocks behind."""
    purge_names = (module_name, *purge)
    purged_originals = {name: sys.modules.get(name, _MISSING) for name in purge_names}
    mock_originals = {name: sys.modules.get(name, _MISSING) for name in module_mocks}

    for name in purge_names:
        sys.modules.pop(name, None)

    try:
        sys.modules.update(module_mocks)
        module = importlib.import_module(module_name)
    finally:
        for name, original in mock_originals.items():
            if original is _MISSING:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = original

    for name in purge_names:
        sys.modules.pop(name, None)

    for name, original in purged_originals.items():
        if original is not _MISSING:
            sys.modules[name] = original
    return module
