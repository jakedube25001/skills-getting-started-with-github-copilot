"""
Tests for the High School Management System API

This module contains comprehensive tests for all endpoints and edge cases
using FastAPI's TestClient.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store initial state
    initial_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice and compete in basketball games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Train and play soccer matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
            "max_participants": 22,
            "participants": []
        },
        "Art Club": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Drama Club": {
            "description": "Act in plays and improve theatrical skills",
            "schedule": "Tuesdays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": []
        }
    }
    
    # Reset before test
    activities.clear()
    activities.update(initial_state)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(initial_state)


# ============================================================================
# Tests for GET /
# ============================================================================

class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
    
    def test_root_redirect_follow(self, client):
        """Test that root endpoint redirects and follows to static page"""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200


# ============================================================================
# Tests for GET /activities
# ============================================================================

class TestGetActivitiesEndpoint:
    """Tests for retrieving all activities"""
    
    def test_get_activities_success(self, client, reset_activities):
        """Test successfully retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert isinstance(data, dict)
        assert len(data) == 9  # All 9 activities
        
        # Verify all expected activities are present
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Soccer Club", "Art Club",
            "Drama Club", "Debate Club", "Science Club"
        ]
        for activity in expected_activities:
            assert activity in data
    
    def test_get_activities_contains_required_fields(self, client, reset_activities):
        """Test that activities contain all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            
            # Verify field types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_participant_data(self, client, reset_activities):
        """Test that participant data is correctly returned"""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club should have 2 participants
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        
        # Basketball Team should have 0 participants
        assert len(data["Basketball Team"]["participants"]) == 0


# ============================================================================
# Tests for POST /activities/{activity_name}/signup
# ============================================================================

class TestSignupForActivityEndpoint:
    """Tests for signing up for an activity"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successfully signing up for an activity"""
        response = client.post("/activities/Basketball Team/signup?email=alex@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "alex@mergington.edu" in data["message"]
        assert "Basketball Team" in data["message"]
        
        # Verify participant was added
        assert "alex@mergington.edu" in activities["Basketball Team"]["participants"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test multiple students signing up for the same activity"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(f"/activities/Art Club/signup?email={email}")
            assert response.status_code == 200
            assert email in activities["Art Club"]["participants"]
        
        # Verify all were added
        assert len(activities["Art Club"]["participants"]) == 3
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signing up for an activity that doesn't exist"""
        response = client.post("/activities/Nonexistent Club/signup?email=student@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_signup(self, client, reset_activities):
        """Test that a student cannot sign up twice for the same activity"""
        email = "newstudent@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response2.status_code == 400
        
        data = response2.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]
    
    def test_signup_valid_email_formats(self, client, reset_activities):
        """Test signing up with various valid email formats"""
        valid_emails = [
            "simple@mergington.edu",
            "user.name@mergington.edu",
            "usertag@mergington.edu",
            "user123@mergington.edu"
        ]
        
        for email in valid_emails:
            response = client.post(f"/activities/Soccer Club/signup?email={email}")
            assert response.status_code == 200
            assert email in activities["Soccer Club"]["participants"]
    
    def test_signup_empty_email(self, client, reset_activities):
        """Test signup with empty email parameter"""
        response = client.post("/activities/Drama Club/signup?email=")
        # FastAPI may handle this differently, but we should check the behavior
        assert response.status_code in [200, 422, 400]  # Depends on validation
    
    def test_signup_missing_email_parameter(self, client, reset_activities):
        """Test signup with missing email query parameter"""
        response = client.post("/activities/Drama Club/signup")
        # Should return 422 Unprocessable Entity due to missing required parameter
        assert response.status_code == 422
    
    def test_signup_to_different_activities(self, client, reset_activities):
        """Test that one student can sign up for multiple activities"""
        email = "versatile@mergington.edu"
        activities_to_join = ["Basketball Team", "Art Club", "Debate Club"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify student is in all activities
        for activity in activities_to_join:
            assert email in activities[activity]["participants"]
    
    def test_signup_activity_name_with_spaces(self, client, reset_activities):
        """Test signing up for activities with spaces in their names"""
        response = client.post("/activities/Chess Club/signup?email=player@mergington.edu")
        assert response.status_code == 200
        assert "player@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_activity_name_case_sensitive(self, client, reset_activities):
        """Test that activity names are case-sensitive"""
        response = client.post("/activities/basketball team/signup?email=student@mergington.edu")
        # Should fail because "basketball team" ≠ "Basketball Team"
        assert response.status_code == 404
    
    def test_signup_response_structure(self, client, reset_activities):
        """Test the structure of the signup response"""
        response = client.post("/activities/Science Club/signup?email=scientist@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 1
        assert "message" in data
        assert isinstance(data["message"], str)
    
    def test_signup_existing_participant_status(self, client, reset_activities):
        """Test that existing participants cannot sign up again"""
        # michael@mergington.edu is already in Chess Club
        response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
        assert response.status_code == 400


# ============================================================================
# Tests for DELETE /activities/{activity_name}/signup
# ============================================================================

class TestUnregisterFromActivityEndpoint:
    """Tests for unregistering from an activity"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successfully unregistering from an activity"""
        # First add a participant
        client.post("/activities/Basketball Team/signup?email=newstudent@mergington.edu")
        
        # Then remove them
        response = client.delete("/activities/Basketball Team/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Basketball Team" in data["message"]
        
        # Verify participant was removed
        assert "newstudent@mergington.edu" not in activities["Basketball Team"]["participants"]
    
    def test_unregister_existing_participant(self, client, reset_activities):
        """Test unregistering an existing participant"""
        # michael@mergington.edu is in Chess Club initially
        response = client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
        assert response.status_code == 200
        
        # Verify removed
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 1
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistering from an activity that doesn't exist"""
        response = client.delete("/activities/Nonexistent Club/signup?email=student@mergington.edu")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_unregister_not_signed_up(self, client, reset_activities):
        """Test unregistering a student who is not signed up"""
        response = client.delete("/activities/Basketball Team/signup?email=notmember@mergington.edu")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]
    
    def test_unregister_twice(self, client, reset_activities):
        """Test that a student cannot unregister twice"""
        email = "student@mergington.edu"
        
        # First signup
        client.post(f"/activities/Soccer Club/signup?email={email}")
        
        # First unregister should succeed
        response1 = client.delete(f"/activities/Soccer Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Second unregister should fail
        response2 = client.delete(f"/activities/Soccer Club/signup?email={email}")
        assert response2.status_code == 400
    
    def test_unregister_from_full_activity(self, client, reset_activities):
        """Test unregistering from an activity that was full"""
        activity = "Gym Class"
        email = "newmember@mergington.edu"
        
        # Sign up (it's not full yet)
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        assert email in activities[activity]["participants"]
        
        # Unregister
        response2 = client.delete(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 200
        assert email not in activities[activity]["participants"]
    
    def test_unregister_missing_email_parameter(self, client, reset_activities):
        """Test unregister with missing email query parameter"""
        response = client.delete("/activities/Chess Club/signup")
        assert response.status_code == 422
    
    def test_unregister_activity_name_case_sensitive(self, client, reset_activities):
        """Test that activity names are case-sensitive for unregister"""
        response = client.delete("/activities/chess club/signup?email=michael@mergington.edu")
        # Should fail because "chess club" ≠ "Chess Club"
        assert response.status_code == 404
    
    def test_unregister_response_structure(self, client, reset_activities):
        """Test the structure of the unregister response"""
        # First add someone
        client.post("/activities/Drama Club/signup?email=actor@mergington.edu")
        
        # Then remove them
        response = client.delete("/activities/Drama Club/signup?email=actor@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 1
        assert "message" in data
        assert isinstance(data["message"], str)
    
    def test_unregister_multiple_participants(self, client, reset_activities):
        """Test unregistering one participant doesn't affect others"""
        activity = "Programming Class"
        new_email = "coder@mergington.edu"
        
        # Add new participant
        client.post(f"/activities/{activity}/signup?email={new_email}")
        initial_count = len(activities[activity]["participants"])
        
        # Unregister new participant
        response = client.delete(f"/activities/{activity}/signup?email={new_email}")
        assert response.status_code == 200
        
        # Others should still be there
        assert "emma@mergington.edu" in activities[activity]["participants"]
        assert "sophia@mergington.edu" in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count - 1


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for combined operations"""
    
    def test_signup_and_unregister_cycle(self, client, reset_activities):
        """Test complete signup and unregister cycle"""
        email = "cycletest@mergington.edu"
        activity = "Debate Club"
        
        # Verify not signed up initially
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 400
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        assert email in activities[activity]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        assert email not in activities[activity]["participants"]
        
        # Can sign up again
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
    
    def test_concurrent_signups(self, client, reset_activities):
        """Test multiple students signing up for the same activity"""
        activity = "Art Club"
        emails = [f"student{i}@mergington.edu" for i in range(5)]
        
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all added
        for email in emails:
            assert email in activities[activity]["participants"]
        
        # Now unregister some
        for email in emails[:3]:
            response = client.delete(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
            assert email not in activities[activity]["participants"]
    
    def test_student_multiple_activity_lifecycle(self, client, reset_activities):
        """Test a student signing up for, then leaving multiple activities"""
        email = "multi@mergington.edu"
        target_activities = ["Chess Club", "Science Club", "Debate Club"]
        
        # Sign up for all
        for activity in target_activities:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify in all
        for activity in target_activities:
            assert email in activities[activity]["participants"]
        
        # Leave middle one
        response = client.delete(f"/activities/{target_activities[1]}/signup?email={email}")
        assert response.status_code == 200
        assert email not in activities[target_activities[1]]["participants"]
        # Still in others
        assert email in activities[target_activities[0]]["participants"]
        assert email in activities[target_activities[2]]["participants"]
    
    def test_activities_data_consistency(self, client, reset_activities):
        """Test that activities data remains consistent across operations"""
        # Get initial state
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_total_participants = sum(
            len(activity["participants"]) for activity in initial_data.values()
        )
        
        # Perform operations
        client.post("/activities/Basketball Team/signup?email=op1@mergington.edu")
        client.post("/activities/Soccer Club/signup?email=op2@mergington.edu")
        client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
        
        # Check new state
        final_response = client.get("/activities")
        final_data = final_response.json()
        final_total_participants = sum(
            len(activity["participants"]) for activity in final_data.values()
        )
        
        # Total should be: initial + 2 - 1
        assert final_total_participants == initial_total_participants + 1