import ee

from swot_wse.config import load_config, save_config


def register_auth_command(subparsers):

    parser = subparsers.add_parser(
        "auth",
        help="Authenticate Google Earth Engine.",
    )

    parser.set_defaults(func=run_auth)


def run_auth(args):

    config = load_config()

    project = input(
        "Google Earth Engine project ID: "
    ).strip()

    if not project:
        print("Project ID cannot be empty.")
        return

    try:

        # Already authenticated?
        ee.Initialize(project=project)

        print("\n Existing Google Earth Engine credentials found.")

    except Exception:

        print("\nNo valid Google Earth Engine credentials found.")
        print("Starting authentication...\n")

        ee.Authenticate()

        ee.Initialize(project=project)

        print("\n !!! Authentication is successful and credentials are saved !!!")

    config["earth_engine_project"] = project
    save_config(config)

    print(f"✓ Saved project: {project}")