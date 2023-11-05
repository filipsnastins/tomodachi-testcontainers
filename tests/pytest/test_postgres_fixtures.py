from textwrap import dedent

import pytest


def test_postgres_image_name_set_from_envvar(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(
        dedent(
            """\
            import os


            os.environ["POSTGRES_TESTCONTAINER_IMAGE_ID"] = "postgres:15.4-alpine3.18"
            """
        )
    )

    pytester.makepyfile(
        dedent(
            """\
            from tomodachi_testcontainers import PostgreSQLContainer


            def test_postgres_image_name_set_from_envvar(postgres_container: PostgreSQLContainer) -> None:
                assert postgres_container.image == "postgres:15.4-alpine3.18"
            """
        )
    )

    result = pytester.runpytest_subprocess()
    result.assert_outcomes(passed=1)
