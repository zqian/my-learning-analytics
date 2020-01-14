import logging, os, HttpRequest

from django.conf import settings
from django.contrib.flatpages.models import FlatPage

from dashboard.common.db_util import get_user_courses_info

from typing import Dict, Optional

logger = logging.getLogger(__name__)


def format_github_url_using_https(github_url: str) -> str:
    ssh_base = "git@"
    https_base = "https://"
    # If the URL is formatted for SSH, convert, otherwise, do nothing
    if ssh_base == github_url[:len(ssh_base)]:
        github_url = github_url.replace(":", "/").replace(".git", "").replace(ssh_base, https_base)
    return github_url


def get_git_version_info() -> Dict[str, str]:
    logger.debug(get_git_version_info.__name__)

    commit = os.getenv("GIT_COMMIT", "")
    if commit != "":
        commit_abbrev = commit[:settings.SHA_ABBREV_LENGTH]
    else:
        commit_abbrev = ""

    # Only include the branch name and not remote info
    branch = os.getenv("GIT_BRANCH", "").split('/')[-1]

    git_version = {
        "repo": format_github_url_using_https(os.getenv("GIT_REPO", "")),
        "commit": commit,
        "commit_abbrev": commit_abbrev,
        "branch": branch
    }
    return git_version


def search_key_for_resource_value(my_dict: Dict, search_for:str) -> Optional[str]:
    for key, value in my_dict.items():
        for resource_types in value["types"]:
            if search_for in resource_types:
                return key
    return None


def get_myla_globals(current_user: HttpRequest.user) -> Dict[str, str] :
    username = ""
    user_courses_info = []
    login_url = ""
    logout_url = ""
    google_analytics_id = ""

    is_superuser = current_user.is_superuser
    if current_user.is_authenticated:
        username = current_user.get_username()
        user_courses_info = get_user_courses_info(username)

    if settings.LOGIN_URL:
        login_url = settings.LOGIN_URL
    if settings.LOGOUT_URL:
        logout_url = settings.LOGOUT_URL
    if settings.GA_ID:
        google_analytics_id = settings.GA_ID
    flatpages = FlatPage.objects.all()
    if flatpages:
        help_url = flatpages[0].content
    else:
        help_url = "https://sites.google.com/umich.edu/my-learning-analytics-help/home"

    myla_globals = {
        "username" : username,
        "is_superuser": is_superuser,
        "user_courses_info": user_courses_info,
        "login": login_url,
        "logout": logout_url,
        "google_analytics_id": google_analytics_id,
        "help_url": help_url
    }
    return myla_globals
