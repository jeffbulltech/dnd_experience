"""Unit tests for inventory_service module."""

import pytest

from app.schemas.inventory import InventoryItemCreate, InventoryItemUpdate
from app.services import inventory_service
from tests.fixtures.characters import create_test_character
from tests.fixtures.users import create_test_user


class TestInventoryService:
    """Unit tests for inventory_service functions."""

    def test_create_inventory_item_success(self, db_session):
        """Test successful inventory item creation."""
        user = create_test_user(db_session)
        character = create_test_character(db_session, user.id)
        
        payload = InventoryItemCreate(
            character_id=character.id,
            name="Longsword",
            quantity=1,
            weight=3.0,
            description="A well-crafted longsword",
            properties={"damage": "1d8 slashing", "properties": ["versatile"]}
        )
        
        result = inventory_service.create_inventory_item(db_session, payload)
        
        assert result.id > 0
        assert result.character_id == character.id
        assert result.name == "Longsword"
        assert result.quantity == 1
        assert result.weight == 3.0
        assert result.description == "A well-crafted longsword"
        assert result.properties == {"damage": "1d8 slashing", "properties": ["versatile"]}

    def test_create_inventory_item_minimal(self, db_session):
        """Test creating inventory item with only required fields."""
        user = create_test_user(db_session)
        character = create_test_character(db_session, user.id)
        
        payload = InventoryItemCreate(
            character_id=character.id,
            name="Simple Item",
            quantity=1
        )
        
        result = inventory_service.create_inventory_item(db_session, payload)
        
        assert result.name == "Simple Item"
        assert result.quantity == 1
        assert result.weight is None
        assert result.description is None
        assert result.properties == {}

    def test_list_inventory_items_by_character(self, db_session):
        """Test listing inventory items filtered by character."""
        user = create_test_user(db_session)
        char1 = create_test_character(db_session, user.id, name="Char 1")
        char2 = create_test_character(db_session, user.id, name="Char 2")
        
        item1 = inventory_service.create_inventory_item(
            db_session,
            InventoryItemCreate(character_id=char1.id, name="Item 1", quantity=1)
        )
        item2 = inventory_service.create_inventory_item(
            db_session,
            InventoryItemCreate(character_id=char2.id, name="Item 2", quantity=1)
        )
        
        char1_items = inventory_service.list_inventory_items(
            db_session, character_id=char1.id
        )
        
        assert len(char1_items) == 1
        assert char1_items[0].id == item1.id
        assert char1_items[0].id != item2.id

    def test_list_inventory_items_all(self, db_session):
        """Test listing all inventory items without filter."""
        user = create_test_user(db_session)
        character = create_test_character(db_session, user.id)
        
        inventory_service.create_inventory_item(
            db_session,
            InventoryItemCreate(character_id=character.id, name="Item 1", quantity=1)
        )
        inventory_service.create_inventory_item(
            db_session,
            InventoryItemCreate(character_id=character.id, name="Item 2", quantity=2)
        )
        
        all_items = inventory_service.list_inventory_items(db_session)
        
        assert len(all_items) == 2

    def test_list_inventory_items_empty(self, db_session):
        """Test listing items when none exist."""
        items = inventory_service.list_inventory_items(db_session)
        assert len(items) == 0

    def test_update_inventory_item_success(self, db_session):
        """Test successful inventory item update."""
        user = create_test_user(db_session)
        character = create_test_character(db_session, user.id)
        
        item = inventory_service.create_inventory_item(
            db_session,
            InventoryItemCreate(
                character_id=character.id,
                name="Original Name",
                quantity=1,
                weight=1.0
            )
        )
        
        update = InventoryItemUpdate(
            name="Updated Name",
            quantity=5,
            weight=2.5
        )
        
        result = inventory_service.update_inventory_item(
            db_session, item.id, update
        )
        
        assert result.name == "Updated Name"
        assert result.quantity == 5
        assert result.weight == 2.5

    def test_update_inventory_item_partial(self, db_session):
        """Test that partial updates only change specified fields."""
        user = create_test_user(db_session)
        character = create_test_character(db_session, user.id)
        
        item = inventory_service.create_inventory_item(
            db_session,
            InventoryItemCreate(
                character_id=character.id,
                name="Original",
                quantity=1,
                weight=1.0,
                description="Original description"
            )
        )
        
        # Only update quantity
        update = InventoryItemUpdate(quantity=10)
        result = inventory_service.update_inventory_item(
            db_session, item.id, update
        )
        
        assert result.quantity == 10
        assert result.name == "Original"  # Unchanged
        assert result.weight == 1.0  # Unchanged
        assert result.description == "Original description"  # Unchanged

    def test_update_inventory_item_properties(self, db_session):
        """Test updating item properties."""
        user = create_test_user(db_session)
        character = create_test_character(db_session, user.id)
        
        item = inventory_service.create_inventory_item(
            db_session,
            InventoryItemCreate(
                character_id=character.id,
                name="Magic Item",
                quantity=1,
                properties={"rarity": "uncommon"}
            )
        )
        
        update = InventoryItemUpdate(
            properties={"rarity": "rare", "attunement": True}
        )
        
        result = inventory_service.update_inventory_item(
            db_session, item.id, update
        )
        
        assert result.properties == {"rarity": "rare", "attunement": True}

    def test_update_inventory_item_not_found(self, db_session):
        """Test updating non-existent inventory item."""
        update = InventoryItemUpdate(quantity=5)
        
        with pytest.raises(ValueError, match="Inventory item not found"):
            inventory_service.update_inventory_item(db_session, 99999, update)

    def test_delete_inventory_item_success(self, db_session):
        """Test successful inventory item deletion."""
        user = create_test_user(db_session)
        character = create_test_character(db_session, user.id)
        
        item = inventory_service.create_inventory_item(
            db_session,
            InventoryItemCreate(character_id=character.id, name="To Delete", quantity=1)
        )
        item_id = item.id
        
        inventory_service.delete_inventory_item(db_session, item_id)
        
        # Verify item is deleted
        from app.models import InventoryItem
        assert db_session.get(InventoryItem, item_id) is None

    def test_delete_inventory_item_not_found(self, db_session):
        """Test deleting non-existent inventory item."""
        with pytest.raises(ValueError, match="Inventory item not found"):
            inventory_service.delete_inventory_item(db_session, 99999)

    def test_inventory_item_quantity_zero(self, db_session):
        """Test that quantity can be set to zero."""
        user = create_test_user(db_session)
        character = create_test_character(db_session, user.id)
        
        item = inventory_service.create_inventory_item(
            db_session,
            InventoryItemCreate(character_id=character.id, name="Item", quantity=5)
        )
        
        update = InventoryItemUpdate(quantity=0)
        result = inventory_service.update_inventory_item(
            db_session, item.id, update
        )
        
        assert result.quantity == 0
