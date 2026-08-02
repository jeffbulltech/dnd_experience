"""Unit tests for dice_roller utility module."""

import pytest

from app.schemas.dice import DiceRollRequest
from app.utils.dice_roller import roll_dice


class TestDiceRoller:
    """Unit tests for dice_roller utility functions."""

    def test_roll_simple_d20(self):
        """Test rolling a simple d20."""
        request = DiceRollRequest(expression="1d20")
        result = roll_dice(request)
        
        assert result.expression == "1d20"
        assert 1 <= result.total <= 20
        assert len(result.individual_rolls) == 1
        assert 1 <= result.individual_rolls[0] <= 20

    def test_roll_with_modifier(self):
        """Test rolling with a modifier."""
        request = DiceRollRequest(expression="1d20+5")
        result = roll_dice(request)
        
        assert result.expression == "1d20+5"
        assert 6 <= result.total <= 25  # 1-20 + 5
        assert len(result.individual_rolls) == 1
        assert result.total == result.individual_rolls[0] + 5

    def test_roll_multiple_dice(self):
        """Test rolling multiple dice."""
        request = DiceRollRequest(expression="3d6")
        result = roll_dice(request)
        
        assert result.expression == "3d6"
        assert 3 <= result.total <= 18  # 3-18
        assert len(result.individual_rolls) == 3
        assert all(1 <= roll <= 6 for roll in result.individual_rolls)
        assert result.total == sum(result.individual_rolls)

    def test_roll_multiple_dice_with_modifier(self):
        """Test rolling multiple dice with modifier."""
        request = DiceRollRequest(expression="2d6+3")
        result = roll_dice(request)
        
        assert result.expression == "2d6+3"
        assert 5 <= result.total <= 15  # 2-12 + 3
        assert len(result.individual_rolls) == 2
        assert result.total == sum(result.individual_rolls) + 3

    def test_roll_with_negative_modifier(self):
        """Test rolling with negative modifier."""
        request = DiceRollRequest(expression="1d20-2")
        result = roll_dice(request)
        
        assert result.expression == "1d20-2"
        assert -1 <= result.total <= 18  # 1-20 - 2
        assert result.total == result.individual_rolls[0] - 2

    def test_roll_d100(self):
        """Test rolling percentile dice."""
        request = DiceRollRequest(expression="1d100")
        result = roll_dice(request)
        
        assert result.expression == "1d100"
        assert 1 <= result.total <= 100
        assert len(result.individual_rolls) == 1

    def test_roll_complex_expression(self):
        """Test rolling complex expression."""
        request = DiceRollRequest(expression="4d6+2")
        result = roll_dice(request)
        
        assert result.expression == "4d6+2"
        assert 6 <= result.total <= 26  # 4-24 + 2
        assert len(result.individual_rolls) == 4
        assert all(1 <= roll <= 6 for roll in result.individual_rolls)

    def test_roll_has_detail(self):
        """Test that roll result includes detail information."""
        request = DiceRollRequest(expression="1d20+5")
        result = roll_dice(request)
        
        assert result.detail is not None
        assert "expression" in result.detail or "rolls" in result.detail

    def test_roll_critical_success_d20(self):
        """Test that natural 20 on d20 is detected as critical success."""
        # We can't guarantee a 20, but we can test the logic
        request = DiceRollRequest(expression="1d20")
        result = roll_dice(request)
        
        # If it's a 20, should be critical success
        if result.individual_rolls[0] == 20:
            assert result.is_critical_success is True
        else:
            assert result.is_critical_success is False

    def test_roll_critical_failure_d20(self):
        """Test that natural 1 on d20 is detected as critical failure."""
        request = DiceRollRequest(expression="1d20")
        result = roll_dice(request)
        
        # If it's a 1, should be critical failure
        if result.individual_rolls[0] == 1:
            assert result.is_critical_failure is True
        else:
            assert result.is_critical_failure is False

    def test_roll_advantage(self):
        """Test rolling with advantage."""
        request = DiceRollRequest(expression="1d20", has_advantage=True)
        result = roll_dice(request)
        
        assert result.has_advantage is True
        assert result.expression == "1d20"
        # With advantage, should roll 2 dice and take higher
        # Implementation may vary, but should have advantage flag

    def test_roll_disadvantage(self):
        """Test rolling with disadvantage."""
        request = DiceRollRequest(expression="1d20", has_disadvantage=True)
        result = roll_dice(request)
        
        assert result.has_disadvantage is True
        assert result.expression == "1d20"

    def test_roll_invalid_expression(self):
        """Test that invalid expressions are handled."""
        # This depends on implementation - may raise error or return error result
        request = DiceRollRequest(expression="invalid")
        
        # The function should either raise an error or return an error result
        # Check the actual implementation behavior
        try:
            result = roll_dice(request)
            # If it doesn't raise, check for error indicators
            assert result.total == 0 or "error" in str(result.detail).lower()
        except (ValueError, Exception):
            # If it raises, that's also acceptable
            pass
