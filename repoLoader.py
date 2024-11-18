import os
import git
import requests
from configuration import Configuration
import cadocsLogger

logger = cadocsLogger.get_cadocs_logger(__name__)

def get_default_branch(config: Configuration):
    """
    Recupera il branch principale del repository utilizzando l'API di GitHub.
    """
    api_url = f"https://api.github.com/repos/{config.repositoryOwner}/{config.repositoryName}"
    headers = {"Authorization": f"Bearer {config.pat}"}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get("default_branch", "main")  # Fallback su "main" se non trovato
    else:
        logger.error(
            f"Errore nel recupero del branch principale. HTTP {response.status_code}: {response.text}"
        )
        return "main"  # Valore predefinito in caso di errore


def get_repo(config: Configuration):
    """
    Clona o aggiorna il repository locale in base alla configurazione.
    """
    # Percorso del repository locale
    repo_path = config.repositoryPath

    # Determina il branch principale
    default_branch = get_default_branch(config)

    # Riferimento al repository
    repo = None
    if not os.path.exists(repo_path):
        logger.info("Clonazione del repository...")
        repo = git.Repo.clone_from(
            config.repositoryUrl,
            repo_path,
            branch=default_branch,
            progress=Progress(),
            odbt=git.GitCmdObjectDB,
        )
        print()
    else:
        repo = git.Repo(repo_path, odbt=git.GitCmdObjectDB)
        logger.info("Aggiornamento del repository...")
        repo.remotes.origin.fetch()
        repo.git.checkout(default_branch)
        repo.git.pull()

    return repo


class Progress(git.remote.RemoteProgress):
    """
    Classe per mostrare il progresso durante le operazioni Git.
    """
    def update(self, op_code, cur_count, max_count=None, message=""):
        print(self._cur_line, end="\r")
