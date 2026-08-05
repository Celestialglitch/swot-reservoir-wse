
import ee

from swot_wse.config import load_config, save_config


def register_auth_command(subparsers):

    parser = subparsers.add_parser(
        "auth",
        help="Authenticate Google Earth Engine.",
    )

    parser.add_argument(
        "--project-id",
        help=(
            "Google Earth Engine project ID. "
            "If omitted, the package prompts for it."
        ),
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Force a new Google Earth Engine authentication "
            "flow instead of reusing existing credentials."
        ),
    )

    parser.set_defaults(func=run_auth)


def run_auth(args):

    config = load_config()

    project = args.project_id

    if project is None:

        project = input(
            "Google Earth Engine project ID: "
        ).strip()

    else:

        project = project.strip()

    if not project:
        print("Project ID cannot be empty.")
        return

    try:

        if args.force:

            print(
                "\nStarting a new Google Earth Engine "
                "authentication flow...\n"
            )

            ee.Authenticate(
                force=True
            )

        else:

            try:

                ee.Initialize(
                    project=project
                )

                print(
                    "\nExisting Google Earth Engine "
                    "credentials found."
                )

            except Exception:

                print(
                    "\nNo valid Google Earth Engine "
                    "credentials found."
                )

                print(
                    "Starting authentication...\n"
                )

                ee.Authenticate()

        ee.Initialize(
            project=project
        )

    except Exception as exc:

        raise RuntimeError(
            "Google Earth Engine authentication "
            "or initialization failed."
        ) from exc

    config[
        "earth_engine_project"
    ] = project

    save_config(
        config
    )

    print(
        "\nAuthentication successful."
    )

    print(
        f"Saved Earth Engine project: {project}"
    )
