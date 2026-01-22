import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the app"""
    return TestClient(app)


@pytest.fixture
def reset_activities(client):
    """Reset activities to known state before each test"""
    # This is a simple reset - in a real app, you'd want more sophisticated state management
    yield
    # Cleanup after test if needed


class TestActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that activities response contains expected activity names"""
        response = client.get("/activities")
        activities = response.json()
        expected_activities = [
            "Football Team",
            "Basketball Club",
            "Drama Club",
            "Art Studio",
            "Debate Team",
            "Science Club",
            "Chess Club",
            "Programming Class",
            "Gym Class"
        ]
        for activity in expected_activities:
            assert activity in activities

    def test_activity_structure(self, client):
        """Test that each activity has the required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_returns_200_on_success(self, client):
        """Test that signup returns status 200 on successful registration"""
        response = client.post(
            "/activities/Football Team/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 200

    def test_signup_adds_participant(self, client):
        """Test that signup adds a participant to the activity"""
        email = "newstudent@mergington.edu"
        response = client.post(
            "/activities/Drama Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities = client.get("/activities").json()
        assert email in activities["Drama Club"]["participants"]

    def test_signup_duplicate_returns_400(self, client):
        """Test that duplicate signup returns 400 error"""
        email = "lucas@mergington.edu"
        # First signup should succeed
        response = client.post(
            "/activities/Football Team/signup",
            params={"email": email}
        )
        # Second signup with same email should fail
        response = client.post(
            "/activities/Football Team/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_success_message(self, client):
        """Test that signup returns appropriate success message"""
        email = "success@mergington.edu"
        response = client.post(
            "/activities/Art Studio/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]


class TestRemoveEndpoint:
    """Tests for the POST /activities/{activity_name}/remove endpoint"""

    def test_remove_returns_200_on_success(self, client):
        """Test that remove returns status 200 on successful removal"""
        email = "rachel@mergington.edu"
        response = client.post(
            "/activities/Science Club/remove",
            params={"email": email}
        )
        assert response.status_code == 200

    def test_remove_removes_participant(self, client):
        """Test that remove deletes a participant from the activity"""
        email = "thomas@mergington.edu"
        response = client.post(
            "/activities/Science Club/remove",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities = client.get("/activities").json()
        assert email not in activities["Science Club"]["participants"]

    def test_remove_nonexistent_participant_returns_400(self, client):
        """Test that removing nonexistent participant returns 400"""
        response = client.post(
            "/activities/Football Team/remove",
            params={"email": "nonexistent@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_remove_nonexistent_activity_returns_404(self, client):
        """Test that remove from nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/remove",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_success_message(self, client):
        """Test that remove returns appropriate success message"""
        email = "isabella@mergington.edu"
        response = client.post(
            "/activities/Drama Club/remove",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert email in response.json()["message"]


class TestRootEndpoint:
    """Tests for the GET / endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
