# Git Directory Update Checker for Nagios

This Python script checks if there are **new commits** in a remote Git repository for a **specific subdirectory** of interest (e.g., `contacts`).  

It is intended to be used as a **Nagios monitoring plugin**, returning Nagios-compatible exit codes based on repository status.

***

## Features

- Monitors a **local Git repository** for updates from a specified remote branch.
- Focuses on a **given subdirectory** (e.g., configuration files or scripts).
- Returns Nagios **status codes**:
  - `0` → OK
  - `1` → WARNING
  - `2` → CRITICAL
  - `3` → UNKNOWN
- Fully configurable via **command-line arguments** or **defaults in the script**.

***

## Default Configuration

The script has built‑in defaults, which can be overridden via arguments.

| Parameter        | Default Value | Description |
|------------------|--------------|-------------|
| `repo_path`      | `/omd/sites/prod/etc/core/conf.d/buhler/prod/dynamic/` | Local repository path |
| `remote_name`    | `origin`     | Git remote name |
| `branch_name`    | `main`       | Branch to monitor |
| `target_dir`     | `contacts`   | Subdirectory within repo to check |
| `git_executable` | `/usr/bin/git` | Path to Git executable |

***

## How It Works

1. **Changes directory** to the specified local repository.
2. **Fetches** the latest state from the specified Git remote.
3. **Compares commit hashes** between local and remote branches.
4. If there are differences:
   - Counts commits **affecting only the specified subdirectory**.
   - Returns:
     - **CRITICAL (2)** if there are new commits in the monitored directory.
     - **OK (0)** if there are no new commits in the monitored directory despite differences in the repo.
5. Returns appropriate **Nagios exit code**.

***

## Installation

1. Copy the script to a monitoring plugins directory:
   ```bash
   cp check_git_subdir_updates.py /usr/local/bin/
   chmod +x /usr/local/bin/check_git_subdir_updates.py
   ```

2. Ensure Python 3 and Git are installed:
   ```bash
   python3 --version
   git --version
   ```

3. Update the `GIT_EXECUTABLE` constant in the script if your Git binary is not at `/usr/bin/git`.

***

## Usage

### Command-line
```bash
./check_git_subdir_updates.py \
  --repo_path /path/to/local/repo \
  --remote_name origin \
  --branch_name main \
  --target_dir contacts
```

Example:
```bash
./check_git_subdir_updates.py --repo_path /srv/repos/my-project --target_dir config
```

***

### Output

Depending on the state of the repository, you might see:

- **OK (0)** – No updates for the target directory:
  ```
  OK: No new commits in contacts to pull from origin/main
  ```

- **CRITICAL (2)** – New commits affecting the target directory:
  ```
  CRITICAL: 3 new commits in contacts to pull from origin/main | commits=3
  ```

- **WARNING (1)** – Unable to determine commit count:
  ```
  WARNING: Unable to determine commit count in contacts. Possible merge issues. Check manually.
  ```

- **UNKNOWN (3)** – Git not found or another error:
  ```
  UNKNOWN: Git command not found. Ensure git is installed and the path is correct in the script.
  ```

***

## Exit Codes

| Code | Status    | Description |
|------|-----------|-------------|
| 0    | OK        | Repository up to date or no relevant changes |
| 1    | WARNING   | Commit count could not be determined |
| 2    | CRITICAL  | New commits detected in monitored directory |
| 3    | UNKNOWN   | Unexpected errors, Git not found, or inaccessible repo |

***

## Troubleshooting

- **Git not found** → Update `GIT_EXECUTABLE` in the script to the correct path for your system.
- **Permissions errors** → Ensure the Nagios user can read the repo path and execute Git commands.
- **Merge or branch issues** → The script assumes a clean Git state; pending merges may need manual resolution.

***
