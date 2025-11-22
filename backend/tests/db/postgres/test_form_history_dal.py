from datetime import date

import pytest

from project.core.db.postgres.form_history import FormHistoryDAL
from tests.conftest import get_async_session


class TestFormHistoryDAL:
    @pytest.mark.asyncio
    async def test_create_form_entry(self, sync_session):
        """Test creating form history entry."""
        async_session = get_async_session()
        async with await async_session.__anext__() as session:
            dal = FormHistoryDAL(session=session)
            test_date = date(2025, 1, 15)
            test_first_name = "Ivan"
            test_last_name = "Ivanov"

            entry = await dal.create_form_entry(
                date=test_date,
                first_name=test_first_name,
                last_name=test_last_name,
            )

            assert entry.date == test_date
            assert entry.first_name == test_first_name
            assert entry.last_name == test_last_name
            assert entry.id is not None
            assert entry.created_at is not None
            assert entry.updated_at is not None

            # Verify entry can be retrieved
            entry_from_db = await dal.get_by_id(entry.id)
            assert entry_from_db.date == test_date
            assert entry_from_db.first_name == test_first_name
            assert entry_from_db.last_name == test_last_name

    @pytest.mark.asyncio
    async def test_get_filtered_history(self, sync_session):
        """Test filtering history by date, first_name, last_name."""
        async_session = get_async_session()
        async with await async_session.__anext__() as session:
            dal = FormHistoryDAL(session=session)

            # Create test data
            await dal.create_form_entry(date=date(2025, 1, 10), first_name="Ivan", last_name="Ivanov")
            await dal.create_form_entry(date=date(2025, 1, 15), first_name="Ivan", last_name="Ivanov")
            await dal.create_form_entry(date=date(2025, 1, 20), first_name="John", last_name="Smith")
            await dal.create_form_entry(date=date(2025, 1, 25), first_name="Ivan", last_name="Petrov")

            # Test filter by date only
            results = await dal.get_filtered_history(date_filter=date(2025, 1, 15))
            assert len(results) == 2
            assert all(r.date <= date(2025, 1, 15) for r in results)

            # Test filter by date and first_name
            results = await dal.get_filtered_history(date_filter=date(2025, 1, 20), first_name="Ivan")
            assert len(results) == 2
            assert all(r.first_name == "Ivan" for r in results)
            assert all(r.date <= date(2025, 1, 20) for r in results)

            # Test filter by date, first_name and last_name
            results = await dal.get_filtered_history(
                date_filter=date(2025, 1, 20), first_name="Ivan", last_name="Ivanov"
            )
            assert len(results) == 2
            assert all(r.first_name == "Ivan" and r.last_name == "Ivanov" for r in results)

    @pytest.mark.asyncio
    async def test_get_filtered_history_limit(self, sync_session):
        """Test that limit works correctly."""
        async_session = get_async_session()
        async with await async_session.__anext__() as session:
            dal = FormHistoryDAL(session=session)

            # Create more than 10 entries
            for i in range(15):
                await dal.create_form_entry(date=date(2025, 1, 1 + i), first_name=f"Name{i}", last_name="Test")

            results = await dal.get_filtered_history(date_filter=date(2025, 1, 20), limit=10)
            assert len(results) == 10

    @pytest.mark.asyncio
    async def test_get_filtered_history_ordering(self, sync_session):
        """Test that results are ordered correctly."""
        async_session = get_async_session()
        async with await async_session.__anext__() as session:
            dal = FormHistoryDAL(session=session)

            await dal.create_form_entry(date=date(2025, 1, 10), first_name="B", last_name="B")
            await dal.create_form_entry(date=date(2025, 1, 15), first_name="A", last_name="A")
            await dal.create_form_entry(date=date(2025, 1, 15), first_name="A", last_name="B")
            await dal.create_form_entry(date=date(2025, 1, 20), first_name="A", last_name="A")

            results = await dal.get_filtered_history(date_filter=date(2025, 1, 20))

            # Should be ordered by date desc, then first_name asc, then last_name asc
            assert results[0].date == date(2025, 1, 20)
            assert results[1].date == date(2025, 1, 15)
            assert results[1].first_name == "A"
            assert results[1].last_name == "A"
            assert results[2].date == date(2025, 1, 15)
            assert results[2].first_name == "A"
            assert results[2].last_name == "B"

    @pytest.mark.asyncio
    async def test_count_filtered_history(self, sync_session):
        """Test counting filtered history entries."""
        async_session = get_async_session()
        async with await async_session.__anext__() as session:
            dal = FormHistoryDAL(session=session)

            # Create test data
            await dal.create_form_entry(date=date(2025, 1, 10), first_name="Ivan", last_name="Ivanov")
            await dal.create_form_entry(date=date(2025, 1, 15), first_name="Ivan", last_name="Ivanov")
            await dal.create_form_entry(date=date(2025, 1, 20), first_name="John", last_name="Smith")
            await dal.create_form_entry(date=date(2025, 1, 25), first_name="Ivan", last_name="Petrov")

            # Count all entries up to date
            count = await dal.count_filtered_history(date_filter=date(2025, 1, 20))
            assert count == 3

            # Count with first_name filter
            count = await dal.count_filtered_history(date_filter=date(2025, 1, 20), first_name="Ivan")
            assert count == 2

            # Count with first_name and last_name filter
            count = await dal.count_filtered_history(
                date_filter=date(2025, 1, 20), first_name="Ivan", last_name="Ivanov"
            )
            assert count == 2

    @pytest.mark.asyncio
    async def test_count_previous_entries(self, sync_session):
        """Test counting previous entries with same name combination."""
        async_session = get_async_session()
        async with await async_session.__anext__() as session:
            dal = FormHistoryDAL(session=session)

            # Create entries for same person on different dates
            await dal.create_form_entry(date=date(2025, 1, 10), first_name="Ivan", last_name="Ivanov")
            await dal.create_form_entry(date=date(2025, 1, 15), first_name="Ivan", last_name="Ivanov")
            await dal.create_form_entry(date=date(2025, 1, 20), first_name="Ivan", last_name="Ivanov")
            await dal.create_form_entry(date=date(2025, 1, 12), first_name="John", last_name="Smith")

            # Count previous entries for entry on 2025-01-20
            count = await dal.count_previous_entries(
                record_date=date(2025, 1, 20), first_name="Ivan", last_name="Ivanov"
            )
            assert count == 2

            # Count previous entries for entry on 2025-01-15
            count = await dal.count_previous_entries(
                record_date=date(2025, 1, 15), first_name="Ivan", last_name="Ivanov"
            )
            assert count == 1

            # Count previous entries for entry on 2025-01-10 (first entry)
            count = await dal.count_previous_entries(
                record_date=date(2025, 1, 10), first_name="Ivan", last_name="Ivanov"
            )
            assert count == 0

            # Count for different person
            count = await dal.count_previous_entries(
                record_date=date(2025, 1, 20), first_name="John", last_name="Smith"
            )
            assert count == 1  # There is one entry on 2025-01-12 before 2025-01-20

    @pytest.mark.asyncio
    async def test_get_unique_first_names(self, sync_session):
        """Test getting unique first names."""
        async_session = get_async_session()
        async with await async_session.__anext__() as session:
            dal = FormHistoryDAL(session=session)

            await dal.create_form_entry(date=date(2025, 1, 10), first_name="Ivan", last_name="Ivanov")
            await dal.create_form_entry(date=date(2025, 1, 15), first_name="Ivan", last_name="Petrov")
            await dal.create_form_entry(date=date(2025, 1, 20), first_name="John", last_name="Smith")

            unique_names = await dal.get_unique_first_names()
            assert set(unique_names) == {"Ivan", "John"}

    @pytest.mark.asyncio
    async def test_get_unique_last_names(self, sync_session):
        """Test getting unique last names."""
        async_session = get_async_session()
        async with await async_session.__anext__() as session:
            dal = FormHistoryDAL(session=session)

            await dal.create_form_entry(date=date(2025, 1, 10), first_name="Ivan", last_name="Ivanov")
            await dal.create_form_entry(date=date(2025, 1, 15), first_name="John", last_name="Ivanov")
            await dal.create_form_entry(date=date(2025, 1, 20), first_name="Jane", last_name="Smith")

            unique_names = await dal.get_unique_last_names()
            assert set(unique_names) == {"Ivanov", "Smith"}
