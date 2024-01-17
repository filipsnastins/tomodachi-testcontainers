from textwrap import dedent

import pytest


def test_minio_image_name_set_from_envvar(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(
        dedent(
            """\
            import os


            os.environ["MINIO_TESTCONTAINER_IMAGE_ID"] = "minio/minio:RELEASE.2023-11-15T20-43-25Z"
            """
        )
    )

    pytester.makepyfile(
        dedent(
            """\
            from tomodachi_testcontainers import MinioContainer


            def test_minio_image_name_set_from_envvar(minio_container: MinioContainer) -> None:
                assert minio_container.image == "minio/minio:RELEASE.2023-11-15T20-43-25Z"
            """
        )
    )

    result = pytester.runpytest_subprocess()
    result.assert_outcomes(passed=1)
