"""GitHub Helper Functions"""
import os
import subprocess


def git_checkout_parent(repo_owner, repo_name, commit_sha, clone_path=None):
    """
    Checkouts the parent commit of a target commit (vulnerable commit from patch link)
    :param repo_owner: Owner of GitHub repo
    :param repo_name: Name of GitHub repo, saved folder in the repos path
    :param commit_sha: Target commit from a patch link
    :param clone_path: Custom directory
    :return: None
    """
    if clone_path == None:
        """Set paths"""
        working_directory = os.getcwd()
        clone_path = f"{working_directory}/github/repos/"

    """Set parent commit"""
    parent_commit_sha = f"{commit_sha}^"

    """Generate commands"""
    if clone_path == None:
        change_directory = f"cd {clone_path}{repo_owner}/{repo_name}"
    else:
        change_directory = f"cd {clone_path}"
    checkout_command = f"git checkout {parent_commit_sha}"

    """
    Changes to the directory and runs a git checkout of parent commit
    Input is trusted, and fails when shell=False
    """
    subprocess.run(f"{change_directory}; {checkout_command}", shell=True)


def git_checkout_target(repo_owner, repo_name, commit_sha, clone_path=None):
    """
    Checkouts the target commit (non-vulnerable commit from patch link)
    :param repo_owner: Owner of GitHub repo
    :param repo_name: Name of GitHub repo, saved folder in the repos path
    :param commit_sha: Target commit from a patch link
    :return: None
    """
    if clone_path == None:
        """Set paths"""
        working_directory = os.getcwd()
        clone_path = f"{working_directory}/github/repos/"

    """Generate commands"""
    if clone_path == None:
        change_directory = f"cd {clone_path}{repo_owner}/{repo_name}"
    else:
        change_directory = f"cd {clone_path}"
    checkout_command = f"git checkout {commit_sha}"

    """
    Changes to the directory and runs a git checkout of parent commit
    Input is trusted, and fails when shell=False
    """
    subprocess.run(f"{change_directory}; {checkout_command}", shell=True)