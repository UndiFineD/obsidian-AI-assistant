# tests/obsidian-ai-agent/test_plugin_structure.py
"""
Python-based tests for validating Obsidian Plugin JavaScript files.
Tests structure, syntax, and key functionality without requiring Node.js.
"""

import json
import re
from pathlib import Path

import pytest

# Skip all tests in this module if plugin is not deployed
pytestmark = pytest.mark.skipif(
    not Path(".obsidian/plugins/obsidian-ai-agent").exists(),
    reason="Plugin not deployed to .obsidian/plugins/obsidian-ai-agent. "
    "These tests require a deployed Obsidian plugin. "
    "Run './setup-plugin.ps1' to deploy to your Obsidian vault.",
)


class TestPluginStructure:
    """Test plugin file structure and manifest."""

    @property
    def plugin_dir(self):
        return Path(".obsidian/plugins/obsidian-ai-agent")

    def test_manifest_exists_and_valid(self):
        """Test that manifest.json exists and is valid."""
        manifest_path = self.plugin_dir / "manifest.json"
        assert manifest_path.exists(), "manifest.json should exist in plugin directory"

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        # Check required manifest fields
        required_fields = [
            "id",
            "name",
            "version",
            "minAppVersion",
            "description",
            "author",
        ]
        for field in required_fields:
            assert field in manifest, f"manifest.json missing required field: {field}"
            assert manifest[field], f"manifest.json field {field} should not be empty"

        # Validate specific values
        assert manifest["id"] == "obsidian-ai-agent"
        assert manifest["name"] == "AI Assistant"
        assert re.match(r"\d+\.\d+\.\d+", manifest["version"]), (
            "Version should follow semantic versioning"
        )
        print("✓ Manifest.json is valid and complete")

    def test_main_js_exists(self):
        """Test that main.js exists and has basic structure."""
        main_path = self.plugin_dir / "main.js"
        assert main_path.exists(), "main.js should exist in plugin directory"

        with open(main_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert len(content) > 1000, "main.js should contain substantial code"
        assert "require('obsidian'" in content or "from 'obsidian'" in content, (
            "main.js should import from obsidian"
        )
        assert "class" in content, "main.js should contain class definitions"

        print(f"✓ main.js exists and contains {len(content)} characters")

    def test_essential_plugin_files_exist(self):
        """Test that all essential plugin files exist."""
        essential_files = [
            "main.js",
            "manifest.json",
            "styles.css",
            "analyticsPane.js",
            "taskQueue.js",
            "taskQueueView.js",
            "voice.js",
            "voiceInput.js",
        ]

        missing_files = []
        for filename in essential_files:
            file_path = self.plugin_dir / filename
            if not file_path.exists():
                missing_files.append(filename)

        assert not missing_files, f"Missing essential plugin files: {missing_files}"
        print(f"✓ All {len(essential_files)} essential plugin files exist")


class TestMainPluginFile:
    """Test the main plugin file structure and key classes."""

    @property
    def main_js_content(self):
        main_path = Path(".obsidian/plugins/obsidian-ai-agent/main.js")
        with open(main_path, "r", encoding="utf-8") as f:
            return f.read()

    def test_plugin_class_structure(self):
        """Test that main plugin class is properly defined."""
        content = self.main_js_content

        # Check for main plugin class
        assert "class ObsidianAIAgent extends Plugin" in content, (
            "Should have ObsidianAIAgent class extending Plugin"
        )

        # Check for essential methods (onload is required, onunload is optional
        assert "onload(" in content or "onload (" in content, "Plugin should have onload method"
        assert "loadSettings(" in content or "loadSettings (" in content, (
            "Plugin should have loadSettings method"
        )
        assert "saveSettings(" in content or "saveSettings (" in content, (
            "Plugin should have saveSettings method"
        )

        print("✓ Main plugin class structure is correct")

    def test_modal_classes_defined(self):
        """Test that modal classes are properly defined."""
        content = self.main_js_content

        # Check for AIModal class
        assert "class AIModal extends Modal" in content, "Should have AIModal class extending Modal"

        # Check for onOpen method (onClose is optional
        pattern = r"onOpen\s*\([^)]*\)\s*\{"
        assert re.search(pattern, content), "AIModal should have onOpen method"

        print("✓ Modal classes are properly defined")

    def test_settings_tab_structure(self):
        """Test that settings tab is properly implemented."""
        content = self.main_js_content

        # Check for settings tab class
        assert "class AIAssistantSettingTab extends PluginSettingTab" in content, (
            "Should have AIAssistantSettingTab class"
        )

        # Check for display method
        assert re.search(r"display\s*\(", content), "Settings tab should have a display() method"

        print("✓ Settings tab structure is correct")

    def test_default_settings_defined(self):
        """Test that default settings are properly defined."""
        content = self.main_js_content

        # Check for DEFAULT_SETTINGS constant
        assert "DEFAULT_SETTINGS" in content, "Should define DEFAULT_SETTINGS"

        # Check for essential setting keys (without quotes for property names
        essential_settings = ["backendUrl", "features"]
        for setting in essential_settings:
            # Look for property name in JavaScript object (can be with or without quotes)
            pattern = rf'["\']?{setting}["\']?\s*:'
            assert re.search(pattern, content), (
                f"DEFAULT_SETTINGS should include {setting} property"
            )

        print("✓ Default settings are properly defined")

    def test_agent_communication_setup(self):
        """Test that backend communication is set up."""
        content = self.main_js_content

        # Check for fetch or HTTP-related code
        communication_patterns = [
            r"fetch\s*\(",
            r"http[s]?://",
            r"backendUrl",
            r"localhost:\d+",
        ]
        found_patterns = []
        for pattern in communication_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                found_patterns.append(pattern)
        assert len(found_patterns) >= 2, (
            f"Should have backend communication setup. Found patterns: {found_patterns}"
        )
        print("✓ Backend communication setup detected")


class TestPluginModules:
    """Test individual plugin module files."""

    @property
    def plugin_dir(self):
        return Path(".obsidian/plugins/obsidian-ai-agent")

    def test_analytics_pane_structure(self):
        """Test analyticsPane.js structure."""
        file_path = self.plugin_dir / "analyticsPane.js"
        assert file_path.exists(), "analyticsPane.js should exist"

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for class or function definitions
        has_structure = any(
            [
                "class" in content,
                "function" in content,
                "=>" in content,  # Arrow functions
            ]
        )
        assert has_structure, "analyticsPane.js should contain function or class definitions"

        print("✓ analyticsPane.js has proper structure")

    def test_task_queue_structure(self):
        """Test taskQueue.js structure."""
        file_path = self.plugin_dir / "taskQueue.js"
        assert file_path.exists(), "taskQueue.js should exist"

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Look for queue-related functionality
        queue_patterns = [r"queue", r"push", r"pop", r"shift", r"unshift", r"length"]

        found_queue_patterns = sum(
            1 for pattern in queue_patterns if re.search(pattern, content, re.IGNORECASE)
        )

        assert found_queue_patterns >= 2, (
            f"taskQueue.js should contain queue functionality. Found {found_queue_patterns} patterns"
        )

        print("✓ taskQueue.js has queue functionality")

    def test_voice_modules_structure(self):
        """Test voice.js and voiceInput.js structure."""
        voice_files = ["voice.js", "voiceInput.js"]
        for filename in voice_files:
            file_path = Path(f".obsidian/plugins/obsidian-ai-agent/{filename}")
            assert file_path.exists(), f"{filename} should exist"

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for voice-related functionality
            voice_patterns = [r"audio", r"microphone", r"record", r"speech", r"voice"]

            found_patterns = sum(
                1 for pattern in voice_patterns if re.search(pattern, content, re.IGNORECASE)
            )

            assert found_patterns >= 1, (
                f"{filename} should contain voice-related functionality. Found {found_patterns} patterns"
            )

        print("✓ Voice modules have proper structure")

    def test_styles_css_exists(self):
        """Test that styles.css exists and contains CSS."""
        file_path = self.plugin_dir / "styles.css"
        assert file_path.exists(), "styles.css should exist"

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for basic CSS structure
        css_patterns = [
            r"\{[^}]+\}",  # CSS rule blocks
            r"[.#][\w-]+",  # CSS selectors
            r":\s*[^;]+;",  # CSS properties
        ]

        found_css = sum(1 for pattern in css_patterns if re.search(pattern, content))

        assert found_css >= 2, f"styles.css should contain valid CSS. Found {found_css} patterns"
        print("✓ styles.css contains valid CSS")


class TestPluginConfiguration:
    """Test plugin configuration and setup."""

    @property
    def plugin_dir(self):
        return Path(".obsidian/plugins/obsidian-ai-agent")

    def test_config_template_exists(self):
        """Test that config template exists."""
        template_path = self.plugin_dir / "config.template.json"
        if template_path.exists():
            with open(template_path, "r") as f:
                config = json.load(f)

            # Should be valid JSON with some configuration
            assert isinstance(config, dict), "config.template.json should be a JSON object"
            print("✓ config.template.json exists and is valid JSON")
        else:
            print("⚠ config.template.json not found (optional)")

    def test_no_sensitive_data_in_files(self):
        """Test that plugin files don't contain sensitive data."""
        sensitive_patterns = [
            r'password\s*=\s*["\'][^"\']{3,}["\']',  # Only match actual assignments with =
            r'api[_-]?key\s*=\s*["\'][^"\']{8,}["\']',  # Only match actual assignments with =
            r'secret\s*=\s*["\'][^"\']{8,}["\']',  # Only match actual assignments with =
            r'token\s*=\s*["\'][^"\']{8,}["\']',  # Only match actual assignments with =, not object properties
        ]

        js_files = self.plugin_dir.glob("*.js")

        for js_file in js_files:
            with open(js_file, "r", encoding="utf-8") as f:
                content = f.read()

            for pattern in sensitive_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                assert not matches, f"Found potential sensitive data in {js_file.name}: {matches}"

        print("✓ No sensitive data found in plugin files")


if __name__ == "__main__":
    # Run tests individually for debugging
    print("🧪 Running Plugin Structure Tests")
    print("==================================")

    # Run with pytest
    pytest.main([__file__, "-v"])
