import tempfile
import git


def clone_repo(repo_url: str):
    temp_dir = tempfile.mkdtemp()
    git.Repo.clone_from(repo_url, temp_dir)
    return temp_dir
