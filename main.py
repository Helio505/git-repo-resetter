import os
import subprocess
import sys
from pathlib import Path

BACKUP_DIR = Path.home() / "Downloads"
BRANCH_NAME = "main"  # Default branch name, can be changed if needed
COMMIT_MESSAGE = "Initial commit (History reset)"  # Default commit message


def check_correct_OS():
    """Checks if the script is running on a supported operating system."""
    is_correct_os = os.name == "nt"  # 'nt' indicates Windows
    return is_correct_os


def check_git_installed():
    """Checks if Git is installed on the system."""
    try:
        subprocess.run(
            ["git", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_git_repository(path):
    """Checks if the provided path is a valid Git repository."""
    git_dir = os.path.join(path, ".git")
    return os.path.isdir(git_dir)


def has_dir_write_permission(path):
    """Checks if the user has write permissions for the directory."""
    return os.access(path, os.W_OK)


def has_repo_write_permission(path):
    """Checks if the user has write permissions for the Git repository."""
    try:
        subprocess.run(
            ["git", "ls-remote", "--exit-code"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def check_remote_origin(path):
    """Checks if the 'origin' remote is configured."""
    try:
        result = subprocess.run(
            ["git", "remote"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return "origin" in result.stdout.split()
    except subprocess.CalledProcessError:
        return False


def get_repo_slug(path):
    """Extracts the repository slug from the remote origin URL."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        url = result.stdout.strip()
        # Remove trailing slashes and '.git' extension if present
        if url.endswith(".git"):
            url = url[:-4]
        # The slug is the last part of the URL path
        slug = url.split("/")[-1].split(":")[-1]
        return slug if slug else "repo_backup"
    except subprocess.CalledProcessError:
        # Fallback to folder name if git command fails
        return os.path.basename(os.path.abspath(path))


def make_backup(repo_path, repo_slug):
    """Creates a backup of the current repository."""
    # Saves the backup in the user's Downloads folder by default
    backup_zip = os.path.join(BACKUP_DIR, f"{repo_slug}_backup.zip")

    print(f"\nCreating a backup of the repository at: {backup_zip}")
    try:
        subprocess.run(
            ["powershell", "-Command", f"Compress-Archive -Path '{repo_path}\\*' -DestinationPath '{backup_zip}' -Force"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print("✅ Backup created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating backup: {e.stderr.decode().strip()}")
        sys.exit(1)


def run_git_command(command, path):
    """Executes a Git command and displays output or error details."""
    print(f"⚡ Executing: {' '.join(command)}")
    result = subprocess.run(
        command, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    if result.returncode != 0:
        print(f"❌ Error executing: {' '.join(command)}")
        print(f"Error details: {result.stderr.strip()}")
        sys.exit(1)
    else:
        if result.stdout:
            print(result.stdout.strip())


def post_reset_verification(repo_path):
    """Verifies that the history reset was successful both locally and remotely."""
    # failures = 0
    # successes = 0

    # Check local commit count
    local_commit_count = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if local_commit_count.returncode != 0:
        print(f"❌ Error checking local commit count: {local_commit_count.stderr.strip()}")
        sys.exit(1)

    local_count = int(local_commit_count.stdout.strip())
    if local_count != 1:
        print(f"❌ Local verification failed: Expected 1 commit, found {local_count}.")
        sys.exit(1)
    else:
        print("✅ Local verification passed: Only one commit exists.")

    # Check remote commit count
    remote_commit_count = subprocess.run(
        ["git", "rev-list", "--count", "origin/" + BRANCH_NAME],
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if remote_commit_count.returncode != 0:
        print(f"❌ Error checking remote commit count: {remote_commit_count.stderr.strip()}")
        sys.exit(1)

    remote_count = int(remote_commit_count.stdout.strip())
    if remote_count != 1:
        print(f"❌ Remote verification failed: Expected 1 commit, found {remote_count}.")
        sys.exit(1)
    else:
        print("✅ Remote verification passed: Only one commit exists.")


def main():
    print("=== Git Repository History Reset Tool ===\n")

    print("Info:")
    print(
        "⚠️  ATTENTION: This tool will permanently erase your entire Git commit history both locally and remotely."
    )

    # 1. Prerequisites
    print("\nPrerequisites:")
    # Correct OS check
    if not check_correct_OS():
        print("❌ Error: This script is designed to run on Windows.")
        sys.exit(1)
    else:
        print("✅ OS check passed: Running on Windows.")

    # Git installed check
    if not check_git_installed():
        print("❌ Error: Git is not installed or not found in your system's PATH.")
        sys.exit(1)
    else:
        print("✅ Git check passed: Git is installed.")
    print()

    # 2. User Input
    repo_path = input("Enter the absolute path of your local Git repository: ").strip()

    # Strip quotes if the user drags and drops the folder into the terminal
    repo_path = repo_path.strip("'\"")

    # 3. Directory and Permission Validations
    print("\nChecks:")
    if not os.path.exists(repo_path):
        print("❌ Error: The specified path does not exist.")
        sys.exit(1)
    elif not os.path.isdir(repo_path):
        print("❌ Error: The specified path is not a directory.")
        sys.exit(1)
    # elif not os.access(repo_path, os.R_OK):
    #     print("❌ Error: You do not have read permissions for this folder.")
    #     sys.exit(1)
    # elif not os.access(repo_path, os.W_OK):
    #     print("❌ Error: You do not have write permissions for this folder.")
    #     sys.exit(1)
    else:
        print("✅ Directory and permission checks passed.")

    if not is_git_repository(repo_path):
        print("❌ Error: The path is not a valid Git repository (.git folder not found).")
        sys.exit(1)
    else:
        print("✅ Git repository check passed: Valid Git repository found.")

    if not has_dir_write_permission(repo_path):
        print("❌ Error: You do not have write permissions for this folder.")
        sys.exit(1)
    else:
        print("✅ Directory write permission check passed.")

    if not has_repo_write_permission(repo_path):
        print("❌ Error: You do not have write permissions for this Git repository.")
        sys.exit(1)
    else:
        print("✅ Repository write permission check passed.")

    # 4. Remote Validation
    if not check_remote_origin(repo_path):
        print("❌ Error: The 'origin' remote is not configured in this repository.")
        sys.exit(1)
    else:
        print("✅ Remote validation check passed: 'origin' remote is configured.")

    # Final User Confirmation
    print("\nConfirmation:")
    print("⚠️  WARNING: This process will permanently wipe your ENTIRE commit history.")
    confirm = input("Are you sure you want to proceed? (type 'yes' to confirm (yes/NO)): ").strip()
    if confirm.lower() != "yes":
        print("Operation cancelled by user.")
        sys.exit(0)

    # Ask if user wants backup before proceeding
    # (zip with powershell Compress-Archive, including .git folder)
    print("\nBackup:")
    backup_confirm = input(
        "Do you want to create a backup of the current repository before proceeding? (YES/no): "
    ).strip()

    if backup_confirm.lower() in ["yes", "y", ""]:
        # Get dynamic repo slug
        repo_slug = get_repo_slug(repo_path)
        backup_zip_path = os.path.join(BACKUP_DIR, f"{repo_slug}_backup.zip")

        # Check if already exists, if so, ask for overwrite confirmation
        if os.path.exists(backup_zip_path):
            overwrite_confirm = input(
                f"Backup already exists at {backup_zip_path}. Do you want to overwrite it? (YES/no): "
            ).strip()
            if overwrite_confirm.lower() not in ["yes", "y", ""]:
                print("Backup creation skipped. Proceeding without backup.")
            else:
                make_backup(repo_path, repo_slug)
        else:
            make_backup(repo_path, repo_slug)
    else:
        print("⚠️  Warning: No backup will be created. Proceeding without backup.")
    print("-" * 50)

    print("\nStarting the history reset process...\n")

    # 5. Git Command Execution
    # Create orphan branch
    run_git_command(["git", "checkout", "--orphan", "latest_branch"], repo_path)

    # Add all files
    run_git_command(["git", "add", "-A"], repo_path)

    # Create the clean initial commit
    run_git_command(["git", "commit", "-am", COMMIT_MESSAGE], repo_path)

    # Delete the old main branch
    run_git_command(["git", "branch", "-D", BRANCH_NAME], repo_path)

    # Rename current branch to main
    run_git_command(["git", "branch", "-m", BRANCH_NAME], repo_path)

    # Force push to the remote repository
    print("\nUploading changes to the remote server (Force Push)...")
    run_git_command(["git", "push", "-f", "origin", BRANCH_NAME], repo_path)

    # Check locally and remotely if the history has been reset, check if only one commit exists with the specified commit message
    print("\nVerifying the history reset...")
    post_reset_verification(repo_path)

    print("\n✅ History successfully reset both locally and remotely!")


if __name__ == "__main__":
    main()
