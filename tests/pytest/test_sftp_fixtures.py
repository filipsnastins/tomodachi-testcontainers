from textwrap import dedent

import pytest

from tomodachi_testcontainers import SFTPContainer


def test_default_sftp_image(sftp_container: SFTPContainer) -> None:
    assert sftp_container.image == "atmoz/sftp:latest"


def test_sftp_image_name_set_from_envvar(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(
        dedent(
            """\
            import os


            os.environ["SFTP_TESTCONTAINER_IMAGE_ID"] = "atmoz/sftp:alpine-3.4"
            """
        )
    )

    pytester.makepyfile(
        dedent(
            """\
            from tomodachi_testcontainers import SFTPContainer


            def test_sftp_image_name_set_from_envvar(sftp_container: SFTPContainer) -> None:
                assert sftp_container.image == "atmoz/sftp:alpine-3.4"
            """
        )
    )

    result = pytester.runpytest_subprocess()
    result.assert_outcomes(passed=1)
