
import json

from swot_wse.config import (
    DEFAULT_CONFIG,
    load_config,
    save_config,
)


def register_config_command(subparsers):

    parser = subparsers.add_parser(
        "config",
        help="Show or modify package configuration.",
    )

    config_sub = parser.add_subparsers(
        dest="config_command",
        required=True,
    )

    # ------------------------------------------
    # show
    # ------------------------------------------

    show = config_sub.add_parser(
        "show",
        help="Display current configuration.",
    )

    show.set_defaults(func=show_config)

    # ------------------------------------------
    # set
    # ------------------------------------------

    set_cmd = config_sub.add_parser(
        "set",
        help="Modify one configuration value.",
    )

    set_cmd.add_argument(
        "key",
        help="Configuration key (supports nested keys).",
    )

    set_cmd.add_argument(
        "value",
        help="New value.",
    )

    set_cmd.set_defaults(func=set_config)

    # ------------------------------------------
    # reset
    # ------------------------------------------

    reset = config_sub.add_parser(
        "reset",
        help="Restore default configuration.",
    )

    reset.set_defaults(func=reset_config)


def show_config(args):

    config = load_config()

    print()
    print(
        json.dumps(
            config,
            indent=4,
        )
    )


def _resolve_key(dictionary, dotted_key):
    """
    Resolve a dotted configuration key.

    Returns
    -------
    parent_dict, final_key
    """

    keys = dotted_key.split(".")

    current = dictionary

    for key in keys[:-1]:

        if (
            key not in current
            or not isinstance(current[key], dict)
        ):
            raise KeyError(dotted_key)

        current = current[key]

    if keys[-1] not in current:
        raise KeyError(dotted_key)

    return current, keys[-1]


def set_config(args):

    config = load_config()

    try:

        default_parent, final_key = _resolve_key(
            DEFAULT_CONFIG,
            args.key,
        )

        config_parent, _ = _resolve_key(
            config,
            args.key,
        )

    except KeyError:

        print(
            f"\nUnknown configuration key: "
            f"{args.key}"
        )

        return

    default_value = default_parent[
        final_key
    ]

    value = args.value

    try:

        if isinstance(default_value, bool):

            value = value.lower()

            if value in (
                "true",
                "1",
                "yes",
                "on",
            ):
                value = True

            elif value in (
                "false",
                "0",
                "no",
                "off",
            ):
                value = False

            else:
                raise ValueError

        elif isinstance(default_value, int):

            value = int(value)

        elif isinstance(default_value, float):

            value = float(value)

        elif isinstance(default_value, list):

            value = json.loads(value)

            if not isinstance(value, list):
                raise ValueError

        elif default_value is None:

            if value.lower() == "none":
                value = None

    except (
        ValueError,
        json.JSONDecodeError,
    ):

        print("\nInvalid value.")

        if isinstance(default_value, list):
            print(
                "List values must use JSON format, "
                'for example: ["001", "002", "003"]'
            )

        return

    config_parent[final_key] = value

    save_config(config)

    print(
        f"\nUpdated {args.key} = {value}"
    )


def reset_config(args):

    save_config(
        DEFAULT_CONFIG
    )

    print(
        "\nConfiguration restored to defaults."
    )
