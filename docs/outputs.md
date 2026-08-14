# Outputs

A successful **swot-reservoir-wse** extraction produces a reservoir-specific Water Surface Elevation (WSE) time series as a CSV file. When plot generation is enabled, a PNG visualization of the time series is generated alongside it.

LakeSP and PIXC produce different CSV fields because the two workflows derive reservoir WSE from different forms of SWOT observations.

---

## Output Files

Outputs are written to the configured output_dir, which is outputs by default.

File names contain the supplied dam coordinates and the SWOT source used for processing.

For example, a LakeSP extraction may produce:

    outputs/
    ├── 19.69000_73.34000_lakesp_wse.csv
    └── 19.69000_73.34000_lakesp_wse.png

while processing the same reservoir using PIXC may produce:

    outputs/
    ├── 19.69000_73.34000_pixc_wse.csv
    └── 19.69000_73.34000_pixc_wse.png

The source name in the filename allows LakeSP- and PIXC-derived time series for the same reservoir to be stored independently.

---

## LakeSP Output

The LakeSP CSV contains one reservoir WSE observation for each acquisition date remaining after LakeSP processing and temporal filtering.

| Field | Description |
| --- | --- |
| date | Acquisition date of the reservoir observation. |
| wse_median | Representative Water Surface Elevation for the acquisition date, in metres. |
| quality_status | Package-derived representative quality class of the retained LakeSP observations contributing to that date. |

An example LakeSP output is:

    date,wse_median,quality_status
    2026-01-27 00:00:00+00:00,130.0410,SUSPECT
    2026-02-09 00:00:00+00:00,129.4380,SUSPECT
    2026-03-02 00:00:00+00:00,129.0610,SUSPECT
    2026-07-05 00:00:00+00:00,126.3205,DEGRADED

The values shown above are illustrative. Actual observations depend on the reservoir, requested observation period, available SWOT observations, and active processing configuration.

### wse_median

More than one retained LakeSP observation can contribute to the same acquisition date. The wse_median field contains the median WSE of the retained reservoir-associated observations for that date.

Only dates remaining after temporal outlier filtering are written to the final CSV.

### quality_status

The quality_status field is a daily status derived by **swot-reservoir-wse** from the quality classes of the retained LakeSP observations. It should therefore not be interpreted as an additional quality flag provided directly by the SWOT LakeSP product.

The possible values are:

| Status | Description |
| --- | --- |
| GOOD | Representative daily quality class is GOOD. |
| SUSPECT | Representative daily quality class is SUSPECT. |
| DEGRADED | Representative daily quality class is DEGRADED. |
| BAD | Representative daily quality class is BAD. |

The most frequent retained quality class for an acquisition date becomes its quality_status. If two or more classes occur equally often, the poorer class is selected according to:

    GOOD < SUSPECT < DEGRADED < BAD

Only quality classes permitted by the active LakeSP configuration can contribute to this status.

### LakeSP Plot

When plot generation is enabled, the corresponding PNG displays the final LakeSP WSE observations over time.

Observations are shown using quality-dependent markers:

| quality_status | Marker colour |
| --- | --- |
| GOOD | Green |
| SUSPECT | Orange |
| DEGRADED | Red |
| BAD | Black |

The observations are connected chronologically to show the variation in reservoir WSE over the processed period.

---

## PIXC Output

The PIXC CSV contains one reservoir-level observation for each acquisition date remaining after PIXC processing and temporal filtering.

Unlike LakeSP, the PIXC workflow derives reservoir WSE from multiple accepted pixel-cloud measurements. The output therefore includes additional statistics describing the pixel measurements contributing to each reservoir observation.

| Field | Description |
| --- | --- |
| date | Acquisition date of the reservoir observation. |
| wse_median | Median WSE of the accepted reservoir pixels, in metres. |
| wse_mean | Mean WSE of the accepted reservoir pixels, in metres. |
| wse_std | Standard deviation of accepted pixel WSE values, in metres. |
| wse_min | Minimum accepted pixel WSE, in metres. |
| wse_max | Maximum accepted pixel WSE, in metres. |
| pixel_count | Number of accepted PIXC pixels contributing to the observation. |
| mean_water_frac | Mean water_frac value of the contributing pixels. |
| mean_phase_noise | Mean phase_noise_std value of the contributing pixels. |

An example PIXC output is:

    date,wse_median,wse_mean,wse_std,wse_min,wse_max,pixel_count,mean_water_frac,mean_phase_noise
    2026-02-09,129.480713,129.512650,1.017850,121.815918,163.244461,10024,0.956371,0.027555
    2026-03-02,129.146469,129.168106,0.615328,123.090378,165.105972,10641,0.982236,0.027686
    2026-03-09,128.553986,128.561295,0.275325,125.510323,132.760345,9780,0.997505,0.035850

The values shown above are illustrative. Actual observations depend on the reservoir, requested observation period, available PIXC observations, and active processing configuration.

### PIXC WSE Statistics

The wse_median field contains the representative reservoir WSE used in the final PIXC time series.

The additional wse_mean, wse_std, wse_min, and wse_max fields describe the distribution of accepted pixel-level WSE measurements from which that reservoir observation was derived.

The pixel_count field records the number of accepted PIXC pixels contributing to the observation. The mean_water_frac and mean_phase_noise fields provide the corresponding mean water_frac and phase_noise_std values across those pixels.

Only acquisition dates remaining after temporal outlier filtering appear in the final output.

### PIXC Plot

When plot generation is enabled, the corresponding PNG displays the final wse_median observations over time.

PIXC observations do not contain the LakeSP-derived quality_status field, so the LakeSP quality-dependent marker scheme is not applied to PIXC plots.

---

## Plot Generation

PNG generation is optional and controlled by the generate_plot configuration parameter.

Disabling plot generation does not affect CSV generation. The CSV remains the numerical output of every successful extraction.

---

## Output Location

Final products are written to the directory specified by output_dir.

The default location is:

    outputs

Relative paths are resolved from the working directory in which **swot-reservoir-wse** is being used. An absolute output path may also be configured.

See [Configuration](configuration.md) for output locations, plot generation, and other configurable processing parameters.

For details of how LakeSP and PIXC observations are processed before reaching these outputs, see [Package Architecture](architecture.md).
