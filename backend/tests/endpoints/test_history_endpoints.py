from datetime import date
from http import HTTPStatus
from unittest.mock import AsyncMock

from project.apps.history.api.v1.dependencies import get_history_uc
from project.apps.history.api.v1.dependencies import get_submit_form_uc
from project.core.application import _app
from project.core.uc.history.dto import GetHistoryResponse
from project.core.uc.history.dto import HistoryItem
from project.core.uc.history.dto import SubmitFormResponse


class TestSubmitForm:
    _url = "/api/submit"

    def test_success(self, client):
        """Test successful form submission."""
        data = self._get_data()
        mocked_uc = self._get_mocked_uc(SubmitFormResponse(success=True))
        _app.dependency_overrides[get_submit_form_uc] = lambda: mocked_uc

        response = client.post(self._url, json=data)

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"success": True}

        _app.dependency_overrides.pop(get_submit_form_uc)

    def test_validation_error_first_name_whitespace(self, client):
        """Test validation error when first_name contains whitespace."""
        data = self._get_data()
        data["first_name"] = "Ivan Ivanov"  # Contains whitespace
        mocked_uc = self._get_mocked_uc(
            SubmitFormResponse(success=False, errors=[ValueError("first_name: No whitespace in first_name is allowed")])
        )
        _app.dependency_overrides[get_submit_form_uc] = lambda: mocked_uc

        response = client.post(self._url, json=data)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        response_data = response.json()
        assert response_data["success"] is False
        assert "error" in response_data
        assert "first_name" in response_data["error"]
        assert len(response_data["error"]["first_name"]) > 0

        _app.dependency_overrides.pop(get_submit_form_uc)

    def test_validation_error_last_name_whitespace(self, client):
        """Test validation error when last_name contains whitespace."""
        data = self._get_data()
        data["last_name"] = "Ivanov Petrov"  # Contains whitespace
        mocked_uc = self._get_mocked_uc(
            SubmitFormResponse(success=False, errors=[ValueError("last_name: No whitespace in last_name is allowed")])
        )
        _app.dependency_overrides[get_submit_form_uc] = lambda: mocked_uc

        response = client.post(self._url, json=data)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        response_data = response.json()
        assert response_data["success"] is False
        assert "error" in response_data
        assert "last_name" in response_data["error"]

        _app.dependency_overrides.pop(get_submit_form_uc)

    def test_validation_error_both_names_whitespace(self, client):
        """Test validation error when both names contain whitespace."""
        data = self._get_data()
        data["first_name"] = "Ivan Ivanov"  # Contains whitespace
        data["last_name"] = "Petrov Smith"  # Contains whitespace
        mocked_uc = self._get_mocked_uc(
            SubmitFormResponse(
                success=False,
                errors=[
                    ValueError("first_name: No whitespace in first_name is allowed"),
                    ValueError("last_name: No whitespace in last_name is allowed"),
                ],
            )
        )
        _app.dependency_overrides[get_submit_form_uc] = lambda: mocked_uc

        response = client.post(self._url, json=data)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        response_data = response.json()
        assert response_data["success"] is False
        assert "error" in response_data
        assert "first_name" in response_data["error"]
        assert "last_name" in response_data["error"]

        _app.dependency_overrides.pop(get_submit_form_uc)

    def test_missing_fields(self, client):
        """Test validation error when required fields are missing."""
        data = {"date": "2025-01-15"}  # Missing first_name and last_name

        response = client.post(self._url, json=data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_invalid_date_format(self, client):
        """Test validation error with invalid date format."""
        data = {
            "date": "invalid-date",
            "first_name": "Ivan",
            "last_name": "Ivanov",
        }

        response = client.post(self._url, json=data)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @staticmethod
    def _get_data():
        return {
            "date": "2025-01-15",
            "first_name": "Ivan",
            "last_name": "Ivanov",
        }

    @staticmethod
    def _get_mocked_uc(mocked_response):
        mock_uc = AsyncMock()
        mock_uc.execute.return_value = mocked_response
        return mock_uc


class TestGetHistory:
    _url = "/api/history"

    def test_success_without_filters(self, client):
        """Test getting history without name filters."""
        mocked_uc = self._get_mocked_uc(
            GetHistoryResponse(
                items=[
                    HistoryItem(date=date(2025, 1, 20), first_name="Ivan", last_name="Ivanov", count=0),
                    HistoryItem(date=date(2025, 1, 15), first_name="John", last_name="Smith", count=0),
                ],
                total=2,
            )
        )
        _app.dependency_overrides[get_history_uc] = lambda: mocked_uc

        response = client.get(f"{self._url}?date=2025-01-20")

        assert response.status_code == HTTPStatus.OK
        response_data = response.json()
        assert "items" in response_data
        assert "total" in response_data
        assert isinstance(response_data["items"], list)
        assert isinstance(response_data["total"], int)
        assert response_data["total"] == 2
        assert len(response_data["items"]) == 2

        _app.dependency_overrides.pop(get_history_uc)

    def test_success_with_first_name_filter(self, client):
        """Test getting history with first_name filter."""
        mocked_uc = self._get_mocked_uc(
            GetHistoryResponse(
                items=[
                    HistoryItem(date=date(2025, 1, 20), first_name="Ivan", last_name="Ivanov", count=0),
                ],
                total=1,
            )
        )
        _app.dependency_overrides[get_history_uc] = lambda: mocked_uc

        response = client.get(f"{self._url}?date=2025-01-20&first_name=Ivan")

        assert response.status_code == HTTPStatus.OK
        response_data = response.json()
        assert all(item["first_name"] == "Ivan" for item in response_data["items"])
        assert response_data["total"] == 1

        _app.dependency_overrides.pop(get_history_uc)

    def test_success_with_all_filters(self, client):
        """Test getting history with all filters."""
        mocked_uc = self._get_mocked_uc(
            GetHistoryResponse(
                items=[
                    HistoryItem(date=date(2025, 1, 20), first_name="Ivan", last_name="Ivanov", count=2),
                ],
                total=1,
            )
        )
        _app.dependency_overrides[get_history_uc] = lambda: mocked_uc

        response = client.get(f"{self._url}?date=2025-01-20&first_name=Ivan&last_name=Ivanov")

        assert response.status_code == HTTPStatus.OK
        response_data = response.json()
        assert all(item["first_name"] == "Ivan" and item["last_name"] == "Ivanov" for item in response_data["items"])
        assert response_data["items"][0]["count"] == 2

        _app.dependency_overrides.pop(get_history_uc)

    def test_missing_date_parameter(self, client):
        """Test error when date parameter is missing."""
        response = client.get(self._url)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_history_response_structure(self, client):
        """Test that history response has correct structure."""
        mocked_uc = self._get_mocked_uc(
            GetHistoryResponse(
                items=[
                    HistoryItem(date=date(2025, 1, 15), first_name="Ivan", last_name="Ivanov", count=0),
                ],
                total=1,
            )
        )
        _app.dependency_overrides[get_history_uc] = lambda: mocked_uc

        response = client.get(f"{self._url}?date=2025-01-20")

        assert response.status_code == HTTPStatus.OK
        response_data = response.json()

        # Check structure
        assert "items" in response_data
        assert "total" in response_data

        if response_data["items"]:
            item = response_data["items"][0]
            assert "date" in item
            assert "first_name" in item
            assert "last_name" in item
            assert "count" in item
            assert isinstance(item["count"], int)

        _app.dependency_overrides.pop(get_history_uc)

    @staticmethod
    def _get_mocked_uc(mocked_response):
        mock_uc = AsyncMock()
        mock_uc.execute.return_value = mocked_response
        return mock_uc
