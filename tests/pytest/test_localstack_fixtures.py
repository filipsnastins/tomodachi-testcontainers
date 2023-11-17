from textwrap import dedent

import pytest


def test_localstack_image_name_set_from_envvar(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(
        dedent(
            """\
            import os


            os.environ["LOCALSTACK_TESTCONTAINER_IMAGE_ID"] = "localstack/localstack:2.3"
            """
        )
    )

    pytester.makepyfile(
        dedent(
            """\
            from tomodachi_testcontainers import LocalStackContainer


            def test_localstack_image_name_set_from_envvar(localstack_container: LocalStackContainer) -> None:
                assert localstack_container.image == "localstack/localstack:2.3"
            """
        )
    )

    result = pytester.runpytest_subprocess()
    result.assert_outcomes(passed=1)
