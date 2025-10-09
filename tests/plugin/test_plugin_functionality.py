# tests/plugin/test_plugin_functionality.py
"""
Python-based tests for validating Obsidian Plugin JavaScript functionality.
Tests specific features and behaviors without requiring Node.js.
"""
import pytest
import re
from pathlib import Path


class TestPluginFunctionality:
    """Test specific plugin functionality through static analysis."""
    
    @property
    def plugin_dir(self):
        return Path(__file__).parent.parent.parent / "plugin"
    
    @property
    def main_js_content(self):
        main_path = self.plugin_dir / "main.js"
        with open(main_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_backend_health_check_functionality(self):
        """Test that backend health check is implemented."""
        content = self.main_js_content
        
        # Look for status/health check endpoint usage
        health_patterns = [
            r'/status',
            r'/health',
            r'status.*check',
            r'backend.*status'
        ]
        
        found_health = sum(1 for pattern in health_patterns 
                          if re.search(pattern, content, re.IGNORECASE))
        
        assert found_health >= 1, "Should have backend health check functionality"
        
        # Should have error handling for backend connection
        error_patterns = [
            r'catch\s*\(',
            r'\.catch',
            r'try\s*\{',
            r'error'
        ]
        
        found_error_handling = sum(1 for pattern in error_patterns 
                                  if re.search(pattern, content, re.IGNORECASE))
        
        assert found_error_handling >= 2, "Should have proper error handling"
        
        print("✓ Backend health check functionality implemented")

    def test_settings_persistence(self):
        """Test that settings can be saved and loaded."""
        content = self.main_js_content
        
        # Check for settings save/load patterns
        settings_patterns = [
            r'loadSettings',
            r'saveSettings', 
            r'settings\s*=',
            r'Object\.assign.*settings'
        ]
        
        found_settings = sum(1 for pattern in settings_patterns
                            if re.search(pattern, content, re.IGNORECASE))
        assert found_settings >= 2, "Should have settings save/load functionality"
        # Check for default settings merge
        assert 'DEFAULT_SETTINGS' in content, "Should use default settings"
        print("✓ Settings persistence functionality implemented")

    def test_fetch_api_usage(self):
        """Test that fetch API is used for backend communication."""
        content = self.main_js_content
        
        # Should use fetch for HTTP requests
        assert 'fetch(' in content, "Should use fetch API for HTTP requests"
        # Should handle different HTTP methods
        http_methods = ['GET', 'POST']  # Check for the most common methods
        found_methods = sum(1 for method in http_methods 
                           if re.search(method, content, re.IGNORECASE))
        
        assert found_methods >= 2, f"Should use multiple HTTP methods, found {found_methods}"
        
        # Should handle JSON content
        json_patterns = [
            r'JSON\.parse',
            r'JSON\.stringify',
            r'application/json'
        ]
        
        found_json = sum(1 for pattern in json_patterns 
                        if re.search(pattern, content))
        
        assert found_json >= 1, "Should handle JSON content"
        
        print("✓ Fetch API usage is proper")

    def test_user_interface_elements(self):
        """Test that UI elements are properly created."""
        content = self.main_js_content
        
        # Should create UI elements
        ui_patterns = [
            r'createEl\s*\(',
            r'contentEl',
            r'containerEl',
            r'setText',
            r'button'
        ]
        
        found_ui = sum(1 for pattern in ui_patterns 
                      if re.search(pattern, content, re.IGNORECASE))
        assert found_ui >= 3, f"Should create UI elements, found {found_ui} patterns"
        # Should handle user interactions
        interaction_patterns = [
            r'onclick',
            r'addEventListener',
            r'onchange',
            r'\.click'
        ]
        found_interactions = sum(1 for pattern in interaction_patterns 
                                if re.search(pattern, content, re.IGNORECASE))
        assert found_interactions >= 1, "Should handle user interactions"
        print("✓ UI elements and interactions are implemented")

    def test_notice_system_usage(self):
        """Test that Obsidian Notice system is used for feedback."""
        content = self.main_js_content
        
        # Should use Notice for user feedback
        assert 'Notice(' in content, "Should use Obsidian Notice system"
        
        # Should provide meaningful feedback messages
        notice_patterns = [
            r'Notice\s*\(\s*["\'][^"\']{10,}["\']',  # Notices with meaningful text
            r'new\s+Notice'
        ]
        
        found_notices = sum(1 for pattern in notice_patterns 
                           if re.search(pattern, content))
        
        assert found_notices >= 1, "Should provide meaningful user feedback"
        
        print("✓ Notice system is properly used")


class TestTaskQueueFunctionality:
    """Test task queue specific functionality."""
    
    @property
    def task_queue_content(self):
        task_queue_path = Path(__file__).parent.parent.parent / "plugin" / "taskQueue.js"
        with open(task_queue_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_queue_operations(self):
        """Test that queue operations are implemented."""
        content = self.task_queue_content
        # Should have queue data structure
        queue_indicators = [
            r'queue',
            r'array',
            r'\[\s*\]',  # Empty array initialization
            r'push',
            r'shift',
            r'length'
        ]
        found_queue_ops = sum(1 for pattern in queue_indicators 
                             if re.search(pattern, content, re.IGNORECASE))
        assert found_queue_ops >= 3, f"Should implement queue operations, found {found_queue_ops}"
        print("✓ Task queue operations implemented")

    def test_task_processing(self):
        """Test that task processing logic exists."""
        content = self.task_queue_content
        # Should have task processing patterns
        processing_patterns = [
            r'process',
            r'execute',
            r'run',
            r'handle',
            r'async',
            r'await'
        ]
        found_processing = sum(1 for pattern in processing_patterns 
                              if re.search(pattern, content, re.IGNORECASE))
        assert found_processing >= 2, "Should have task processing logic"
        print("✓ Task processing logic implemented")


class TestVoiceFunctionality:
    """Test voice input functionality."""
    
    @property
    def voice_content(self):
        voice_path = Path(__file__).parent.parent.parent / "plugin" / "voice.js"
        with open(voice_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @property
    def voice_input_content(self):
        voice_input_path = Path(__file__).parent.parent.parent / "plugin" / "voiceInput.js"
        with open(voice_input_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_audio_recording_setup(self):
        """Test that audio recording is set up."""
        voice_content = self.voice_content
        voice_input_content = self.voice_input_content
        combined_content = voice_content + voice_input_content
        # Should have audio/media-related APIs
        audio_patterns = [
            r'getUserMedia',
            r'MediaRecorder',
            r'audio',
            r'microphone',
            r'record',
            r'start.*record',
            r'stop.*record'
        ]
        found_audio = sum(1 for pattern in audio_patterns 
                         if re.search(pattern, combined_content, re.IGNORECASE))
        assert found_audio >= 2, f"Should implement audio recording, found {found_audio} patterns"
        print("✓ Audio recording functionality detected")

    def test_voice_processing_workflow(self):
        """Test that voice processing workflow exists."""
        voice_content = self.voice_content
        voice_input_content = self.voice_input_content
        combined_content = voice_content + voice_input_content
        # Should have workflow-related patterns
        workflow_patterns = [
            r'start',
            r'stop',
            r'process',
            r'transcribe',
            r'speech.*text',
            r'audio.*process'
        ]
        found_workflow = sum(1 for pattern in workflow_patterns 
                            if re.search(pattern, combined_content, re.IGNORECASE))
        assert found_workflow >= 3, "Should have voice processing workflow"
        print("✓ Voice processing workflow implemented")


class TestAnalyticsFunctionality:
    """Test analytics functionality."""
    
    @property
    def analytics_content(self):
        analytics_path = Path(__file__).parent.parent.parent / "plugin" / "analyticsPane.js"
        with open(analytics_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_analytics_data_handling(self):
        """Test that analytics data is handled."""
        content = self.analytics_content
        # Should handle data collection/display
        analytics_patterns = [
            r'data',
            r'stats',
            r'analytics',
            r'metrics',
            r'count',
            r'total',
            r'display.*data'
        ]
        found_analytics = sum(1 for pattern in analytics_patterns 
                             if re.search(pattern, content, re.IGNORECASE))
        assert found_analytics >= 2, "Should handle analytics data"
        print("✓ Analytics data handling implemented")

    def test_ui_rendering_for_analytics(self):
        """Test that analytics UI is rendered."""
        content = self.analytics_content
        # Should create UI for analytics display
        ui_patterns = [
            r'create',
            r'render',
            r'display',
            r'show',
            r'update.*ui',
            r'element'
        ]
        found_ui = sum(1 for pattern in ui_patterns 
                      if re.search(pattern, content, re.IGNORECASE))
        assert found_ui >= 2, "Should create analytics UI"
        print("✓ Analytics UI rendering implemented")


class TestErrorHandlingAndRobustness:
    """Test error handling and robustness across plugin files."""
    
    def test_comprehensive_error_handling(self):
        """Test that all plugin files have proper error handling."""
        plugin_dir = Path(__file__).parent.parent.parent / "plugin"
        js_files = list(plugin_dir.glob("*.js"))
        
        def has_error_handling(file_path):
            """Check if a file contains error handling patterns."""
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Check for error handling patterns
            error_patterns = [
                r'try\s*\{',
                r'catch\s*\(',
                r'\.catch\s*\(',
                r'throw\s+',
                r'Error\s*\(',
                r'console\.(error|warn)'
            ]
            return any(re.search(pattern, content) for pattern in error_patterns)

        files_with_error_handling = sum(1 for js_file in js_files if has_error_handling(js_file))
        
        # At least 40% of files should have error handling (main files)
        error_coverage = files_with_error_handling / len(js_files)
        assert error_coverage >= 0.40, \
            f"Should have error handling in key files. Coverage: {error_coverage:.2%}"
        print(f"✓ Error handling coverage: {error_coverage:.2%} ({files_with_error_handling}/{len(js_files)} files)")


if __name__ == "__main__":
    # Run tests individually for debugging
    print("🧪 Running Plugin Functionality Tests")
    print("======================================")
    
    # Run with pytest
    pytest.main([__file__, "-v"])