from textwrap import dedent

import pytest


def test_testcontainer_image_set_from_envvar(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(
        dedent(
            """\
            import os


            os.environ["TESTCONTAINER_IMAGE_ID"] = "alpine:3.18.2"
            """
        )
    )

    pytester.makepyfile(
        dedent(
            """\
            def test_testcontainer_image_set_from_envvar(testcontainer_image: str) -> None:
                assert testcontainer_image == "alpine:3.18.2"
            """
        )
    )

    result = pytester.runpytest_subprocess()
    result.assert_outcomes(passed=1)
