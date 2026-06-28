"""Tests for Typer CLI commands."""

from unittest.mock import AsyncMock, patch

from typer.testing import CliRunner

from app.cli import app

runner = CliRunner()


class TestCLIHelp:
    def test_root_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "jobs" in result.output

    def test_jobs_help(self) -> None:
        result = runner.invoke(app, ["jobs", "--help"])
        assert result.exit_code == 0
        assert "fetch-news" in result.output

    def test_db_help(self) -> None:
        result = runner.invoke(app, ["db", "--help"])
        assert result.exit_code == 0


class TestCLIJobs:
    @patch("app.cli._fetch_news", new_callable=AsyncMock)
    def test_fetch_news_command(self, mock_fn: AsyncMock) -> None:
        mock_fn.return_value = 5
        result = runner.invoke(app, ["jobs", "fetch-news"])
        assert result.exit_code == 0
        assert "5" in result.output

    @patch("app.cli._refresh_prices", new_callable=AsyncMock)
    def test_refresh_prices_command(self, mock_fn: AsyncMock) -> None:
        mock_fn.return_value = 3
        result = runner.invoke(app, ["jobs", "refresh-prices"])
        assert result.exit_code == 0
        assert "3" in result.output

    @patch("app.cli._refresh_fx", new_callable=AsyncMock)
    def test_refresh_fx_command(self, mock_fn: AsyncMock) -> None:
        mock_fn.return_value = 2
        result = runner.invoke(app, ["jobs", "refresh-fx"])
        assert result.exit_code == 0
        assert "2" in result.output
