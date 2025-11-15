"""
Tests for pellet rendering components.

Ensures pellet renderer works correctly with pellets and integrates
with the rendering system.
"""

import unittest
import pygame
from src.models.pellet import Pellet, create_random_pellet, PelletTraits
from src.models.creature import Creature
from src.models.spatial import Arena, Vector2D
from src.systems.battle_spatial import SpatialBattle
from src.rendering.pellet_renderer import PelletRenderer
from src.rendering.arena_renderer import ArenaRenderer
from src.rendering.ui_components import UIComponents


class TestPelletRenderer(unittest.TestCase):
    """Test cases for PelletRenderer."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize pygame once for all tests."""
        pygame.init()
        cls.screen = pygame.display.set_mode((800, 600))
    
    @classmethod
    def tearDownClass(cls):
        """Clean up pygame."""
        pygame.quit()
    
    def test_pellet_renderer_initialization(self):
        """Test that PelletRenderer can be initialized."""
        renderer = PelletRenderer()
        self.assertIsNotNone(renderer)
        self.assertEqual(renderer.base_radius, 6)
        self.assertTrue(renderer.show_generation)
    
    def test_pellet_renderer_with_custom_settings(self):
        """Test PelletRenderer with custom settings."""
        renderer = PelletRenderer(
            base_radius=10,
            show_generation=False,
            show_stats_on_hover=True
        )
        self.assertEqual(renderer.base_radius, 10)
        self.assertFalse(renderer.show_generation)
        self.assertTrue(renderer.show_stats_on_hover)
    
    def test_render_simple_pellet(self):
        """Test rendering a simple pellet."""
        # Create test pellet
        pellet = Pellet(
            x=50.0,
            y=50.0,
            traits=PelletTraits(
                color=(100, 200, 100),
                size=1.0,
                nutritional_value=40.0
            )
        )
        
        # Create battle with pellet
        creature = Creature(name="TestCreature", hunger=100)
        battle = SpatialBattle([creature], arena_width=100, arena_height=100)
        battle.arena.add_pellet(pellet)
        
        # Create renderer and render
        renderer = PelletRenderer()
        self.assertIsNotNone(renderer)
        
        # Should not raise any exceptions
        renderer.render(self.screen, battle)
    
    def test_render_evolved_pellet(self):
        """Test rendering an evolved pellet with generation marker."""
        # Create evolved pellet
        pellet = Pellet(
            x=50.0,
            y=50.0,
            generation=5,
            traits=PelletTraits(
                color=(150, 220, 150),
                size=1.2,
                nutritional_value=60.0
            )
        )
        
        # Create battle with pellet
        creature = Creature(name="TestCreature", hunger=100)
        battle = SpatialBattle([creature], arena_width=100, arena_height=100)
        battle.arena.add_pellet(pellet)
        
        # Create renderer with generation display
        renderer = PelletRenderer(show_generation=True)
        
        # Should not raise any exceptions
        renderer.render(self.screen, battle)
    
    def test_render_toxic_pellet(self):
        """Test rendering a toxic pellet (should appear darker)."""
        # Create toxic pellet
        pellet = Pellet(
            x=50.0,
            y=50.0,
            traits=PelletTraits(
                color=(200, 100, 200),
                toxicity=0.5,  # 50% toxic
                nutritional_value=40.0
            )
        )
        
        # Create battle with pellet
        creature = Creature(name="TestCreature", hunger=100)
        battle = SpatialBattle([creature], arena_width=100, arena_height=100)
        battle.arena.add_pellet(pellet)
        
        # Create renderer
        renderer = PelletRenderer()
        
        # Should not raise any exceptions
        renderer.render(self.screen, battle)
    
    def test_render_multiple_pellets(self):
        """Test rendering multiple pellets at once."""
        # Create several pellets
        pellets = [
            create_random_pellet(20, 20, generation=0),
            create_random_pellet(40, 40, generation=1),
            create_random_pellet(60, 60, generation=2),
            create_random_pellet(80, 80, generation=3),
        ]
        
        # Create battle without initial resources
        creature = Creature(name="TestCreature", hunger=100)
        battle = SpatialBattle([creature], arena_width=100, arena_height=100, initial_resources=0)
        for pellet in pellets:
            battle.arena.add_pellet(pellet)
        
        # Create renderer
        renderer = PelletRenderer()
        
        # Should not raise any exceptions
        renderer.render(self.screen, battle)
        
        # Verify our pellets are in battle
        self.assertEqual(len(battle.arena.pellets), 4)


class TestArenaRendererWithPellets(unittest.TestCase):
    """Test ArenaRenderer integration with pellets."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize pygame once for all tests."""
        pygame.init()
        cls.screen = pygame.display.set_mode((800, 600))
    
    @classmethod
    def tearDownClass(cls):
        """Clean up pygame."""
        pygame.quit()
    
    def test_arena_renderer_with_pellet_renderer(self):
        """Test ArenaRenderer using PelletRenderer for pellets."""
        # Create pellet and simple resource
        pellet = create_random_pellet(50, 50)
        
        # Create battle
        creature = Creature(name="TestCreature", hunger=100)
        battle = SpatialBattle([creature], arena_width=100, arena_height=100)
        battle.arena.add_pellet(pellet)
        
        # Create renderers
        pellet_renderer = PelletRenderer()
        arena_renderer = ArenaRenderer(pellet_renderer=pellet_renderer)
        
        # Should not raise any exceptions
        arena_renderer.render(self.screen, battle)
    
    def test_arena_renderer_backward_compatibility(self):
        """Test ArenaRenderer works without pellet_renderer (backward compatibility)."""
        # Create pellet
        pellet = create_random_pellet(50, 50)
        
        # Create battle
        creature = Creature(name="TestCreature", hunger=100)
        battle = SpatialBattle([creature], arena_width=100, arena_height=100)
        battle.arena.add_pellet(pellet)
        
        # Create arena renderer without pellet renderer
        arena_renderer = ArenaRenderer()
        
        # Should not raise any exceptions (renders pellets as simple resources)
        arena_renderer.render(self.screen, battle)
    
    def test_arena_renderer_mixed_resources(self):
        """Test ArenaRenderer with both Pellet and Vector2D resources."""
        # Create pellet and Vector2D resource
        pellet = create_random_pellet(50, 50)
        vector_resource = Vector2D(70, 70)
        
        # Create battle without initial resources
        creature = Creature(name="TestCreature", hunger=100)
        battle = SpatialBattle([creature], arena_width=100, arena_height=100, initial_resources=0)
        battle.arena.add_pellet(pellet)
        battle.arena.resources.append(vector_resource)
        
        # Create renderers
        pellet_renderer = PelletRenderer()
        arena_renderer = ArenaRenderer(pellet_renderer=pellet_renderer)
        
        # Should not raise any exceptions
        arena_renderer.render(self.screen, battle)
        
        # Verify both resources are present
        self.assertEqual(len(battle.arena.resources), 2)


class TestUIComponentsWithPellets(unittest.TestCase):
    """Test UI components with pellet statistics."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize pygame once for all tests."""
        pygame.init()
        cls.screen = pygame.display.set_mode((800, 600))
    
    @classmethod
    def tearDownClass(cls):
        """Clean up pygame."""
        pygame.quit()
    
    def test_ui_components_with_pellet_stats(self):
        """Test UI components rendering pellet statistics panel."""
        # Create battle with pellets
        creature = Creature(name="TestCreature", hunger=100)
        battle = SpatialBattle([creature], arena_width=100, arena_height=100)
        
        # Add several pellets with varying traits
        for i in range(10):
            pellet = create_random_pellet(i * 10, i * 10, generation=i % 5)
            battle.arena.add_pellet(pellet)
        
        # Create UI components with pellet stats enabled
        ui = UIComponents(show_pellet_stats=True)
        
        # Should not raise any exceptions
        ui.render(self.screen, battle, paused=False)
    
    def test_ui_components_without_pellet_stats(self):
        """Test UI components with pellet stats disabled."""
        # Create battle with pellets
        creature = Creature(name="TestCreature", hunger=100)
        battle = SpatialBattle([creature], arena_width=100, arena_height=100)
        
        # Add pellets
        for i in range(5):
            battle.arena.add_pellet(create_random_pellet(i * 20, i * 20))
        
        # Create UI components with pellet stats disabled
        ui = UIComponents(show_pellet_stats=False)
        
        # Should not raise any exceptions
        ui.render(self.screen, battle, paused=False)
    
    def test_ui_components_empty_pellets(self):
        """Test UI components when no pellets exist."""
        # Create battle with no pellets
        creature = Creature(name="TestCreature", hunger=100)
        battle = SpatialBattle([creature], arena_width=100, arena_height=100, initial_resources=0)
        
        # Create UI components with pellet stats enabled
        ui = UIComponents(show_pellet_stats=True)
        
        # Should not raise any exceptions (panel should not render)
        ui.render(self.screen, battle, paused=False)


if __name__ == '__main__':
    unittest.main()
