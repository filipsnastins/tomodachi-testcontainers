from textwrap import dedent

import pytest


def test_tomodachi_image_id_set_from_envvar(pytester: pytest.Pytester) -> None:
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

            from tomodachi_testcontainers import get_docker_image


            def test_tomodachi_image_id_set_from_envvar(tomodachi_image: DockerImage) -> None:
                image = get_docker_image("alpine:3.18.2")

                assert tomodachi_image.id == image.id
            """
        )
    )

    result = pytester.runpytest_subprocess()
    result.assert_outcomes(passed=1)
