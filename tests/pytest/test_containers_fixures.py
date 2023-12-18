from textwrap import dedent

import pytest


def test_testcontainers_docker_image_set_from_envvar(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(
        dedent(
            """\
            import os


            os.environ["TOMODACHI_TESTCONTAINER_IMAGE_ID"] = "alpine:3.18.2"
            """
        )
    )

    pytester.makepyfile(
        dedent(
            """\
            def test_testcontainers_docker_image_set_from_envvar(testcontainers_docker_image: str) -> None:
                assert testcontainers_docker_image == "alpine:3.18.2"
            """
        )
    )

    result = pytester.runpytest_subprocess()
    result.assert_outcomes(passed=1)
