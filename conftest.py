import os
import datetime

# Global variable to store generated benchmark report path
benchmark_html_path = None


def pytest_addoption(parser):
    """
    Add default --benchmark-html option so pytest-benchmark writes HTML report automatically.
    """
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = os.path.join(os.getcwd(), 'reports')
    os.makedirs(report_dir, exist_ok=True)
    default_path = os.path.join(report_dir, f"benchmark_{now}.html")
    parser.addoption(
        "--benchmark-html",
        action="store",
        default=default_path,
        help="Path to write pytest-benchmark HTML report",
    )


def pytest_configure(config):
    """
    Configure file path for main HTML report in 'reports/' directory.
    Also capture benchmark_html_path for embedding.
    """
    global benchmark_html_path
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = os.path.join(config.rootpath, 'reports')
    os.makedirs(report_dir, exist_ok=True)

    # Main pytest-html report
    if config.pluginmanager.hasplugin('html'):
        config.option.htmlpath = os.path.join(report_dir, f"report_{now}.html")

    # Capture the benchmark HTML path set via CLI (default from pytest_addoption)
    if config.pluginmanager.hasplugin('benchmark'):
        benchmark_html_path = getattr(config.option, 'benchmark_html', None)


def pytest_html_results_summary(prefix, summary, postfix):
    """
    Append a link and embed the benchmark report using raw HTML strings.
    """
    global benchmark_html_path
    if benchmark_html_path and os.path.exists(benchmark_html_path):
        relpath = os.path.basename(benchmark_html_path)
        # Link to the benchmark report
        prefix.append(f'<p>View Benchmark Report: <a href="{relpath}">{relpath}</a></p>')
        # Embed the report via iframe
        prefix.append(f'<iframe src="{relpath}" width="100%" height="600"></iframe>')


def pytest_sessionfinish(session, exitstatus):
    """
    After tests complete, explicitly instruct pytest-benchmark plugin to write the HTML report.
    """
    global benchmark_html_path
    if not benchmark_html_path:
        return
    bench_plugin = session.config.pluginmanager.get_plugin('benchmark')
    if not bench_plugin:
        return
    # Try known methods to write HTML
    for method in ('write_html', 'save_html', 'generate_html'):
        fn = getattr(bench_plugin, method, None)
        if callable(fn):
            try:
                fn(benchmark_html_path)
            except Exception:
                continue
            break
