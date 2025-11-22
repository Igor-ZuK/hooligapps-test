from datetime import date
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest

from project.core.uc.history.dto import SubmitFormRequest
from project.core.uc.history.submit_form import SubmitForm

_path_to_tested = "project.core.uc.history.submit_form"


class TestSubmitForm:
    @pytest.mark.asyncio
    @patch(f"{_path_to_tested}.asyncio.sleep")
    async def test_success(self, sleep_mock):
        """Test successful form submission."""
        dal_mock = AsyncMock()
        uc = SubmitForm(form_history_dal=dal_mock)

        request = SubmitFormRequest(
            date=date(2025, 1, 15),
            first_name="Ivan",
            last_name="Ivanov",
        )

        result = await uc.execute(request)

        assert result.success is True
        assert not result.has_errors()
        sleep_mock.assert_called_once()
        dal_mock.create_form_entry.assert_awaited_once_with(
            date=date(2025, 1, 15),
            first_name="Ivan",
            last_name="Ivanov",
        )

    @pytest.mark.asyncio
    @patch(f"{_path_to_tested}.asyncio.sleep")
    async def test_validation_error_first_name_whitespace(self, sleep_mock):
        """Test validation error when first_name contains whitespace."""
        dal_mock = AsyncMock()
        uc = SubmitForm(form_history_dal=dal_mock)

        request = SubmitFormRequest(
            date=date(2025, 1, 15),
            first_name="Ivan Ivanov",  # Contains whitespace
            last_name="Ivanov",
        )

        result = await uc.execute(request)

        assert result.success is False
        assert result.has_errors()
        assert len(result.errors) == 1
        assert "first_name" in str(result.errors[0]).lower()
        sleep_mock.assert_called_once()
        dal_mock.create_form_entry.assert_not_awaited()

    @pytest.mark.asyncio
    @patch(f"{_path_to_tested}.asyncio.sleep")
    async def test_validation_error_last_name_whitespace(self, sleep_mock):
        """Test validation error when last_name contains whitespace."""
        dal_mock = AsyncMock()
        uc = SubmitForm(form_history_dal=dal_mock)

        request = SubmitFormRequest(
            date=date(2025, 1, 15),
            first_name="Ivan",
            last_name="Ivanov Petrov",  # Contains whitespace
        )

        result = await uc.execute(request)

        assert result.success is False
        assert result.has_errors()
        assert len(result.errors) == 1
        assert "last_name" in str(result.errors[0]).lower()
        sleep_mock.assert_called_once()
        dal_mock.create_form_entry.assert_not_awaited()

    @pytest.mark.asyncio
    @patch(f"{_path_to_tested}.asyncio.sleep")
    async def test_validation_error_both_names_whitespace(self, sleep_mock):
        """Test validation error when both names contain whitespace."""
        dal_mock = AsyncMock()
        uc = SubmitForm(form_history_dal=dal_mock)

        request = SubmitFormRequest(
            date=date(2025, 1, 15),
            first_name="Ivan Ivanov",  # Contains whitespace
            last_name="Petrov Smith",  # Contains whitespace
        )

        result = await uc.execute(request)

        assert result.success is False
        assert result.has_errors()
        assert len(result.errors) == 2
        sleep_mock.assert_called_once()
        dal_mock.create_form_entry.assert_not_awaited()

    @pytest.mark.asyncio
    @patch(f"{_path_to_tested}.asyncio.sleep")
    async def test_delay_simulation(self, sleep_mock):
        """Test that delay is simulated."""
        dal_mock = AsyncMock()
        uc = SubmitForm(form_history_dal=dal_mock)

        request = SubmitFormRequest(
            date=date(2025, 1, 15),
            first_name="Ivan",
            last_name="Ivanov",
        )

        await uc.execute(request)

        # Verify sleep was called (delay simulation)
        sleep_mock.assert_called_once()
        # Verify delay is between 0 and 3 seconds
        call_args = sleep_mock.call_args[0][0]
        assert 0 <= call_args <= 3
