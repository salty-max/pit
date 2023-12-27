import subprocess


def get_default_branch_name():
    """Use git to get the default branch name from the global config"""
    try:
        result = subprocess.run(
            ["git", "config", "--global", "init.defaultBranch"],
            capture_output=True,
            text=True,
            check=True,
        )
        default_branch_name = result.stdout.strip()
        return default_branch_name
    except subprocess.CalledProcessError as e:
        print("Failed to get git global configuration: ", e)
        return "main"


def get_user_name_email():
    """Use git to get the default user name and email from the global config"""
    try:
        name = subprocess.run(
            ["git", "config", "--global", "user.name"],
            capture_output=True,
            text=True,
            check=True,
        )
        email = subprocess.run(
            ["git", "config", "--global", "user.email"],
            capture_output=True,
            text=True,
            check=True,
        )
        user_info = "{0} {1}".format(name.stdout.strip(), email.stdout.strip())
        return user_info
    except subprocess.CalledProcessError as e:
        print("Failed to get git global configuration: ", e)
        return "main"
