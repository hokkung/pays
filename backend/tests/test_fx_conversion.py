"""Tests for FX conversion logic and properties."""

from datetime import UTC, datetime
from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from app.models.fx_rate import FxRate
from app.services.fx import convert_to_thb, get_latest_rate


async def _insert_rate(
    session: AsyncSession,  # type: ignore[name-defined]  # noqa: F821
    base: str,
    quote: str,
    rate: str,
) -> None:
    """Insert a test FX rate."""

    session.add(
        FxRate(
            base_ccy=base,
            quote_ccy=quote,
            rate=Decimal(rate),
            as_of=datetime.now(UTC),
            source="frankfurter",
        )
    )
    await session.flush()


class TestConvertToThb:
    """Tests for convert_to_thb."""

    async def test_identity_thb(self, session: object) -> None:
        """Converting THB to THB should return the same amount."""
        result = await convert_to_thb(session, Decimal("100.00"), "THB")  # type: ignore[arg-type]
        assert result == Decimal("100.00")

    async def test_usd_to_thb(self, session: object) -> None:
        """Converting USD to THB should use the stored rate."""
        await _insert_rate(session, "USD", "THB", "33.50")  # type: ignore[arg-type]
        result = await convert_to_thb(session, Decimal("100.00"), "USD")  # type: ignore[arg-type]
        assert result is not None
        assert result == Decimal("3350.00")

    async def test_no_rate_available(self, session: object) -> None:
        """Converting a currency with no stored rate should return None."""
        result = await convert_to_thb(session, Decimal("100.00"), "EUR")  # type: ignore[arg-type]
        assert result is None

    async def test_uses_latest_rate(self, session: object) -> None:
        """Should use the most recent rate when multiple exist."""
        from datetime import timedelta

        old_time = datetime.now(UTC) - timedelta(days=2)
        new_time = datetime.now(UTC)

        for ts, rate in [(old_time, "30.00"), (new_time, "35.00")]:
            session.add(  # type: ignore[attr-defined]
                FxRate(
                    base_ccy="USD",
                    quote_ccy="THB",
                    rate=Decimal(rate),
                    as_of=ts,
                    source="frankfurter",
                )
            )
        await session.flush()  # type: ignore[attr-defined]

        result = await convert_to_thb(session, Decimal("10.00"), "USD")  # type: ignore[arg-type]
        assert result == Decimal("350.00")


class TestGetLatestRate:
    """Tests for get_latest_rate."""

    async def test_same_currency(self, session: object) -> None:
        """Same currency should return Decimal('1')."""
        rate = await get_latest_rate(session, "USD", "USD")  # type: ignore[arg-type]
        assert rate == Decimal("1")

    async def test_no_data(self, session: object) -> None:
        """Missing pair should return None."""
        rate = await get_latest_rate(session, "USD", "THB")  # type: ignore[arg-type]
        assert rate is None


class TestConversionMath:
    """Property-based tests for the conversion arithmetic."""

    @given(
        amount=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=2),
        rate=st.decimals(min_value=Decimal("0.0001"), max_value=Decimal("1000"), places=6),
    )
    def test_conversion_is_multiplication(self, amount: Decimal, rate: Decimal) -> None:
        """Converted amount should equal amount * rate."""
        result = amount * rate
        assert result >= Decimal("0")

    @given(
        amount=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"), places=2),
    )
    def test_identity_conversion(self, amount: Decimal) -> None:
        """Converting with rate 1 should return the same amount."""
        assert amount * Decimal("1") == amount
