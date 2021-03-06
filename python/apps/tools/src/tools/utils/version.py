"""Versioning utility functions."""
import subprocess
import pkg_resources


def git_version():
    """Retrieve version of source code repository as git describe long output."""
    try:
        version = subprocess.check_output(["git", "describe", "--long"],
                                          encoding='UTF-8', stderr=subprocess.DEVNULL) \
            .strip().replace('-', '.')
    except subprocess.CalledProcessError:
        version = "0.0.1.dev1"
    return version


def package_version(package):
    """Retrieve python package version."""
    try:
        version = pkg_resources.get_distribution(package).version
    except pkg_resources.DistributionNotFound:
        version = "0.0.1.dev1"
    return version
