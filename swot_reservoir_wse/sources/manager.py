from swot_reservoir_wse.sources.lakesp_source import run_lakesp_pipeline
from swot_reservoir_wse.sources.pixc_source import run_pixc_pipeline


SOURCES = {
    "lakesp": run_lakesp_pipeline,
    "pixc": run_pixc_pipeline,
}


def run_source(
    source,
    polygon,
    start_date,
    end_date,
):
    """
    Execute the selected SWOT observation source.
    """

    source = str(source).strip().lower()

    if source not in SOURCES:
        supported_sources = ", ".join(
            sorted(SOURCES)
        )

        raise ValueError(
            f"Unsupported source: {source}. "
            f"Supported sources: {supported_sources}"
        )

    runner = SOURCES[source]

    return runner(
        polygon=polygon,
        start_date=start_date,
        end_date=end_date,
    )