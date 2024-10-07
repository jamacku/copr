from copy import deepcopy
from unittest import mock
from coprs import app
from coprs.repos import (
    generate_repo_url,
    pre_process_repo_url,
    parse_repo_params,
)
from tests.coprs_test_case import CoprsTestCase


class TestRepos(CoprsTestCase):
    def test_generate_repo_url(self):
        test_sets = []

        http_url = "http://example.com/path"
        https_url = "https://example.com/path"

        mock_chroot = mock.MagicMock()
        mock_chroot.os_release = "fedora"
        mock_chroot.os_version = "20"

        # pylint: disable=use-dict-literal
        test_sets.extend([
            dict(args=(mock_chroot, http_url),
                 expected="http://example.com/path/fedora-$releasever-$basearch/"),
            dict(args=(mock_chroot, https_url),
                 expected="https://example.com/path/fedora-$releasever-$basearch/")])

        m2 = deepcopy(mock_chroot)
        m2.os_version = "rawhide"

        test_sets.extend([
            dict(args=(m2, http_url),
                 expected="http://example.com/path/fedora-$releasever-$basearch/"),
            dict(args=(m2, https_url),
                 expected="https://example.com/path/fedora-$releasever-$basearch/")])

        m3 = deepcopy(mock_chroot)
        m3.os_release = "rhel7"
        m3.os_version = "7.1"

        test_sets.extend([
            dict(args=(m3, http_url),
                 expected="http://example.com/path/rhel7-7.1-$basearch/"),
            dict(args=(m3, https_url),
                 expected="https://example.com/path/rhel7-7.1-$basearch/")])

        test_sets.extend([
            dict(args=(m3, http_url, 'i386'),
                 expected="http://example.com/path/rhel7-7.1-i386/"),
            dict(args=(m3, https_url, 'ppc64le'),
                 expected="https://example.com/path/rhel7-7.1-ppc64le/")])

        m4 = deepcopy(mock_chroot)
        m4.os_release = "centos-stream"
        m4.os_version = "9"

        test_sets.extend([
            dict(args=(m4, http_url),
                 expected="http://example.com/path/centos-stream-$releasever-$basearch/"),
            dict(args=(m4, https_url),
                 expected="https://example.com/path/centos-stream-$releasever-$basearch/")])

        app.config["USE_HTTPS_FOR_RESULTS"] = True
        for test_set in test_sets:
            result = generate_repo_url(*test_set["args"])
            assert result == test_set["expected"]

    def test_pre_process_repo_url(self):
        app.config["BACKEND_BASE_URL"] = "http://backend"

        test_cases = [
            ("http://example1.com/foo/$chroot/", "http://example1.com/foo/fedora-rawhide-x86_64/"),
            ("copr://someuser/someproject", "http://backend/results/someuser/someproject/fedora-rawhide-x86_64/"),
            ("copr://someuser/someproject?foo=bar&baz=10",
             "http://backend/results/someuser/someproject/fedora-rawhide-x86_64/"),
            ("http://example1.com/foo/$chroot?priority=10",
             "http://example1.com/foo/fedora-rawhide-x86_64"),
            ("http://example1.com/foo/$chroot?priority=10&foo=bar",
             "http://example1.com/foo/fedora-rawhide-x86_64?foo=bar"),
        ]
        with app.app_context():
            for url, exp in test_cases:
                assert pre_process_repo_url("fedora-rawhide-x86_64", url) == exp

    def test_parse_repo_params(self):
        test_cases = [
            ("copr://foo/bar", {}),
            ("copr://foo/bar?priority=10", {"priority": 10}),
            ("copr://foo/bar?priority=10&unexp1=baz&unexp2=qux", {"priority": 10}),
            ("http://example1.com/foo?priority=10", {"priority": 10}),
        ]
        for repo, exp in test_cases:
            assert parse_repo_params(repo) == exp

    def test_parse_repo_params_pass_keys(self):
        url = "copr://foo/bar?param1=foo&param2=bar&param3=baz&param4=qux"
        supported = ["param1", "param2", "param4"]
        expected = {"param1": "foo", "param2": "bar", "param4": "qux"}
        assert parse_repo_params(url, supported_keys=supported) == expected
