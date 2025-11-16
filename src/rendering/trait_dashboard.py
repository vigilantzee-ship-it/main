"""
Trait Analytics Dashboard - UI component for visualizing trait data.

Displays:
- Total trait statistics
- Most successful traits
- Recent trait discoveries and injections
- Generation-by-generation trait timeline
- Export options
"""

import pygame
from typing import Optional, List, Dict, Any, Tuple
from ..models.trait_analytics import TraitAnalytics


class TraitAnalyticsDashboard:
    """
    Interactive dashboard for trait analytics visualization.
    
    Shows comprehensive trait data including discoveries, spread,
    injections, and success metrics.
    """
    
    def __init__(self, analytics: TraitAnalytics):
        """
        Initialize the dashboard.
        
        Args:
            analytics: TraitAnalytics instance to visualize
        """
        pygame.font.init()
        
        self.analytics = analytics
        
        # Fonts
        self.title_font = pygame.font.Font(None, 32)
        self.header_font = pygame.font.Font(None, 24)
        self.text_font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        
        # Colors
        self.bg_color = (20, 20, 30, 240)
        self.panel_color = (40, 40, 50)
        self.header_color = (60, 60, 80)
        self.text_color = (255, 255, 255)
        self.highlight_color = (100, 200, 255)
        self.success_color = (100, 255, 150)
        self.warning_color = (255, 200, 100)
        self.legendary_color = (255, 215, 0)
        
        # Layout
        self.visible = False
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Dimensions (will be calculated based on screen size)
        self.width = 800
        self.height = 600
        self.margin = 20
        self.line_height = 22
        self.section_spacing = 15
        
        # Cached dashboard data
        self.cached_data = None
        self.data_cache_time = 0
        self.cache_duration = 1.0  # Refresh every second
    
    def toggle(self):
        """Toggle dashboard visibility."""
        self.visible = not self.visible
        if self.visible:
            self.refresh_data()
    
    def show(self):
        """Show the dashboard."""
        self.visible = True
        self.refresh_data()
    
    def hide(self):
        """Hide the dashboard."""
        self.visible = False
    
    def refresh_data(self):
        """Refresh cached dashboard data."""
        import time
        current_time = time.time()
        
        # Only refresh if cache is stale
        if current_time - self.data_cache_time > self.cache_duration:
            self.cached_data = self.analytics.get_dashboard_data()
            self.data_cache_time = current_time
    
    def handle_event(self, event: pygame.event.Event, screen_width: int, screen_height: int) -> bool:
        """
        Handle input events.
        
        Args:
            event: Pygame event
            screen_width: Screen width
            screen_height: Screen height
            
        Returns:
            True if event was handled
        """
        if not self.visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d and pygame.key.get_mods() & pygame.KMOD_CTRL:
                # Ctrl+D to toggle dashboard
                self.toggle()
                return True
            elif event.key == pygame.K_ESCAPE:
                self.hide()
                return True
        
        elif event.type == pygame.MOUSEWHEEL:
            # Scroll with mouse wheel
            self.scroll_offset -= event.y * 30
            self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
            return True
        
        return False
    
    def render(self, screen: pygame.Surface):
        """
        Render the dashboard.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.visible:
            return
        
        screen_width, screen_height = screen.get_size()
        
        # Calculate dimensions
        self.width = min(900, screen_width - 100)
        self.height = min(700, screen_height - 100)
        
        # Center position
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        
        # Create panel surface
        panel = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        panel.fill(self.bg_color)
        
        # Draw border
        pygame.draw.rect(panel, self.highlight_color, panel.get_rect(), 3)
        
        # Title bar
        title_height = 40
        title_bar = pygame.Rect(0, 0, self.width, title_height)
        pygame.draw.rect(panel, self.header_color, title_bar)
        
        title_text = self.title_font.render("Trait Analytics Dashboard", True, self.text_color)
        panel.blit(title_text, (self.margin, 8))
        
        # Close button
        close_text = self.text_font.render("✕", True, self.warning_color)
        panel.blit(close_text, (self.width - 40, 10))
        
        # Render content with scrolling
        if self.cached_data is None:
            self.refresh_data()
        
        content_surface = self._render_content()
        
        # Calculate max scroll
        self.max_scroll = max(0, content_surface.get_height() - self.height + title_height + 20)
        
        # Blit scrolled content
        content_y = title_height + 10
        panel.blit(content_surface, (0, content_y - self.scroll_offset))
        
        # Draw to screen
        screen.blit(panel, (x, y))
        
        # Draw hint
        hint_text = self.small_font.render(
            "Ctrl+D to toggle  •  ESC to close  •  Mouse wheel to scroll",
            True,
            (200, 200, 200)
        )
        screen.blit(hint_text, (x + 10, y + self.height + 5))
    
    def _render_content(self) -> pygame.Surface:
        """
        Render all dashboard content.
        
        Returns:
            Surface with content
        """
        if self.cached_data is None:
            # Empty surface if no data
            surface = pygame.Surface((self.width, 100), pygame.SRCALPHA)
            no_data_text = self.text_font.render("No data available", True, self.text_color)
            surface.blit(no_data_text, (self.margin, self.margin))
            return surface
        
        # Estimate height
        estimated_height = 1500
        content = pygame.Surface((self.width, estimated_height), pygame.SRCALPHA)
        
        y = self.margin
        x_margin = self.margin
        
        # === Statistics Overview ===
        y = self._render_stats_overview(content, x_margin, y)
        y += self.section_spacing
        
        # === Top Traits ===
        y = self._render_top_traits(content, x_margin, y)
        y += self.section_spacing
        
        # === Recent Events ===
        y = self._render_recent_events(content, x_margin, y)
        y += self.section_spacing
        
        # Crop to actual height
        actual_surface = pygame.Surface((self.width, y + self.margin), pygame.SRCALPHA)
        actual_surface.blit(content, (0, 0))
        
        return actual_surface
    
    def _render_stats_overview(self, surface: pygame.Surface, x: int, y: int) -> int:
        """Render statistics overview section."""
        # Header
        header = self.header_font.render("Statistics Overview", True, self.highlight_color)
        surface.blit(header, (x, y))
        y += header.get_height() + 10
        
        stats = self.cached_data['statistics']
        
        # Create stat boxes
        stat_items = [
            ("Total Discoveries", stats['total_discoveries'], self.success_color),
            ("Total Injections", stats['total_injections'], self.warning_color),
            ("Active Traits", stats['active_traits'], self.highlight_color),
            ("Unique Traits Ever", stats['unique_traits_ever'], self.legendary_color)
        ]
        
        box_width = (self.width - 3 * self.margin - x) // 4
        box_height = 70
        
        for i, (label, value, color) in enumerate(stat_items):
            box_x = x + i * (box_width + 10)
            
            # Box background
            box_rect = pygame.Rect(box_x, y, box_width, box_height)
            pygame.draw.rect(surface, self.panel_color, box_rect)
            pygame.draw.rect(surface, color, box_rect, 2)
            
            # Value (large)
            value_text = self.header_font.render(str(value), True, color)
            value_x = box_x + (box_width - value_text.get_width()) // 2
            surface.blit(value_text, (value_x, y + 10))
            
            # Label (small)
            label_text = self.small_font.render(label, True, self.text_color)
            label_x = box_x + (box_width - label_text.get_width()) // 2
            surface.blit(label_text, (label_x, y + 45))
        
        return y + box_height + 15
    
    def _render_top_traits(self, surface: pygame.Surface, x: int, y: int) -> int:
        """Render top traits section."""
        # Header
        header = self.header_font.render("Most Successful Traits", True, self.highlight_color)
        surface.blit(header, (x, y))
        y += header.get_height() + 10
        
        top_traits = self.cached_data['top_traits']
        
        if not top_traits:
            no_traits = self.text_font.render("No traits recorded yet", True, (150, 150, 150))
            surface.blit(no_traits, (x + 10, y))
            return y + self.line_height
        
        # Table header
        headers = ["Rank", "Trait Name", "Carriers", "Total", "Generations", "Survival"]
        header_x = x + 10
        
        for i, header_text in enumerate(headers):
            col_x = header_x + i * 120
            text = self.small_font.render(header_text, True, (180, 180, 180))
            surface.blit(text, (col_x, y))
        
        y += self.line_height + 5
        
        # Traits
        for rank, trait_data in enumerate(top_traits[:10], 1):
            # Rank with medal for top 3
            rank_text = str(rank)
            if rank == 1:
                rank_text = "🥇"
            elif rank == 2:
                rank_text = "🥈"
            elif rank == 3:
                rank_text = "🥉"
            
            rank_render = self.text_font.render(rank_text, True, self.text_color)
            surface.blit(rank_render, (header_x, y))
            
            # Trait name (truncate if needed)
            name = trait_data['name'][:20]
            name_render = self.text_font.render(name, True, self.highlight_color)
            surface.blit(name_render, (header_x + 60, y))
            
            # Stats
            stats_data = [
                str(trait_data['carriers']),
                str(trait_data['total_ever']),
                str(trait_data['generations']),
                trait_data['survival_rate']
            ]
            
            for i, stat in enumerate(stats_data):
                col_x = header_x + (i + 2) * 120
                stat_render = self.text_font.render(stat, True, self.text_color)
                surface.blit(stat_render, (col_x, y))
            
            y += self.line_height
        
        return y
    
    def _render_recent_events(self, surface: pygame.Surface, x: int, y: int) -> int:
        """Render recent events section."""
        # Header
        header = self.header_font.render("Recent Trait Events", True, self.highlight_color)
        surface.blit(header, (x, y))
        y += header.get_height() + 10
        
        recent_events = self.cached_data['recent_events']
        
        if not recent_events:
            no_events = self.text_font.render("No events recorded yet", True, (150, 150, 150))
            surface.blit(no_events, (x + 10, y))
            return y + self.line_height
        
        # Events timeline
        for event in recent_events:
            # Event type icon
            event_icons = {
                'discovery': "🔍",
                'injection': "💉"
            }
            icon = event_icons.get(event['type'], "•")
            icon_render = self.text_font.render(icon, True, self.highlight_color)
            surface.blit(icon_render, (x + 10, y))
            
            # Event details
            event_type = event['type'].title()
            trait_name = event['trait']
            generation = event['generation']
            
            detail_text = f"{event_type}: {trait_name} (Gen {generation})"
            detail_render = self.text_font.render(detail_text, True, self.text_color)
            surface.blit(detail_render, (x + 40, y))
            
            # Time
            time_text = event['time']
            time_render = self.small_font.render(time_text, True, (150, 150, 150))
            time_x = self.width - self.margin - time_render.get_width() - 20
            surface.blit(time_render, (time_x, y + 2))
            
            y += self.line_height
        
        return y
    
    def _render_section_header(self, surface: pygame.Surface, text: str, x: int, y: int) -> int:
        """Render a section header."""
        header = self.header_font.render(text, True, self.highlight_color)
        surface.blit(header, (x, y))
        
        # Underline
        line_y = y + header.get_height() + 2
        pygame.draw.line(surface, self.highlight_color, (x, line_y), (self.width - self.margin, line_y), 2)
        
        return line_y + 8
