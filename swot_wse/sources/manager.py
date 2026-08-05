from swot_wse.sources.lakesp_source import run_lakesp_pipeline


SOURCES = {
    "lakesp": run_lakesp_pipeline,
}


def run_source(source, polygon, start_date, end_date):
    """
    Execute any SWOT science product source.

    Parameters
    ----------
    source : Source name.
    polygon : Reservoir footprint.
    start_date : Start date (YYYY-MM-DD).
    end_date : End date (YYYY-MM-DD).

    """
    source = source.lower()

    try:
        runner = SOURCES[source]
    except KeyError:
        raise ValueError(f"Unsupported source: {source}")

    return runner(
        polygon=polygon,
        start_date=start_date,
        end_date=end_date,
    )