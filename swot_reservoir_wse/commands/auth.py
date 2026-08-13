import getpass
import netrc
import os
from pathlib import Path

import earthaccess
import ee

from swot_reservoir_wse.config import load_config, save_config


EARTHDATA_MACHINE = "urs.earthdata.nasa.gov"


def register_auth_command(subparsers):
    """
    Register authentication management commands.
    """

    parser = subparsers.add_parser(
        "auth",
        help=(
            "Manage Google Earth Engine "
            "and NASA Earthdata authentication."
        ),
    )

    parser.add_argument(
        "--project-id",
        default=None,
        help=(
            "Google Earth Engine project ID. "
            "If omitted, the stored project is reused "
            "or the package prompts for one."
        ),
    )

    action_group = parser.add_mutually_exclusive_group()

    action_group.add_argument(
        "--force",
        action="store_true",
        help=(
            "Force reauthentication instead of "
            "reusing existing credentials."
        ),
    )

    action_group.add_argument(
        "--remove",
        action="store_true",
        help=(
            "Remove locally stored authentication "
            "configuration or credentials."
        ),
    )

    service_group = parser.add_mutually_exclusive_group()

    service_group.add_argument(
        "--earth-engine-only",
        action="store_true",
        help="Manage only Google Earth Engine authentication.",
    )

    service_group.add_argument(
        "--earthdata-only",
        action="store_true",
        help="Manage only NASA Earthdata authentication.",
    )

    parser.set_defaults(func=run_auth)


def _netrc_path():
    """
    Return the netrc path used for Earthdata credentials.
    """

    override = os.environ.get("NETRC")

    if override:
        return Path(override).expanduser().resolve()

    home = Path.home()

    if os.name == "nt":
        return home / "_netrc"

    return home / ".netrc"


def _earthdata_credentials_exist():
    """
    Check whether stored Earthdata credentials exist.
    """

    path = _netrc_path()

    if not path.exists():
        return False

    try:
        credentials = netrc.netrc(str(path))

        return (
            credentials.authenticators(EARTHDATA_MACHINE)
            is not None
        )

    except (netrc.NetrcParseError, OSError):
        return False


def _remove_machine_entry(path, machine):
    """
    Remove a machine entry written in the standard
    block format used by this package.

    Other machine entries are preserved.
    """

    if not path.exists():
        return False

    try:
        lines = path.read_text(
            encoding="utf-8",
        ).splitlines()

    except OSError as exc:
        raise RuntimeError(
            f"Could not read credential file: {path}"
        ) from exc

    cleaned = []
    index = 0
    removed = False

    while index < len(lines):
        stripped = lines[index].strip()

        if stripped.startswith("machine "):
            parts = stripped.split()

            current_machine = (
                parts[1]
                if len(parts) >= 2
                else ""
            )

            if current_machine == machine:
                removed = True
                index += 1

                while index < len(lines):
                    next_line = lines[index].strip()

                    if (
                        next_line.startswith("machine ")
                        or next_line.startswith("default ")
                    ):
                        break

                    index += 1

                continue

        cleaned.append(lines[index])
        index += 1

    if not removed:
        return False

    remaining = "\n".join(cleaned).strip()

    try:
        if remaining:
            path.write_text(
                remaining + "\n",
                encoding="utf-8",
            )
        else:
            path.unlink()

    except OSError as exc:
        raise RuntimeError(
            f"Could not update credential file: {path}"
        ) from exc

    return True


def _remove_earthdata_credentials():
    """
    Remove stored NASA Earthdata credentials.
    """

    path = _netrc_path()

    removed = _remove_machine_entry(
        path,
        EARTHDATA_MACHINE,
    )

    if removed:
        print(
            "\nNASA Earthdata credentials removed."
        )
    else:
        print(
            "\nNo stored NASA Earthdata "
            "credentials were found."
        )


def _save_earthdata_credentials(
    username,
    password,
):
    """
    Save validated Earthdata credentials
    to the user's netrc file.
    """

    path = _netrc_path()

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    _remove_machine_entry(
        path,
        EARTHDATA_MACHINE,
    )

    entry = (
        f"machine {EARTHDATA_MACHINE}\n"
        f"login {username}\n"
        f"password {password}\n"
    )

    try:
        if path.exists():
            existing = path.read_text(
                encoding="utf-8",
            ).rstrip()

            content = (
                existing + "\n\n" + entry
                if existing
                else entry
            )
        else:
            content = entry

        path.write_text(
            content,
            encoding="utf-8",
        )

        if os.name != "nt":
            path.chmod(0o600)

    except OSError as exc:
        raise RuntimeError(
            "Earthdata authentication succeeded, "
            "but the credentials could not be saved."
        ) from exc


def _validate_earthdata_credentials(
    username,
    password,
):
    """
    Validate Earthdata credentials without
    persisting them.
    """

    old_username = os.environ.get(
        "EARTHDATA_USERNAME"
    )
    old_password = os.environ.get(
        "EARTHDATA_PASSWORD"
    )

    os.environ[
        "EARTHDATA_USERNAME"
    ] = username

    os.environ[
        "EARTHDATA_PASSWORD"
    ] = password

    try:
        auth = earthaccess.login(
            strategy="environment",
            persist=False,
        )

        return bool(auth.authenticated)

    except Exception:
        return False

    finally:
        if old_username is None:
            os.environ.pop(
                "EARTHDATA_USERNAME",
                None,
            )
        else:
            os.environ[
                "EARTHDATA_USERNAME"
            ] = old_username

        if old_password is None:
            os.environ.pop(
                "EARTHDATA_PASSWORD",
                None,
            )
        else:
            os.environ[
                "EARTHDATA_PASSWORD"
            ] = old_password


def _authenticate_earthdata(force=False):
    """
    Authenticate NASA Earthdata Login.
    """

    if (
        not force
        and _earthdata_credentials_exist()
    ):
        try:
            auth = earthaccess.login(
                strategy="netrc",
                persist=False,
            )

            if auth.authenticated:
                print(
                    "\nExisting NASA Earthdata "
                    "credentials found."
                )
                return

        except Exception:
            pass

        print(
            "\nStored NASA Earthdata credentials "
            "are no longer valid."
        )

    print(
        "\nStarting NASA Earthdata "
        "authentication...\n"
    )

    username = input(
        "Earthdata Login username: "
    ).strip()

    if not username:
        raise RuntimeError(
            "Earthdata username cannot be empty."
        )

    password = getpass.getpass(
        "Earthdata password: "
    )

    if not password:
        raise RuntimeError(
            "Earthdata password cannot be empty."
        )

    if not _validate_earthdata_credentials(
        username,
        password,
    ):
        raise RuntimeError(
            "NASA Earthdata authentication failed. "
            "Please verify your username and password."
        )

    # The old credential is replaced only after
    # the new credential has been validated.
    _save_earthdata_credentials(
        username,
        password,
    )

    try:
        auth = earthaccess.login(
            strategy="netrc",
            persist=False,
        )

        if not auth.authenticated:
            raise RuntimeError

    except Exception as exc:
        raise RuntimeError(
            "NASA Earthdata credentials were validated "
            "but could not be reused from the stored "
            "credential file."
        ) from exc

    print(
        "\nNASA Earthdata authentication successful."
    )
    print(
        f"Credentials saved to: {_netrc_path()}"
    )


def _authenticate_earth_engine(
    project,
    force=False,
):
    """
    Authenticate and initialize Google Earth Engine.
    """

    if isinstance(project, str):
        project = project.strip()

    if not project:
        project = input(
            "Google Earth Engine project ID: "
        ).strip()

    if not project:
        raise RuntimeError(
            "Google Earth Engine project ID "
            "cannot be empty."
        )

    if force:
        print(
            "\nStarting new Google Earth Engine "
            "authentication...\n"
        )

        ee.Authenticate(force=True)
        ee.Initialize(project=project)

        print(
            "\nGoogle Earth Engine "
            "authentication successful."
        )

        return project

    try:
        ee.Initialize(project=project)

    except Exception:
        print(
            "\nNo valid Google Earth Engine "
            "credentials found."
        )
        print(
            "Starting authentication...\n"
        )

        ee.Authenticate()
        ee.Initialize(project=project)

        print(
            "\nGoogle Earth Engine "
            "authentication successful."
        )

    else:
        print(
            "\nExisting Google Earth Engine "
            "credentials found."
        )

    return project


def _remove_earth_engine_configuration():
    """
    Remove the Earth Engine project stored
    by swot-reservoir-wse.

    Google-managed OAuth credentials are not deleted.
    """

    config = load_config()
    config["earth_engine_project"] = None

    save_config(config)

    print(
        "\nStored Google Earth Engine "
        "Project ID removed."
    )


def run_auth(args):
    """
    Manage Google Earth Engine and
    NASA Earthdata authentication.
    """

    if (
        args.earthdata_only
        and args.project_id is not None
    ):
        raise RuntimeError(
            "--project-id cannot be used with "
            "--earthdata-only."
        )

    manage_earth_engine = (
        not args.earthdata_only
    )
    manage_earthdata = (
        not args.earth_engine_only
    )

    if args.remove:
        if manage_earth_engine:
            _remove_earth_engine_configuration()

        if manage_earthdata:
            _remove_earthdata_credentials()

        return

    if manage_earth_engine:
        config = load_config()

        project = (
            args.project_id
            or config["earth_engine_project"]
        )

        project = _authenticate_earth_engine(
            project=project,
            force=args.force,
        )

        config["earth_engine_project"] = project
        save_config(config)

        print(
            f"Saved Earth Engine project: {project}"
        )

    if manage_earthdata:
        _authenticate_earthdata(
            force=args.force,
        )