"""
Tests for the Edu & Skill Path Recommender application.
"""

import unittest
from django.test import TestCase
from django.utils import timezone
from recommender.models import (
    EducationStage, 
    UserProfile, 
    Feedback
)
from recommender import services


class FeedbackTestCase(TestCase):
    """Test cases for the Feedback model and related functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create an education stage
        self.stage = EducationStage.objects.create(
            code=EducationStage.UG,
            name="Undergraduate",
            description="Undergraduate education stage"
        )
        
        # Create a user profile
        self.user = UserProfile.objects.create(
            name="Test User",
            education_stage=self.stage,
            age=20
        )
    
    def test_feedback_creation(self):
        """Test creating feedback entries."""
        feedback = Feedback.objects.create(
            user_profile=self.user,
            feedback_type=Feedback.FEEDBACK_TYPES[0][0],  # RECOMMENDATION
            rating=5,
            comment="Great recommendations!",
            suggestion="Add more career options"
        )
        
        self.assertEqual(feedback.user_profile, self.user)
        self.assertEqual(feedback.feedback_type, "RECOMMENDATION")
        self.assertEqual(feedback.rating, 5)
        self.assertEqual(feedback.comment, "Great recommendations!")
        self.assertEqual(feedback.suggestion, "Add more career options")
        self.assertFalse(feedback.is_resolved)
        self.assertIsNone(feedback.resolved_at)
    
    def test_feedback_str_representation(self):
        """Test the string representation of feedback."""
        feedback = Feedback.objects.create(
            user_profile=self.user,
            feedback_type="GENERAL",
            comment="Test feedback"
        )
        
        expected_str = f"Feedback from {self.user} - GENERAL ({feedback.created_at.strftime('%Y-%m-%d')})"
        self.assertEqual(str(feedback), expected_str)
    
    def test_feedback_without_user(self):
        """Test creating feedback without a user profile."""
        feedback = Feedback.objects.create(
            feedback_type="BUG_REPORT",
            comment="Found a bug"
        )
        
        self.assertIsNone(feedback.user_profile)
        self.assertEqual(feedback.feedback_type, "BUG_REPORT")
        self.assertEqual(feedback.comment, "Found a bug")
    
    def test_submit_user_feedback_service(self):
        """Test the submit_user_feedback service function."""
        feedback = services.submit_user_feedback(
            user_profile=self.user,
            feedback_type="FEATURE_REQUEST",
            rating=4,
            comment="Nice feature",
            suggestion="Improve the UI"
        )
        
        self.assertIsInstance(feedback, Feedback)
        self.assertEqual(feedback.user_profile, self.user)
        self.assertEqual(feedback.feedback_type, "FEATURE_REQUEST")
        self.assertEqual(feedback.rating, 4)
        self.assertEqual(feedback.comment, "Nice feature")
        self.assertEqual(feedback.suggestion, "Improve the UI")
    
    def test_get_user_feedback_stats(self):
        """Test the get_user_feedback_stats service function."""
        # Create some feedback entries
        Feedback.objects.create(
            user_profile=self.user,
            feedback_type="RECOMMENDATION",
            rating=5,
            comment="Great!"
        )
        
        Feedback.objects.create(
            user_profile=self.user,
            feedback_type="UI_EXPERIENCE",
            rating=4,
            comment="Good UI"
        )
        
        Feedback.objects.create(
            feedback_type="GENERAL",
            comment="Anonymous feedback"
        )
        
        stats = services.get_user_feedback_stats()
        
        self.assertEqual(stats['total_feedback'], 3)
        self.assertEqual(stats['resolved_feedback'], 0)
        self.assertAlmostEqual(stats['average_rating'], 4.5, places=1)
        self.assertIn('RECOMMENDATION', stats['feedback_by_type'])
        self.assertIn('UI_EXPERIENCE', stats['feedback_by_type'])
        self.assertIn('GENERAL', stats['feedback_by_type'])
        self.assertEqual(len(stats['recent_feedback']), 3)


class ModelTestCase(TestCase):
    """Test cases for the various models in the application."""
    
    def setUp(self):
        """Set up test data."""
        self.stage = EducationStage.objects.create(
            code=EducationStage.HIGH_SCHOOL,
            name="High School",
            description="High school education stage"
        )
    
    def test_education_stage_str(self):
        """Test the string representation of EducationStage."""
        self.assertEqual(str(self.stage), "High School")
    
    def test_user_profile_str(self):
        """Test the string representation of UserProfile."""
        user = UserProfile.objects.create(
            name="John Doe",
            education_stage=self.stage,
            age=16
        )
        
        self.assertEqual(str(user), "John Doe")


if __name__ == '__main__':
    unittest.main()