import pytest

from tomodachi_testcontainers.async_probes import probe_during_interval, probe_until


class TestProbeUntil:
    @pytest.mark.asyncio(loop_scope="session")
    async def test_fails_and_reraises_exception(self) -> None:
        def _f() -> None:
            raise ValueError("Something went wrong")

        with pytest.raises(ValueError, match="Something went wrong"):
            await probe_until(_f, probe_interval=0.1, stop_after=0.3)

    @pytest.mark.asyncio(loop_scope="session")
    async def test_passes(self) -> None:
        def _f() -> bool:
            return True

        result = await probe_until(_f, probe_interval=0.1, stop_after=0.3)

        assert result is True

    @pytest.mark.asyncio(loop_scope="session")
    async def test_with_asynchronous_function(self) -> None:
        async def _f() -> bool:
            return True

        result = await probe_until(_f, probe_interval=0.1, stop_after=0.3)

        assert result is True

    @pytest.mark.asyncio(loop_scope="session")
    async def test_with_lambda_returning_coroutine(self) -> None:
        async def _f() -> bool:
            return True

        result = await probe_until(
            lambda: _f(), probe_interval=0.1, stop_after=0.3  # pylint: disable=unnecessary-lambda
        )

        assert result is True

    @pytest.mark.asyncio(loop_scope="session")
    async def test_recovers_after_failure(self) -> None:
        attempts = [False, False, True]

        def _f() -> None:
            assert attempts.pop(0)

        await probe_until(_f, probe_interval=0.1, stop_after=0.3)

    @pytest.mark.asyncio(loop_scope="session")
    async def test_timeout_reached(self) -> None:
        attempts = [False, False, False, False, True]

        def _f() -> None:
            assert attempts.pop(0)

        with pytest.raises(AssertionError, match="assert False"):
            await probe_until(_f, probe_interval=0.1, stop_after=0.3)


class TestProbeDuringInterval:
    @pytest.mark.asyncio(loop_scope="session")
    async def test_runs_until_timeout_reached_and_passes(self) -> None:
        attempts = [True, True, True, True]
        attempt = len(attempts)

        def _f() -> bool:
            nonlocal attempt
            assert len(attempts) == attempt
            assert attempts.pop(0)
            attempt -= 1
            return True

        result = await probe_during_interval(_f, probe_interval=0.1, stop_after=0.3)

        assert result is True

    @pytest.mark.asyncio(loop_scope="session")
    async def test_with_asynchronous_function(self) -> None:
        async def _f() -> bool:
            return True

        result = await probe_during_interval(_f, probe_interval=0.1, stop_after=0.3)

        assert result is True

    @pytest.mark.asyncio(loop_scope="session")
    async def test_with_lambda_returning_coroutine(self) -> None:
        async def _f() -> bool:
            return True

        result = await probe_during_interval(
            lambda: _f(), probe_interval=0.1, stop_after=0.3  # pylint: disable=unnecessary-lambda
        )

        assert result is True

    @pytest.mark.asyncio(loop_scope="session")
    async def test_fails_with_assertion_error(self) -> None:
        attempts = [True, True, False, True]

        def _f() -> None:
            assert attempts.pop(0)

        with pytest.raises(AssertionError, match="assert False"):
            await probe_during_interval(_f, probe_interval=0.1, stop_after=0.5)

    @pytest.mark.asyncio(loop_scope="session")
    async def test_fails_with_other_exceptions(self) -> None:
        attempts = [True, True, False, True]

        def _f() -> None:
            if attempts.pop(0) is False:
                raise ValueError("Something went wrong")

        with pytest.raises(ValueError, match="Something went wrong"):
            await probe_during_interval(_f, probe_interval=0.1, stop_after=0.5)
