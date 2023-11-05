from textwrap import dedent

import pytest


def test_mysql_image_name_set_from_envvar(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(
        dedent(
            """\
            import os


            os.environ["MYSQL_TESTCONTAINER_IMAGE_ID"] = "mysql:8.2.0"
            """
        )
    )

    pytester.makepyfile(
        dedent(
            """\
            from tomodachi_testcontainers import MySQLContainer


            def test_localstack_image_name_set_from_envvar(mysql_container: MySQLContainer) -> None:
                assert mysql_container.image == "mysql:8.2.0"
            """
        )
    )

    result = pytester.runpytest_subprocess()
    result.assert_outcomes(passed=1)
