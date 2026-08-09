import pytest


@pytest.hookimpl(trylast=True)
def pytest_unconfigure(config):
    """Close the in-memory databases left open by the coverage reports

    Coverage re-maps the collected data into a new in-memory sqlite database
    for each report (Coverage._prepare_data_for_reporting) and it only closes
    them from the atexit handler registered when the process measures coverage
    (Coverage._init_for_start).

    The pytest-xdist controller process does not measure coverage, only the
    workers do, so the handler is not registered there and python>=3.13 emits
    "ResourceWarning: unclosed database" for each report at interpreter exit.

    TODO: Remove it when coverage closes the databases of _data_to_close from
    the reporting methods
    """
    cov_plugin = config.pluginmanager.get_plugin("_cov")
    cov = getattr(getattr(cov_plugin, "cov_controller", None), "cov", None)
    for data in getattr(cov, "_data_to_close", []):
        data.close(force=True)
