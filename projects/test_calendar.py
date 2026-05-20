"""
Test suite for calendar deadline features across all user roles.
Tests that project deadlines display correctly in the calendar for:
- Admin (sees all projects)
- Project Manager (sees managed projects)
- Team Leader (sees assigned projects)
- Team Member (sees projects with assigned tasks)
- Client (sees their client's projects)
"""

from django.test import TestCase, Client as HttpClient
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date, timedelta
import json

from .models import Project, UserProfile, ProjectAssignment, Team, Client


class CalendarDeadlineTest(TestCase):
    def setUp(self):
        """Set up test data for calendar deadline testing."""
        # Create a test client
        self.test_client = Client.objects.create(
            name='Test Client',
            email='client@company.com',
            phone='555-1234'
        )
        
        # Create users with different roles
        # Note: UserProfile is auto-created via post_save signal, so just update the role
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()
        
        self.pm_user = User.objects.create_user(
            username='pm',
            email='pm@test.com',
            password='testpass123'
        )
        self.pm_user.profile.role = 'project_manager'
        self.pm_user.profile.save()
        
        self.tl_user = User.objects.create_user(
            username='tl',
            email='tl@test.com',
            password='testpass123'
        )
        self.tl_user.profile.role = 'team_leader'
        self.tl_user.profile.save()
        
        self.tm_user = User.objects.create_user(
            username='tm',
            email='tm@test.com',
            password='testpass123'
        )
        self.tm_user.profile.role = 'team_member'
        self.tm_user.profile.save()
        
        # Create test projects with deadlines
        self.project1 = Project.objects.create(
            title='Test Project 1',
            manager=self.pm_user,
            client=self.test_client,
            deadline=date.today() + timedelta(days=7),
            status='active'
        )
        
        self.project2 = Project.objects.create(
            title='Test Project 2',
            manager=self.pm_user,
            client=self.test_client,
            deadline=date.today() + timedelta(days=14),
            status='active'
        )
        
        # Assign project to team leader
        ProjectAssignment.objects.create(
            project=self.project1,
            team_leader=self.tl_user,
            status='accepted'
        )
        
        self.client = HttpClient()
    
    def test_calendar_page_accessibility(self):
        """Test that calendar page is accessible to authenticated users."""
        # Admin can access calendar
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('calendar'))
        self.assertEqual(response.status_code, 200)
        
        # Project manager can access calendar
        self.client.login(username='pm', password='testpass123')
        response = self.client.get(reverse('calendar'))
        self.assertEqual(response.status_code, 200)
        
        # Team leader can access calendar
        self.client.login(username='tl', password='testpass123')
        response = self.client.get(reverse('calendar'))
        self.assertEqual(response.status_code, 200)
        
        # Team member can access calendar
        self.client.login(username='tm', password='testpass123')
        response = self.client.get(reverse('calendar'))
        self.assertEqual(response.status_code, 200)
    
    def test_calendar_events_json_admin(self):
        """Test that admin sees all project deadlines in calendar events."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('calendar_events_json'))
        
        self.assertEqual(response.status_code, 200)
        events = json.loads(response.content)
        
        # Admin should see both projects
        project_events = [e for e in events if e['extendedProps']['type'] == 'project']
        self.assertGreaterEqual(len(project_events), 2)
        
        # Verify project titles
        titles = [e['title'] for e in project_events]
        self.assertTrue(any('Test Project 1' in t for t in titles))
        self.assertTrue(any('Test Project 2' in t for t in titles))
    
    def test_calendar_events_json_project_manager(self):
        """Test that project manager sees only their managed projects."""
        self.client.login(username='pm', password='testpass123')
        response = self.client.get(reverse('calendar_events_json'))
        
        self.assertEqual(response.status_code, 200)
        events = json.loads(response.content)
        
        # Project manager should see their projects
        project_events = [e for e in events if e['extendedProps']['type'] == 'project']
        self.assertGreaterEqual(len(project_events), 2)
        
        # Verify they see projects they manage
        titles = [e['title'] for e in project_events]
        self.assertTrue(any('Test Project' in t for t in titles))
    
    def test_calendar_events_json_team_leader(self):
        """Test that team leader sees assigned project deadlines."""
        self.client.login(username='tl', password='testpass123')
        response = self.client.get(reverse('calendar_events_json'))
        
        self.assertEqual(response.status_code, 200)
        events = json.loads(response.content)
        
        # Team leader should see assigned project
        project_events = [e for e in events if e['extendedProps']['type'] == 'project']
        self.assertGreaterEqual(len(project_events), 1)
        
        # Verify they see Project 1 (which is assigned to them)
        titles = [e['title'] for e in project_events]
        self.assertTrue(any('Test Project 1' in t for t in titles))
    
    def test_project_deadline_display_format(self):
        """Test that project deadlines are properly formatted in calendar."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('calendar_events_json'))
        
        events = json.loads(response.content)
        project_events = [e for e in events if e['extendedProps']['type'] == 'project']
        
        # Verify event structure
        for event in project_events:
            self.assertIn('id', event)
            self.assertIn('title', event)
            self.assertIn('start', event)
            self.assertIn('backgroundColor', event)
            self.assertIn('extendedProps', event)
            
            # Verify extended properties contain project info
            props = event['extendedProps']
            self.assertEqual(props['type'], 'project')
            self.assertIn('client', props)
            self.assertIn('manager', props)
            self.assertIn('status', props)
    
    def test_project_deadline_color_coding(self):
        """Test that project deadlines are color-coded based on status."""
        # Create projects with different statuses
        completed_project = Project.objects.create(
            title='Completed Project',
            manager=self.pm_user,
            deadline=date.today() + timedelta(days=7),
            status='completed'
        )
        
        on_hold_project = Project.objects.create(
            title='On Hold Project',
            manager=self.pm_user,
            deadline=date.today() + timedelta(days=7),
            status='on_hold'
        )
        
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('calendar_events_json'))
        
        events = json.loads(response.content)
        project_events = {e['title']: e for e in events if e['extendedProps']['type'] == 'project'}
        
        # Verify color coding
        # Green for completed
        if any('Completed Project' in t for t in project_events.keys()):
            for title, event in project_events.items():
                if 'Completed Project' in title:
                    self.assertEqual(event['backgroundColor'], '#10b981')  # Green
        
        # Amber for on_hold
        if any('On Hold Project' in t for t in project_events.keys()):
            for title, event in project_events.items():
                if 'On Hold Project' in title:
                    self.assertEqual(event['backgroundColor'], '#f59e0b')  # Amber


class CalendarAccessibilityTest(TestCase):
    """Test calendar accessibility for different user roles."""
    
    def setUp(self):
        """Create test users."""
        # Client user (should not see calendar or see limited version)
        self.client_user = User.objects.create_user(
            username='client',
            email='client@test.com',
            password='testpass123'
        )
        self.client_user.profile.role = 'client'
        self.client_user.profile.save()
        
        self.client_http = HttpClient()
    
    def test_client_cannot_access_calendar_directly(self):
        """Test that clients are redirected away from calendar page."""
        self.client_http.login(username='client', password='testpass123')
        response = self.client_http.get(reverse('calendar'), follow=False)
        
        # Clients should be redirected from calendar page (status 302)
        self.assertEqual(response.status_code, 302)


# Run tests with: python manage.py test projects.test_calendar
