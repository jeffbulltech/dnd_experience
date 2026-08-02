"""Unit tests for adventure_service module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from app.services import adventure_service


class TestAdventureService:
    """Unit tests for adventure_service functions."""

    def test_list_adventure_templates_success(self, tmp_path):
        """Test listing adventure templates when directory exists with valid files."""
        # Create temporary adventures directory
        adventures_dir = tmp_path / "adventures"
        adventures_dir.mkdir()
        
        # Create test adventure files
        adventure1 = {
            "id": "test-adventure-1",
            "name": "Test Adventure One",
            "description": "First test adventure",
            "level_range": "1-5",
            "setting": "Test Setting",
            "seed_content": "Test seed content"
        }
        adventure2 = {
            "id": "test-adventure-2",
            "name": "Another Adventure",
            "description": "Second test adventure",
            "level_range": "3-7",
            "setting": "Another Setting",
            "seed_content": "More seed content"
        }
        
        (adventures_dir / "test-adventure-1.json").write_text(
            json.dumps(adventure1), encoding="utf-8"
        )
        (adventures_dir / "test-adventure-2.json").write_text(
            json.dumps(adventure2), encoding="utf-8"
        )
        
        # Patch the ADVENTURES_DIR
        with patch("app.services.adventure_service.ADVENTURES_DIR", adventures_dir):
            templates = adventure_service.list_adventure_templates()
        
        assert len(templates) == 2
        # Should be sorted by name
        assert templates[0].name == "Another Adventure"
        assert templates[1].name == "Test Adventure One"
        assert templates[0].id == "test-adventure-2"
        assert templates[1].id == "test-adventure-1"

    def test_list_adventure_templates_empty_directory(self, tmp_path):
        """Test listing when directory exists but is empty."""
        adventures_dir = tmp_path / "adventures"
        adventures_dir.mkdir()
        
        with patch("app.services.adventure_service.ADVENTURES_DIR", adventures_dir):
            templates = adventure_service.list_adventure_templates()
        
        assert len(templates) == 0

    def test_list_adventure_templates_directory_not_exists(self, tmp_path):
        """Test listing when adventures directory doesn't exist."""
        adventures_dir = tmp_path / "nonexistent"
        
        with patch("app.services.adventure_service.ADVENTURES_DIR", adventures_dir):
            templates = adventure_service.list_adventure_templates()
        
        assert len(templates) == 0

    def test_list_adventure_templates_skips_invalid_json(self, tmp_path):
        """Test that invalid JSON files are skipped."""
        adventures_dir = tmp_path / "adventures"
        adventures_dir.mkdir()
        
        # Valid JSON
        valid_adventure = {
            "id": "valid",
            "name": "Valid Adventure",
            "description": "Valid",
            "level_range": "1-5",
            "setting": "Test",
            "seed_content": "Content"
        }
        (adventures_dir / "valid.json").write_text(
            json.dumps(valid_adventure), encoding="utf-8"
        )
        
        # Invalid JSON
        (adventures_dir / "invalid.json").write_text("not valid json", encoding="utf-8")
        
        # Missing required fields
        incomplete = {"id": "incomplete", "name": "Incomplete"}
        (adventures_dir / "incomplete.json").write_text(
            json.dumps(incomplete), encoding="utf-8"
        )
        
        with patch("app.services.adventure_service.ADVENTURES_DIR", adventures_dir):
            templates = adventure_service.list_adventure_templates()
        
        # Should only return the valid one
        assert len(templates) == 1
        assert templates[0].id == "valid"

    def test_get_adventure_template_success(self, tmp_path):
        """Test retrieving a specific adventure template."""
        adventures_dir = tmp_path / "adventures"
        adventures_dir.mkdir()
        
        adventure_data = {
            "id": "specific-adventure",
            "name": "Specific Adventure",
            "description": "A specific adventure",
            "level_range": "1-10",
            "setting": "Fantasy World",
            "seed_content": "Detailed seed content here"
        }
        
        (adventures_dir / "specific-adventure.json").write_text(
            json.dumps(adventure_data), encoding="utf-8"
        )
        
        with patch("app.services.adventure_service.ADVENTURES_DIR", adventures_dir):
            template = adventure_service.get_adventure_template("specific-adventure")
        
        assert template is not None
        assert template.id == "specific-adventure"
        assert template.name == "Specific Adventure"
        assert template.description == "A specific adventure"
        assert template.level_range == "1-10"
        assert template.setting == "Fantasy World"
        assert template.seed_content == "Detailed seed content here"

    def test_get_adventure_template_not_found(self, tmp_path):
        """Test retrieving non-existent adventure template."""
        adventures_dir = tmp_path / "adventures"
        adventures_dir.mkdir()
        
        with patch("app.services.adventure_service.ADVENTURES_DIR", adventures_dir):
            template = adventure_service.get_adventure_template("nonexistent")
        
        assert template is None

    def test_get_adventure_template_custom_returns_none(self):
        """Test that 'custom' template ID returns None."""
        template = adventure_service.get_adventure_template("custom")
        assert template is None

    def test_get_adventure_seed_content_success(self, tmp_path):
        """Test retrieving seed content for an adventure."""
        adventures_dir = tmp_path / "adventures"
        adventures_dir.mkdir()
        
        adventure_data = {
            "id": "seed-test",
            "name": "Seed Test",
            "description": "Test",
            "level_range": "1-5",
            "setting": "Test",
            "seed_content": "This is the seed content for the adventure"
        }
        
        (adventures_dir / "seed-test.json").write_text(
            json.dumps(adventure_data), encoding="utf-8"
        )
        
        with patch("app.services.adventure_service.ADVENTURES_DIR", adventures_dir):
            seed = adventure_service.get_adventure_seed_content("seed-test")
        
        assert seed == "This is the seed content for the adventure"

    def test_get_adventure_seed_content_none_returns_empty(self):
        """Test that None template_id returns empty string."""
        seed = adventure_service.get_adventure_seed_content(None)
        assert seed == ""

    def test_get_adventure_seed_content_custom_returns_empty(self):
        """Test that 'custom' template_id returns empty string."""
        seed = adventure_service.get_adventure_seed_content("custom")
        assert seed == ""

    def test_get_adventure_seed_content_not_found_returns_empty(self, tmp_path):
        """Test that non-existent template returns empty string."""
        adventures_dir = tmp_path / "adventures"
        adventures_dir.mkdir()
        
        with patch("app.services.adventure_service.ADVENTURES_DIR", adventures_dir):
            seed = adventure_service.get_adventure_seed_content("nonexistent")
        
        assert seed == ""

    def test_adventure_template_to_dict(self, tmp_path):
        """Test AdventureTemplate.to_dict() method."""
        adventures_dir = tmp_path / "adventures"
        adventures_dir.mkdir()
        
        adventure_data = {
            "id": "dict-test",
            "name": "Dict Test",
            "description": "Test dict conversion",
            "level_range": "1-5",
            "setting": "Test Setting",
            "seed_content": "Content"
        }
        
        (adventures_dir / "dict-test.json").write_text(
            json.dumps(adventure_data), encoding="utf-8"
        )
        
        with patch("app.services.adventure_service.ADVENTURES_DIR", adventures_dir):
            template = adventure_service.get_adventure_template("dict-test")
        
        assert template is not None
        result_dict = template.to_dict()
        
        assert result_dict["id"] == "dict-test"
        assert result_dict["name"] == "Dict Test"
        assert result_dict["description"] == "Test dict conversion"
        assert result_dict["level_range"] == "1-5"
        assert result_dict["setting"] == "Test Setting"
        # seed_content should NOT be in to_dict output
        assert "seed_content" not in result_dict

    def test_adventure_template_defaults(self, tmp_path):
        """Test that AdventureTemplate uses default values for optional fields."""
        adventures_dir = tmp_path / "adventures"
        adventures_dir.mkdir()
        
        # Minimal adventure data (only required fields)
        adventure_data = {
            "id": "minimal",
            "name": "Minimal Adventure",
            "description": "Minimal description"
        }
        
        (adventures_dir / "minimal.json").write_text(
            json.dumps(adventure_data), encoding="utf-8"
        )
        
        with patch("app.services.adventure_service.ADVENTURES_DIR", adventures_dir):
            template = adventure_service.get_adventure_template("minimal")
        
        assert template is not None
        assert template.level_range == "1-20"  # Default
        assert template.setting == "Custom"  # Default
        assert template.seed_content == ""  # Default
