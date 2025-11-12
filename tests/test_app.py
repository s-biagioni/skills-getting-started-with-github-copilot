import pytest
from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_dict(self):
        """Test that /activities endpoint returns a dictionary"""
        response = client.get("/activities")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that response contains expected activity names"""
        response = client.get("/activities")
        activities = response.json()
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Theater Club",
            "Debate Team",
            "Science Club",
        ]
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        required_fields = ["description", "schedule", "max_participants", "participants"]

        for activity_name, activity_details in activities.items():
            for field in required_fields:
                assert field in activity_details, f"Missing field '{field}' in {activity_name}"


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_activity_not_found(self):
        """Test signup fails when activity doesn't exist"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_student(self):
        """Test signup fails when student is already registered"""
        email = "duplicate_test@mergington.edu"
        activity = "Chess%20Club"

        # First signup should succeed
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200

        # Second signup with same email should fail
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_updates_participant_count(self):
        """Test that signup updates the participant list"""
        email = "counttest@mergington.edu"
        activity = "Tennis%20Club"

        # Get initial participant count
        response_before = client.get("/activities")
        initial_count = len(response_before.json()["Tennis Club"]["participants"])

        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")

        # Get updated participant count
        response_after = client.get("/activities")
        updated_count = len(response_after.json()["Tennis Club"]["participants"])

        assert updated_count == initial_count + 1
        assert email in response_after.json()["Tennis Club"]["participants"]


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self):
        """Test successful unregister from an activity"""
        email = "unregister_test@mergington.edu"
        activity = "Basketball%20Team"

        # First, sign up the student
        client.post(f"/activities/{activity}/signup?email={email}")

        # Then unregister
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_activity_not_found(self):
        """Test unregister fails when activity doesn't exist"""
        response = client.post(
            "/activities/NonexistentActivity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_student_not_registered(self):
        """Test unregister fails when student isn't registered"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        email = "removal_test@mergington.edu"
        activity = "Art%20Studio"

        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")

        # Verify they are registered
        response_before = client.get("/activities")
        assert email in response_before.json()["Art Studio"]["participants"]

        # Unregister
        client.post(f"/activities/{activity}/unregister?email={email}")

        # Verify they are no longer registered
        response_after = client.get("/activities")
        assert email not in response_after.json()["Art Studio"]["participants"]
