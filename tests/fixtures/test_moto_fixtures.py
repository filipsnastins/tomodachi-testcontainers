from textwrap import dedent

import pytest


def test_moto_image_name_set_from_envvar(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(
        dedent(
            """\
            import os


            os.environ["MOTO_TESTCONTAINER_IMAGE_ID"] = "motoserver/moto:5.0.6"
            """
        )
    )

    pytester.makepyfile(
        dedent(
            """\
            from tomodachi_testcontainers import MotoContainer


            def test_moto_image_name_set_from_envvar(moto_container: MotoContainer) -> None:
                assert moto_container.image == "motoserver/moto:5.0.6"
            """
        )
    )

    result = pytester.runpytest_subprocess()
    result.assert_outcomes(passed=1)
