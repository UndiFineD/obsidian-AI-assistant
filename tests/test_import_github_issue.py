"""
Tests for GitHub issue import script.
"""

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Import the script module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from import_github_issue import (
    slugify,
    parse_issue_url,
    fetch_github_issue,
    build_change_id,
    create_change_directory
)


class TestSlugify:
    """Test slugify function."""
    
    def test_basic_slug(self):
        assert slugify("Hello World") == "hello-world"
    
    def test_special_characters(self):
        assert slugify("Fix: Bug in @user's feature (v2.0)") == "fix-bug-in-user-s-feature-v2-0"
    
    def test_multiple_spaces(self):
        assert slugify("Multiple   Spaces") == "multiple-spaces"
    
    def test_leading_trailing_hyphens(self):
        assert slugify("---leading trailing---") == "leading-trailing"
    
    def test_max_length(self):
        long_text = "a" * 100
        result = slugify(long_text, max_length=50)
        assert len(result) == 50
        assert not result.endswith('-')
    
    def test_unicode(self):
        assert slugify("Héllo Wörld") == "h-llo-w-rld"


class TestParseIssueUrl:
    """Test parse_issue_url function."""
    
    def test_parse_full_url(self):
        url = "https://github.com/owner/repo/issues/42"
        owner, repo, number = parse_issue_url(url)
        assert owner == "owner"
        assert repo == "repo"
        assert number == 42
    
    def test_parse_url_with_trailing_slash(self):
        url = "https://github.com/owner/repo/issues/42/"
        owner, repo, number = parse_issue_url(url)
        assert number == 42
    
    def test_parse_number_with_defaults(self):
        owner, repo, number = parse_issue_url("42", "default-owner", "default-repo")
        assert owner == "default-owner"
        assert repo == "default-repo"
        assert number == 42
    
    def test_parse_number_without_defaults(self):
        with pytest.raises(ValueError, match="Issue number provided without URL"):
            parse_issue_url("42")
    
    def test_invalid_hostname(self):
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            parse_issue_url("https://example.com/owner/repo/issues/42")
    
    def test_invalid_url_format(self):
        with pytest.raises(ValueError, match="Invalid GitHub issue URL format"):
            parse_issue_url("https://github.com/owner/repo")
    
    def test_invalid_issue_number(self):
        with pytest.raises(ValueError, match="Invalid issue number"):
            parse_issue_url("https://github.com/owner/repo/issues/not-a-number")


class TestFetchGitHubIssue:
    """Test fetch_github_issue function."""
    
    @patch('import_github_issue.requests.get')
    def test_fetch_with_token(self, mock_get):
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'number': 42,
            'title': 'Test Issue',
            'body': 'Test body',
            'user': {'login': 'testuser'},
            'html_url': 'https://github.com/owner/repo/issues/42',
            'state': 'open',
            'labels': []
        }
        mock_response.headers = {'X-RateLimit-Remaining': '5000'}
        mock_get.return_value = mock_response
        
        result = fetch_github_issue('owner', 'repo', 42, token='test-token')
        
        assert result['number'] == 42
        assert result['title'] == 'Test Issue'
        
        # Verify token was used
        call_args = mock_get.call_args
        assert 'Authorization' in call_args[1]['headers']
        assert call_args[1]['headers']['Authorization'] == 'token test-token'
    
    @patch('import_github_issue.requests.get')
    def test_fetch_without_token(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'number': 42}
        mock_response.headers = {'X-RateLimit-Remaining': '60'}
        mock_get.return_value = mock_response
        
        result = fetch_github_issue('owner', 'repo', 42)
        
        # Verify no token in headers
        call_args = mock_get.call_args
        assert 'Authorization' not in call_args[1]['headers']
    
    @patch('import_github_issue.requests.get')
    def test_fetch_404_not_found(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404")
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError, match="Issue not found"):
            fetch_github_issue('owner', 'repo', 42)
    
    @patch('import_github_issue.requests.get')
    def test_fetch_403_forbidden(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = Exception("403")
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError, match="Access forbidden"):
            fetch_github_issue('owner', 'repo', 42)
    
    @patch('import_github_issue.requests.get')
    def test_rate_limit_warning(self, mock_get, capsys):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'number': 42}
        mock_response.headers = {'X-RateLimit-Remaining': '5'}
        mock_get.return_value = mock_response
        
        fetch_github_issue('owner', 'repo', 42)
        
        captured = capsys.readouterr()
        assert 'rate limit low' in captured.out.lower()


class TestBuildChangeId:
    """Test build_change_id function."""
    
    def test_build_with_date(self):
        change_id = build_change_id("Test Issue", "2025-10-18")
        assert change_id == "2025-10-18-test-issue"
    
    def test_build_without_date(self):
        change_id = build_change_id("Test Issue")
        assert change_id.endswith("-test-issue")
        # Should start with date in YYYY-MM-DD format
        assert len(change_id.split('-')[0]) == 4  # Year
    
    def test_build_with_special_chars(self):
        change_id = build_change_id("Fix: Bug in Feature (v2)", "2025-10-18")
        assert change_id == "2025-10-18-fix-bug-in-feature-v2"


class TestCreateChangeDirectory:
    """Test create_change_directory function."""
    
    def test_create_basic_directory(self, tmp_path):
        # Create template directory
        template_dir = tmp_path / 'openspec' / 'templates'
        template_dir.mkdir(parents=True)
        
        # Create basic template
        (template_dir / 'todo.md').write_text(
            "# TODO: <Change Title>\n"
            "Change ID: <change-id>\n"
            "Date: YYYY-MM-DD\n"
            "Owner: @username\n"
            "GitHub Issue: #XXX\n"
        )
        
        # Mock issue data
        issue_data = {
            'number': 42,
            'title': 'Test Issue',
            'body': 'Test description',
            'user': {'login': 'testuser', 'html_url': 'https://github.com/testuser'},
            'html_url': 'https://github.com/owner/repo/issues/42',
            'state': 'open',
            'created_at': '2025-10-18T10:00:00Z',
            'labels': [{'name': 'bug'}, {'name': 'enhancement'}]
        }
        
        # Create change directory
        change_dir = create_change_directory(
            issue_data,
            tmp_path,
            change_id='2025-10-18-test-issue',
            owner='@testowner'
        )
        
        # Verify directory created
        assert change_dir.exists()
        assert change_dir.name == '2025-10-18-test-issue'
        
        # Verify files created
        assert (change_dir / 'proposal.md').exists()
        assert (change_dir / 'spec.md').exists()
        assert (change_dir / 'tasks.md').exists()
        assert (change_dir / 'test_plan.md').exists()
        assert (change_dir / 'todo.md').exists()
        
        # Verify content
        proposal = (change_dir / 'proposal.md').read_text()
        assert 'Test Issue' in proposal
        assert 'Test description' in proposal
        assert 'https://github.com/owner/repo/issues/42' in proposal
        assert 'bug, enhancement' in proposal
        
        todo = (change_dir / 'todo.md').read_text()
        assert 'Test Issue' in todo
        assert '2025-10-18-test-issue' in todo
        assert '@testowner' in todo
        assert 'https://github.com/owner/repo/issues/42' in todo
    
    def test_create_without_template(self, tmp_path):
        issue_data = {
            'number': 42,
            'title': 'Test Issue',
            'body': 'Test description',
            'user': {'login': 'testuser', 'html_url': 'https://github.com/testuser'},
            'html_url': 'https://github.com/owner/repo/issues/42',
            'state': 'open',
            'created_at': '2025-10-18T10:00:00Z',
            'labels': []
        }
        
        change_dir = create_change_directory(
            issue_data,
            tmp_path,
            change_id='test-change'
        )
        
        # Should still create files, including basic todo.md
        assert (change_dir / 'todo.md').exists()
        todo = (change_dir / 'todo.md').read_text()
        assert 'Test Issue' in todo
    
    def test_create_directory_exists_no_force(self, tmp_path):
        issue_data = {
            'number': 42,
            'title': 'Test Issue',
            'body': '',
            'user': {'login': 'test', 'html_url': 'https://github.com/test'},
            'html_url': 'https://github.com/owner/repo/issues/42',
            'state': 'open',
            'created_at': '2025-10-18T10:00:00Z',
            'labels': []
        }
        
        # Create directory first time
        change_dir = create_change_directory(
            issue_data,
            tmp_path,
            change_id='existing-change'
        )
        
        # Try to create again without force
        with pytest.raises(ValueError, match="already exists"):
            create_change_directory(
                issue_data,
                tmp_path,
                change_id='existing-change',
                force=False
            )
    
    def test_create_directory_exists_with_force(self, tmp_path):
        issue_data = {
            'number': 42,
            'title': 'Test Issue',
            'body': '',
            'user': {'login': 'test', 'html_url': 'https://github.com/test'},
            'html_url': 'https://github.com/owner/repo/issues/42',
            'state': 'open',
            'created_at': '2025-10-18T10:00:00Z',
            'labels': []
        }
        
        # Create directory first time
        change_dir = create_change_directory(
            issue_data,
            tmp_path,
            change_id='existing-change'
        )
        
        # Create marker file
        (change_dir / 'marker.txt').write_text('original')
        
        # Overwrite with force
        change_dir = create_change_directory(
            issue_data,
            tmp_path,
            change_id='existing-change',
            force=True
        )
        
        # Should succeed and files should exist
        assert (change_dir / 'proposal.md').exists()
    
    def test_auto_generated_change_id(self, tmp_path):
        issue_data = {
            'number': 42,
            'title': 'Auto Generated ID',
            'body': '',
            'user': {'login': 'test', 'html_url': 'https://github.com/test'},
            'html_url': 'https://github.com/owner/repo/issues/42',
            'state': 'open',
            'created_at': '2025-10-18T10:00:00Z',
            'labels': []
        }
        
        change_dir = create_change_directory(issue_data, tmp_path)
        
        # Should auto-generate from title
        assert 'auto-generated-id' in change_dir.name
    
    def test_default_owner_from_issue(self, tmp_path):
        issue_data = {
            'number': 42,
            'title': 'Test',
            'body': '',
            'user': {'login': 'issueauthor', 'html_url': 'https://github.com/issueauthor'},
            'html_url': 'https://github.com/owner/repo/issues/42',
            'state': 'open',
            'created_at': '2025-10-18T10:00:00Z',
            'labels': []
        }
        
        change_dir = create_change_directory(issue_data, tmp_path, change_id='test')
        
        # Should use issue author as owner
        todo = (change_dir / 'todo.md').read_text()
        assert '@issueauthor' in todo


class TestIntegration:
    """Integration tests for the full workflow."""
    
    @patch('import_github_issue.requests.get')
    def test_full_workflow(self, mock_get, tmp_path):
        """Test complete workflow from URL to directory creation."""
        # Setup
        template_dir = tmp_path / 'openspec' / 'templates'
        template_dir.mkdir(parents=True)
        (template_dir / 'todo.md').write_text(
            "# TODO: <Change Title>\nChange ID: <change-id>\n"
        )
        
        # Mock GitHub API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'number': 123,
            'title': 'Add New Feature',
            'body': 'This feature would be awesome',
            'user': {'login': 'contributor', 'html_url': 'https://github.com/contributor'},
            'html_url': 'https://github.com/myorg/myrepo/issues/123',
            'state': 'open',
            'created_at': '2025-10-18T12:00:00Z',
            'labels': [{'name': 'enhancement'}]
        }
        mock_response.headers = {'X-RateLimit-Remaining': '5000'}
        mock_get.return_value = mock_response
        
        # Execute
        url = "https://github.com/myorg/myrepo/issues/123"
        owner, repo, number = parse_issue_url(url)
        issue_data = fetch_github_issue(owner, repo, number)
        change_dir = create_change_directory(issue_data, tmp_path)
        
        # Verify
        assert change_dir.exists()
        assert 'add-new-feature' in change_dir.name
        assert (change_dir / 'proposal.md').exists()
        
        proposal = (change_dir / 'proposal.md').read_text()
        assert 'Add New Feature' in proposal
        assert 'This feature would be awesome' in proposal
        assert 'enhancement' in proposal


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
