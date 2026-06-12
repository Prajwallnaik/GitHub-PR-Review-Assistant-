"""Tests for the URL parser utility."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.utils.parser import parse_pr_url


def test_valid_url():
    owner, repo, pr_number = parse_pr_url("https://github.com/octocat/hello-world/pull/42")
    assert owner == "octocat"
    assert repo == "hello-world"
    assert pr_number == 42


def test_valid_url_with_trailing_slash():
    # Regex won't match trailing content, but the base should work
    owner, repo, pr_number = parse_pr_url("https://github.com/owner/repo/pull/1")
    assert owner == "owner"
    assert repo == "repo"
    assert pr_number == 1


def test_http_url():
    owner, repo, pr_number = parse_pr_url("http://github.com/user/project/pull/99")
    assert owner == "user"
    assert repo == "project"
    assert pr_number == 99


def test_invalid_url_no_pull():
    with pytest.raises(ValueError, match="Invalid GitHub PR URL"):
        parse_pr_url("https://github.com/owner/repo/issues/5")


def test_invalid_url_random_string():
    with pytest.raises(ValueError, match="Invalid GitHub PR URL"):
        parse_pr_url("not-a-url-at-all")


def test_invalid_url_empty():
    with pytest.raises(ValueError, match="Invalid GitHub PR URL"):
        parse_pr_url("")
