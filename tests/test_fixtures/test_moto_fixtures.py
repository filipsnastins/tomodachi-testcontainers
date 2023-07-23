from textwrap import dedent

import pytest

from tomodachi_testcontainers.containers import MotoContainer


def test_default_moto_image(moto_container: MotoContainer) -> None:
    assert moto_container.image == "motoserver/moto:latest"


def test_moto_image_name_set_from_envvar(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(
        dedent(
            """\
            import os

            from testcontainers.core.docker_client import DockerClient


            DockerClient().client.images.pull("motoserver/moto:4.1.0")
            os.environ["MOTO_TESTCONTAINER_IMAGE_ID"] = "motoserver/moto:4.1.0"
            """
        )
    )

    pytester.makepyfile(
        dedent(
            """\
            from tomodachi_testcontainers.containers import MotoContainer


            def test_moto_image_name_set_from_envvar(moto_container: MotoContainer) -> None:
                assert moto_container.image == "motoserver/moto:4.1.0"
            """
        )
    )

    result = pytester.runpytest_subprocess()
    result.assert_outcomes(passed=1)
