#!/usr/bin/env python3

import subprocess
import os
import sys
import argparse

# Default Configuration (can be overridden by command-line arguments)
DEFAULT_REPO_PATH = "/omd/sites/prod/etc/core/conf.d/buhler/prod/dynamic/"
DEFAULT_REMOTE_NAME = "origin"
DEFAULT_BRANCH_NAME = "main"
DEFAULT_TARGET_DIR = "contacts"
GIT_EXECUTABLE = "/usr/bin/git"  # IMPORTANT: Change if git is in a different location!


# Nagios status codes
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


def check_git_updates(repo_path, remote_name, branch_name, target_dir, git_executable):
    """
    Checks if there are new commits to pull from the remote repository,
    specifically looking for changes within the target directory.

    Args:
        repo_path (str): The path to the local git repository.
        remote_name (str): The name of the remote repository (e.g., "origin").
        branch_name (str): The branch to check (e.g., "master").
        target_dir (str): The subdirectory to monitor for changes.
        git_executable (str): The full path to the git executable.

    Returns:
        tuple: A tuple containing the Nagios status code and a message.
    """
    try:
        # Ensure we are in the correct directory
        os.chdir(repo_path)

        # Fetch the latest changes from the remote
        subprocess.run([git_executable, "fetch", remote_name], check=True, capture_output=True)

        # Get the hash of the local branch
        local_hash = subprocess.check_output([git_executable, "rev-parse", branch_name]).decode("utf-8").strip()

        # Get the hash of the remote branch
        remote_hash = subprocess.check_output([git_executable, "rev-parse", f"{remote_name}/{branch_name}"]).decode("utf-8").strip()

        if local_hash != remote_hash:
            # Determine the number of commits affecting the target directory
            try:
                commit_count = subprocess.check_output([
                    git_executable, "rev-list", f"{local_hash}..{remote_hash}", "--count", target_dir
                ]).decode("utf-8").strip()

                if int(commit_count) > 0:
                    return CRITICAL, f"CRITICAL: {commit_count} new commits in {target_dir} to pull from {remote_name}/{branch_name} | commits={commit_count}"
                else:
                    return OK, f"OK: No new commits in {target_dir} to pull from {remote_name}/{branch_name}"

            except subprocess.CalledProcessError as e:
                return WARNING, f"WARNING: Unable to determine commit count in {target_dir}. Possible merge issues. Check manually. Error: {e.stderr.decode('utf-8').strip()}"

        return OK, f"OK: Local repository is up to date with {remote_name}/{branch_name} in {target_dir}"

    except subprocess.CalledProcessError as e:
        return UNKNOWN, f"UNKNOWN: Error executing git command: {e.stderr.decode('utf-8').strip()}"
    except FileNotFoundError:
        return UNKNOWN, "UNKNOWN: Git command not found. Ensure git is installed *and the path is correct in the script.*"
    except OSError as e:
        return UNKNOWN, f"UNKNOWN: Error changing directory to repository: {e}"
    except Exception as e:
        return UNKNOWN, f"UNKNOWN: An unexpected error occurred: {e}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check for Git updates in a local repository.")
    parser.add_argument("--repo_path", default=DEFAULT_REPO_PATH, help="Path to the local Git repository.")
    parser.add_argument("--remote_name", default=DEFAULT_REMOTE_NAME, help="Name of the remote repository.")
    parser.add_argument("--branch_name", default=DEFAULT_BRANCH_NAME, help="Name of the branch to check.")
    parser.add_argument("--target_dir", default=DEFAULT_TARGET_DIR, help="Subdirectory to monitor for changes.")
    args = parser.parse_args()

    status_code, message = check_git_updates(args.repo_path, args.remote_name, args.branch_name, args.target_dir, GIT_EXECUTABLE)
    print(message)
    sys.exit(status_code)