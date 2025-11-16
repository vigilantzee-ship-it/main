"""
Arena Renderer - Renders the 2D battle arena.

Draws the arena boundaries, grid, and any hazards or resources.
"""

import pygame
from ..systems.battle_spatial import SpatialBattle
from ..models.spatial import Vector2D
from ..models.pellet import Pellet


class ArenaRenderer:
    """
    Renders the 2D battle arena including boundaries and grid.
    
    Attributes:
        grid_color: Color for the grid lines
        border_color: Color for the arena border
        hazard_color: Color for hazards
        resource_color: Color for resources
        show_grid: Whether to show the grid
    """
    
    def __init__(
        self,
        grid_color: tuple = (40, 40, 50),
        border_color: tuple = (100, 100, 120),
        hazard_color: tuple = (200, 50, 50),
        resource_color: tuple = (50, 200, 100),
        show_grid: bool = False,
        pellet_renderer = None
    ):
        """
        Initialize the arena renderer.
        
        Args:
            grid_color: RGB color for grid lines
            border_color: RGB color for arena border
            hazard_color: RGB color for hazards
            resource_color: RGB color for resources (for simple Vector2D resources)
            show_grid: Whether to display the grid (default False for performance)
            pellet_renderer: Optional PelletRenderer for detailed pellet rendering
        """
        self.grid_color = grid_color
        self.border_color = border_color
        self.hazard_color = hazard_color
        self.resource_color = resource_color
        self.show_grid = show_grid
        self.pellet_renderer = pellet_renderer
        
        # Background colors
        self.bg_color = (30, 30, 40)
        self.player_side_tint = (30, 40, 50)
        self.enemy_side_tint = (50, 40, 40)
        
        # Grid cache for performance
        self._cached_grid_surface = None
        self._cached_grid_bounds = None
    
    def render(self, screen: pygame.Surface, battle: SpatialBattle):
        """
        Render the arena.
        
        Args:
            screen: Pygame surface to draw on
            battle: The spatial battle containing arena data
        """
        # Get arena bounds on screen
        bounds = self._get_arena_bounds(screen)
        x, y, width, height = bounds
        
        # Draw background with team side tints
        mid_x = x + width // 2
        
        # Player side (left) - blue tint
        player_rect = pygame.Rect(x, y, width // 2, height)
        pygame.draw.rect(screen, self.player_side_tint, player_rect)
        
        # Enemy side (right) - red tint
        enemy_rect = pygame.Rect(mid_x, y, width // 2, height)
        pygame.draw.rect(screen, self.enemy_side_tint, enemy_rect)
        
        # Draw center line
        pygame.draw.line(
            screen,
            (60, 60, 70),
            (mid_x, y),
            (mid_x, y + height),
            2
        )
        
        # Draw grid if enabled
        if self.show_grid:
            self._draw_grid(screen, bounds, battle.arena)
        
        # Draw arena border
        pygame.draw.rect(screen, self.border_color, (x, y, width, height), 3)
        
        # Draw hazards
        for hazard_pos in battle.arena.hazards:
            self._draw_hazard(screen, hazard_pos, bounds, battle.arena)
        
        # Draw resources (delegate pellets to pellet_renderer if available)
        if self.pellet_renderer:
            # Draw only simple Vector2D resources here
            for resource in battle.arena.resources:
                if isinstance(resource, Vector2D):
                    self._draw_resource(screen, resource, bounds, battle.arena)
            # Pellets will be rendered by pellet_renderer separately
        else:
            # No pellet renderer, draw all resources simply
            for resource_pos in battle.arena.resources:
                self._draw_resource(screen, resource_pos, bounds, battle.arena)
    
    def _get_arena_bounds(self, screen: pygame.Surface) -> tuple:
        """
        Get the screen bounds for the arena.
        
        Arena is positioned in the center with margins for UI panels:
        - Left: GENETIC STRAINS panel (250px)
        - Right: CREATURES + PELLET ECOSYSTEM panels (250px)
        - Top: Header/title (80px)
        - Bottom: Battle Feed (200px)
        """
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Left margin for GENETIC STRAINS panel
        ui_margin_left = 250
        # Right margin for CREATURES and PELLET ECOSYSTEM panels
        ui_margin_right = 250
        # Top margin for header/title
        ui_margin_top = 80
        # Bottom margin for Battle Feed
        ui_margin_bottom = 200
        
        x = ui_margin_left
        y = ui_margin_top
        width = screen_width - ui_margin_left - ui_margin_right
        height = screen_height - ui_margin_top - ui_margin_bottom
        
        return (x, y, width, height)
    
    def world_to_screen(
        self,
        world_pos: Vector2D,
        screen: pygame.Surface,
        arena
    ) -> tuple:
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_pos: World position to convert
            screen: Pygame surface for bounds calculation
            arena: Arena object for world dimensions
            
        Returns:
            Tuple of (screen_x, screen_y)
        """
        bounds = self._get_arena_bounds(screen)
        return self._world_to_screen(world_pos, bounds, arena)
    
    def _draw_grid(self, screen: pygame.Surface, bounds: tuple, arena):
        """Draw grid lines on the arena using cached surface when possible."""
        x, y, width, height = bounds
        
        # Check if we need to regenerate the grid cache
        if (self._cached_grid_surface is None or 
            self._cached_grid_bounds != bounds or
            self._cached_grid_surface.get_size() != (width, height)):
            # Create cached grid surface
            self._cached_grid_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            self._cached_grid_bounds = bounds
            
            # Draw vertical lines (every 10 units)
            grid_spacing_world = 10.0
            num_vertical_lines = int(arena.width / grid_spacing_world)
            
            for i in range(1, num_vertical_lines):
                world_x = i * grid_spacing_world
                screen_x = int((world_x / arena.width) * width)
                pygame.draw.line(
                    self._cached_grid_surface,
                    self.grid_color,
                    (screen_x, 0),
                    (screen_x, height),
                    1
                )
            
            # Draw horizontal lines
            num_horizontal_lines = int(arena.height / grid_spacing_world)
            
            for i in range(1, num_horizontal_lines):
                world_y = i * grid_spacing_world
                screen_y = int((world_y / arena.height) * height)
                pygame.draw.line(
                    self._cached_grid_surface,
                    self.grid_color,
                    (0, screen_y),
                    (width, screen_y),
                    1
                )
        
        # Blit the cached grid surface
        screen.blit(self._cached_grid_surface, (x, y))
    
    def _world_to_screen(
        self,
        world_pos: Vector2D,
        bounds: tuple,
        arena
    ) -> tuple:
        """Convert world coordinates to screen coordinates."""
        x, y, width, height = bounds
        
        screen_x = x + (world_pos.x / arena.width) * width
        screen_y = y + (world_pos.y / arena.height) * height
        
        return (int(screen_x), int(screen_y))
    
    def _draw_hazard(
        self,
        screen: pygame.Surface,
        hazard_pos: Vector2D,
        bounds: tuple,
        arena
    ):
        """Draw a hazard at the specified position."""
        screen_pos = self._world_to_screen(hazard_pos, bounds, arena)
        pygame.draw.circle(screen, self.hazard_color, screen_pos, 8)
        pygame.draw.circle(screen, (255, 100, 100), screen_pos, 8, 2)
    
    def _draw_resource(
        self,
        screen: pygame.Surface,
        resource_pos,
        bounds: tuple,
        arena
    ):
        """
        Draw a resource/food at the specified position.
        
        Draws simple Vector2D resources as green circles.
        Pellet objects should be rendered by PelletRenderer for detailed visualization.
        """
        # Handle both Vector2D and Pellet (for backward compatibility)
        if isinstance(resource_pos, Pellet):
            # Use pellet position
            pos = Vector2D(resource_pos.x, resource_pos.y)
        else:
            pos = resource_pos
        
        screen_pos = self._world_to_screen(pos, bounds, arena)
        # Draw food as a circle with a distinctive color
        pygame.draw.circle(screen, (80, 200, 60), screen_pos, 8)  # Green center
        pygame.draw.circle(screen, (120, 255, 100), screen_pos, 8, 2)  # Bright green outline
