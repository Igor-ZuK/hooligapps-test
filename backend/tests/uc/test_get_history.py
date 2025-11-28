from datetime import date
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from project.core.db.postgres.models import FormHistory
from project.core.uc.history.dto import GetHistoryRequest
from project.core.uc.history.dto import HistoryItem
from project.core.uc.history.get_history import GetHistory


class TestGetHistory:
    @pytest.mark.asyncio
    async def test_success_without_filters(self):
        """Test getting history without name filters."""
        dal_mock = AsyncMock()
        uc = GetHistory(form_history_dal=dal_mock)

        mock_record1 = MagicMock(spec=FormHistory)
        mock_record1.date = date(2025, 1, 20)
        mock_record1.first_name = "Ivan"
        mock_record1.last_name = "Ivanov"

        mock_record2 = MagicMock(spec=FormHistory)
        mock_record2.date = date(2025, 1, 15)
        mock_record2.first_name = "John"
        mock_record2.last_name = "Smith"

        # New method returns tuples: (record, count)
        mock_records_with_counts = [
            (mock_record1, 0),
            (mock_record2, 0),
        ]

        dal_mock.get_filtered_history_with_counts.return_value = mock_records_with_counts
        dal_mock.count_filtered_history.return_value = 2

        request = GetHistoryRequest(date_filter=date(2025, 1, 20))

        result = await uc.execute(request)

        assert result.total == 2
        assert len(result.items) == 2
        assert isinstance(result.items[0], HistoryItem)
        assert result.items[0].date == date(2025, 1, 20)
        assert result.items[0].first_name == "Ivan"
        assert result.items[0].count == 0

        dal_mock.get_filtered_history_with_counts.assert_awaited_once_with(
            date_filter=date(2025, 1, 20),
            first_name=None,
            last_name=None,
            limit=10,
        )
        dal_mock.count_filtered_history.assert_awaited_once_with(
            date_filter=date(2025, 1, 20),
            first_name=None,
            last_name=None,
        )

    @pytest.mark.asyncio
    async def test_success_with_first_name_filter(self):
        """Test getting history with first_name filter."""
        dal_mock = AsyncMock()
        uc = GetHistory(form_history_dal=dal_mock)

        mock_record = MagicMock(spec=FormHistory)
        mock_record.date = date(2025, 1, 20)
        mock_record.first_name = "Ivan"
        mock_record.last_name = "Ivanov"

        # New method returns tuples: (record, count)
        mock_records_with_counts = [(mock_record, 2)]

        dal_mock.get_filtered_history_with_counts.return_value = mock_records_with_counts
        dal_mock.count_filtered_history.return_value = 1

        request = GetHistoryRequest(date_filter=date(2025, 1, 20), first_name="Ivan")

        result = await uc.execute(request)

        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].first_name == "Ivan"
        assert result.items[0].count == 2

        dal_mock.get_filtered_history_with_counts.assert_awaited_once_with(
            date_filter=date(2025, 1, 20),
            first_name="Ivan",
            last_name=None,
            limit=10,
        )

    @pytest.mark.asyncio
    async def test_success_with_all_filters(self):
        """Test getting history with all filters."""
        dal_mock = AsyncMock()
        uc = GetHistory(form_history_dal=dal_mock)

        mock_record = MagicMock(spec=FormHistory)
        mock_record.date = date(2025, 1, 20)
        mock_record.first_name = "Ivan"
        mock_record.last_name = "Ivanov"

        # New method returns tuples: (record, count)
        mock_records_with_counts = [(mock_record, 3)]

        dal_mock.get_filtered_history_with_counts.return_value = mock_records_with_counts
        dal_mock.count_filtered_history.return_value = 1

        request = GetHistoryRequest(
            date_filter=date(2025, 1, 20),
            first_name="Ivan",
            last_name="Ivanov",
        )

        result = await uc.execute(request)

        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].count == 3

        dal_mock.get_filtered_history_with_counts.assert_awaited_once_with(
            date_filter=date(2025, 1, 20),
            first_name="Ivan",
            last_name="Ivanov",
            limit=10,
        )

    @pytest.mark.asyncio
    async def test_get_filtered_history_with_counts_called_once(self):
        """Test that get_filtered_history_with_counts is called once (no N+1)."""
        dal_mock = AsyncMock()
        uc = GetHistory(form_history_dal=dal_mock)

        mock_record1 = MagicMock(spec=FormHistory)
        mock_record1.date = date(2025, 1, 20)
        mock_record1.first_name = "Ivan"
        mock_record1.last_name = "Ivanov"

        mock_record2 = MagicMock(spec=FormHistory)
        mock_record2.date = date(2025, 1, 15)
        mock_record2.first_name = "John"
        mock_record2.last_name = "Smith"

        # New method returns tuples: (record, count)
        mock_records_with_counts = [
            (mock_record1, 0),
            (mock_record2, 1),
        ]

        dal_mock.get_filtered_history_with_counts.return_value = mock_records_with_counts
        dal_mock.count_filtered_history.return_value = 2

        request = GetHistoryRequest(date_filter=date(2025, 1, 20))

        result = await uc.execute(request)

        # Should be called only once, not N times
        assert dal_mock.get_filtered_history_with_counts.await_count == 1
        assert len(result.items) == 2
        assert result.items[0].count == 0
        assert result.items[1].count == 1
