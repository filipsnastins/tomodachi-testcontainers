from textwrap import dedent

import pytest


def test_wiremock_image_name_set_from_envvar(pytester: pytest.Pytester) -> None:
    pytester.makeconftest(
        dedent(
            """\
            import os


            os.environ["WIREMOCK_TESTCONTAINER_IMAGE_ID"] = "wiremock/wiremock:3.3.1-1"
            os.environ["WIREMOCK_TESTCONTAINER_MAPPING_STUBS"] = ""
            os.environ["WIREMOCK_TESTCONTAINER_MAPPING_FILES"] = ""
            """
        )
    )

    pytester.makepyfile(
        dedent(
            """\
            from tomodachi_testcontainers import WireMockContainer


            def test_wiremock_image_name_set_from_envvar(wiremock_container: WireMockContainer) -> None:
                assert wiremock_container.image == "wiremock/wiremock:3.3.1-1"
            """
        )
    )

    result = pytester.runpytest_subprocess()
    result.assert_outcomes(passed=1)
