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
            from docker.models.images import Image as DockerImage

            from tomodachi_testcontainers.utils import get_docker_image


            def test_testcontainers_docker_image_set_from_envvar(testcontainers_docker_image: DockerImage) -> None:
                image = get_docker_image("alpine:3.18.2")

                assert testcontainers_docker_image.id == image.id
            """
        )
    )

    result = pytester.runpytest_subprocess()
    result.assert_outcomes(passed=1)
