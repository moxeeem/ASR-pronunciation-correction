import dotenv
import os


def try_get_env_vars(
    variable_names: list[str], load_dotenv: bool = False
) -> tuple[bool, dict]:
    """
    Tries to load all specified environment variable into a dictionary.
    Returns tuple of:
    - result flag (bool: True if all variables was loaded)
    - env vars values (dict)
    """
    if load_dotenv:
        dotenv.load_dotenv()

    env: dict[str, str] = {}

    for var_name in variable_names:
        value = os.environ.get(var_name)
        if value is None:
            return (False, env)
        env[var_name] = value

    return (True, env)
