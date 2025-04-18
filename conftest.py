import os
import datetime


def pytest_configure(config):
    """
    Configure file path for main HTML report in 'reports/' directory.
    """
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = os.path.join(config.rootpath, 'reports')
    os.makedirs(report_dir, exist_ok=True)
    if config.pluginmanager.hasplugin('html'):
        config.option.htmlpath = os.path.join(report_dir, f"report_{now}.html")
