import copy
import json

from swot_wse.config import (
    DEFAULT_CONFIG,
    load_config,
    save_config,
)


LAKESP_QUALITY_FLAGS = {
    "good",
    "suspect",
    "degraded",
    "bad",
}


def register_config_command(subparsers):
    """
    Register configuration management commands.
    """

    parser = subparsers.add_parser(
        "config",
        help="View or modify package configuration.",
    )

    config_subparsers = parser.add_subparsers(
        dest="config_command",
        required=True,
    )

    show_parser = (
        config_subparsers.add_parser(
            "show",
            help="Display the active configuration.",
        )
    )
    show_parser.set_defaults(
        func=show_config
    )

    set_parser = (
        config_subparsers.add_parser(
            "set",
            help="Modify one configuration value.",
        )
    )
    set_parser.add_argument(
        "key",
        help=(
            "Configuration key. "
            "Nested keys use dotted notation."
        ),
    )
    set_parser.add_argument(
        "value",
        help="New configuration value.",
    )
    set_parser.set_defaults(
        func=set_config
    )

    reset_parser = (
        config_subparsers.add_parser(
            "reset",
            help="Restore the default configuration.",
        )
    )
    reset_parser.set_defaults(
        func=reset_config
    )


def show_config(args):
    """
    Display the active package configuration.
    """

    config = load_config()

    print()
    print(
        json.dumps(
            config,
            indent=4,
        )
    )


def _resolve_key(
    dictionary,
    dotted_key,
):
    """
    Resolve a dotted configuration key.

    Returns the parent dictionary and final key.
    """

    keys = dotted_key.split(".")
    current = dictionary

    for key in keys[:-1]:
        if (
            key not in current
            or not isinstance(
                current[key],
                dict,
            )
        ):
            raise KeyError(
                dotted_key
            )

        current = current[key]

    final_key = keys[-1]

    if final_key not in current:
        raise KeyError(
            dotted_key
        )

    return current, final_key


def _parse_list_value(value):
    """
    Parse a JSON list or comma-separated list.
    """

    value = value.strip()

    if not value:
        raise ValueError

    try:
        parsed = json.loads(value)

    except json.JSONDecodeError:
        parsed = None

    if isinstance(parsed, list):
        parsed = [
            str(item).strip()
            for item in parsed
            if str(item).strip()
        ]

        if not parsed:
            raise ValueError

        return parsed

    if (
        value.startswith("[")
        and value.endswith("]")
    ):
        value = value[1:-1]

    parsed = [
        item
        .strip()
        .strip('"')
        .strip("'")
        for item in value.split(",")
        if item.strip()
    ]

    if not parsed:
        raise ValueError

    return parsed


def _convert_value(
    value,
    default_value,
):
    """
    Convert a CLI string to the type used
    by the corresponding default value.
    """

    if isinstance(
        default_value,
        bool,
    ):
        normalized = (
            value.strip().lower()
        )

        if normalized in (
            "true",
            "1",
            "yes",
            "on",
        ):
            return True

        if normalized in (
            "false",
            "0",
            "no",
            "off",
        ):
            return False

        raise ValueError

    if isinstance(
        default_value,
        int,
    ):
        return int(value)

    if isinstance(
        default_value,
        float,
    ):
        return float(value)

    if isinstance(
        default_value,
        list,
    ):
        return _parse_list_value(
            value
        )

    if default_value is None:
        if (
            value.strip().lower()
            == "none"
        ):
            return None

        return value

    return value


def _validate_config_value(
    key,
    value,
):
    """
    Validate configuration values that have
    explicit package constraints.
    """

    if (
        key == "max_workers"
        and value < 1
    ):
        raise ValueError(
            "max_workers must be at least 1."
        )

    if (
        key == "search_radius_m"
        and value <= 0
    ):
        raise ValueError(
            "search_radius_m must be greater than 0."
        )

    if (
        key == "pekel_threshold"
        and not 0 <= value <= 100
    ):
        raise ValueError(
            "pekel_threshold must be between "
            "0 and 100."
        )

    if (
        key in (
            "sources.lakesp.search_buffer_degrees",
            "sources.pixc.search_buffer_degrees",
        )
        and value < 0
    ):
        raise ValueError(
            "Search buffer cannot be negative."
        )

    if (
        key in (
            "sources.lakesp.mad_threshold",
            "sources.pixc.mad_threshold",
        )
        and value <= 0
    ):
        raise ValueError(
            "MAD threshold must be greater than 0."
        )

    if (
        key
        == "sources.pixc.water_classification"
        and value < 0
    ):
        raise ValueError(
            "PIXC water classification "
            "cannot be negative."
        )


def _normalize_science_cycles(value):
    """
    Normalize science-cycle values to
    zero-padded three-digit strings.
    """

    normalized = []

    for cycle in value:
        cycle_number = int(cycle)

        if cycle_number < 1:
            raise ValueError

        normalized.append(
            f"{cycle_number:03d}"
        )

    return list(
        dict.fromkeys(
            normalized
        )
    )


def _normalize_lakesp_quality_flags(value):
    """
    Validate and normalize LakeSP quality classes.
    """

    normalized = [
        str(flag)
        .strip()
        .lower()
        for flag in value
    ]

    if not normalized:
        raise ValueError(
            "At least one LakeSP quality "
            "class must be selected."
        )

    invalid = [
        flag
        for flag in normalized
        if flag not in LAKESP_QUALITY_FLAGS
    ]

    if invalid:
        raise ValueError(
            "Invalid LakeSP quality class: "
            + ", ".join(invalid)
            + ". Supported values: "
            "good, suspect, degraded, bad."
        )

    return list(
        dict.fromkeys(
            normalized
        )
    )


def set_config(args):
    """
    Modify one configuration parameter.
    """

    config = load_config()

    try:
        default_parent, final_key = (
            _resolve_key(
                DEFAULT_CONFIG,
                args.key,
            )
        )

        config_parent, _ = (
            _resolve_key(
                config,
                args.key,
            )
        )

    except KeyError:
        print(
            f"\nUnknown configuration key: "
            f"{args.key}"
        )
        return

    default_value = (
        default_parent[
            final_key
        ]
    )

    try:
        value = _convert_value(
            args.value,
            default_value,
        )

        _validate_config_value(
            args.key,
            value,
        )

        if args.key in (
            "sources.lakesp.science_cycles",
            "sources.pixc.science_cycles",
        ):
            value = _normalize_science_cycles(
                value
            )

        if (
            args.key
            == "sources.lakesp.accepted_quality_flags"
        ):
            value = (
                _normalize_lakesp_quality_flags(
                    value
                )
            )

    except ValueError as exc:
        message = str(exc)

        if message:
            print(
                f"\nInvalid value. {message}"
            )
        else:
            print(
                "\nInvalid value."
            )

        return

    config_parent[
        final_key
    ] = value

    save_config(
        config
    )

    print(
        f"\nUpdated "
        f"{args.key} = {value}"
    )


def reset_config(args):
    """
    Restore the package default configuration.
    """

    save_config(
        copy.deepcopy(
            DEFAULT_CONFIG
        )
    )

    print(
        "\nConfiguration restored to defaults."
    )