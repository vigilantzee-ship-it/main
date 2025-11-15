"""
Post-Game Summary - Battle results and statistics screen.

Displays comprehensive battle results, final stats, achievements,
and provides options to export data or continue playing.
"""

import pygame
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from ..systems.battle_spatial import SpatialBattle, BattleCreature


class PostGameSummary:
    """
    Post-game summary screen showing battle results and statistics.
    
    Displays:
    - Final battle outcome (winner/survivors)
    - Battle duration and statistics
    - Per-creature breakdown with kills, damage, etc.
    - Achievements earned
    - Export and replay options
    
    Attributes:
        visible: Whether the summary is currently displayed
        battle: The completed battle to summarize
        stats: Compiled battle statistics
    """
    
    def __init__(self):
        """Initialize the post-game summary."""
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 56)
        self.header_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 22)
        self.small_font = pygame.font.Font(None, 18)
        
        # Colors
        self.bg_color = (20, 20, 30)
        self.overlay_color = (0, 0, 0, 180)
        self.text_color = (255, 255, 255)
        self.highlight_color = (100, 200, 255)
        self.success_color = (100, 255, 150)
        self.warning_color = (255, 200, 100)
        self.error_color = (255, 100, 100)
        
        # State
        self.visible = False
        self.battle: Optional[SpatialBattle] = None
        self.stats: Dict[str, Any] = {}
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Button states
        self.button_rects = {}
        self.hovered_button = None
    
    def show(self, battle: SpatialBattle):
        """
        Show the post-game summary for a battle.
        
        Args:
            battle: The completed battle to summarize
        """
        self.visible = True
        self.battle = battle
        self.scroll_offset = 0
        self._compile_stats()
    
    def hide(self):
        """Hide the post-game summary."""
        self.visible = False
    
    def _compile_stats(self):
        """Compile battle statistics from the battle."""
        if not self.battle:
            return
        
        battle = self.battle
        
        # Get survivors and casualties
        survivors = [bc for bc in battle.creatures if bc.is_alive()]
        casualties = [bc for bc in battle.creatures if not bc.is_alive()]
        
        # Compile overall stats
        self.stats = {
            'duration': battle.current_time,
            'total_creatures': len(battle.creatures),
            'survivors': len(survivors),
            'casualties': len(casualties),
            'total_events': len(battle.events),
            'survivor_creatures': survivors,
            'casualty_creatures': casualties,
        }
        
        # Add per-creature stats
        creature_stats = []
        for bc in battle.creatures:
            creature = bc.creature
            stats_entry = {
                'name': creature.name,
                'alive': bc.is_alive(),
                'final_hp': creature.stats.hp,
                'max_hp': creature.stats.max_hp,
                'level': creature.level,
                'kills': len(creature.history.kills) if hasattr(creature, 'history') else 0,
                'damage_dealt': creature.history.total_damage_dealt if hasattr(creature, 'history') else 0,
                'damage_received': creature.history.total_damage_received if hasattr(creature, 'history') else 0,
                'battles': creature.history.battles_fought if hasattr(creature, 'history') else 0,
                'achievements': [a.name for a in creature.history.achievements] if hasattr(creature, 'history') else [],
                'color': creature.get_display_color() if hasattr(creature, 'get_display_color') else (255, 255, 255),
            }
            creature_stats.append(stats_entry)
        
        # Sort by alive status then by damage dealt
        creature_stats.sort(key=lambda x: (not x['alive'], -x['damage_dealt']))
        self.stats['creatures'] = creature_stats
    
    def handle_input(self, event: pygame.event.Event) -> str:
        """
        Handle input events.
        
        Args:
            event: Pygame event
            
        Returns:
            Action to take: 'replay', 'menu', 'export', or ''
        """
        if not self.visible:
            return ''
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return 'menu'
            elif event.key == pygame.K_r:
                return 'replay'
            elif event.key == pygame.K_e:
                return 'export'
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 30)
            elif event.key == pygame.K_DOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 30)
        
        elif event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - event.y * 30))
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self.hovered_button = None
            for button_name, rect in self.button_rects.items():
                if rect.collidepoint(mouse_pos):
                    self.hovered_button = button_name
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for button_name, rect in self.button_rects.items():
                if rect.collidepoint(mouse_pos):
                    if button_name == 'replay':
                        return 'replay'
                    elif button_name == 'menu':
                        self.hide()
                        return 'menu'
                    elif button_name == 'export':
                        return 'export'
        
        return ''
    
    def export_stats(self) -> str:
        """
        Export battle statistics to JSON file.
        
        Returns:
            Path to the exported file
        """
        if not self.stats:
            return ''
        
        # Create exports directory
        export_dir = Path.home() / '.evobattle' / 'exports'
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'battle_stats_{timestamp}.json'
        filepath = export_dir / filename
        
        # Prepare data for export (convert non-serializable types)
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'duration': self.stats['duration'],
            'total_creatures': self.stats['total_creatures'],
            'survivors': self.stats['survivors'],
            'casualties': self.stats['casualties'],
            'total_events': self.stats['total_events'],
            'creatures': []
        }
        
        for creature_stat in self.stats['creatures']:
            export_data['creatures'].append({
                'name': creature_stat['name'],
                'alive': creature_stat['alive'],
                'final_hp': creature_stat['final_hp'],
                'max_hp': creature_stat['max_hp'],
                'level': creature_stat['level'],
                'kills': creature_stat['kills'],
                'damage_dealt': creature_stat['damage_dealt'],
                'damage_received': creature_stat['damage_received'],
                'battles': creature_stat['battles'],
                'achievements': creature_stat['achievements'],
            })
        
        # Write to file
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Stats exported to: {filepath}")
        return str(filepath)
    
    def render(self, screen: pygame.Surface):
        """
        Render the post-game summary.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.visible:
            return
        
        screen_width, screen_height = screen.get_size()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill(self.overlay_color)
        screen.blit(overlay, (0, 0))
        
        # Create scrollable content surface
        content_height = 1500  # Estimated
        content = pygame.Surface((screen_width, content_height), pygame.SRCALPHA)
        
        y = 40
        
        # Title
        if self.stats['survivors'] == 0:
            title_text = "NO SURVIVORS"
            title_color = self.error_color
        elif self.stats['survivors'] == 1:
            survivor = self.stats['survivor_creatures'][0]
            title_text = f"{survivor.creature.name.upper()} WINS!"
            title_color = self.success_color
        else:
            title_text = f"{self.stats['survivors']} SURVIVORS!"
            title_color = self.success_color
        
        title_surface = self.title_font.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(screen_width // 2, y))
        content.blit(title_surface, title_rect)
        y += 80
        
        # Battle Statistics
        y = self._render_section(content, "Battle Statistics", screen_width // 2, y)
        
        stats_lines = [
            f"Duration: {self.stats['duration']:.1f} seconds",
            f"Total Creatures: {self.stats['total_creatures']}",
            f"Survivors: {self.stats['survivors']}",
            f"Casualties: {self.stats['casualties']}",
            f"Total Events: {self.stats['total_events']}",
        ]
        
        for line in stats_lines:
            text = self.text_font.render(line, True, self.text_color)
            text_rect = text.get_rect(center=(screen_width // 2, y))
            content.blit(text, text_rect)
            y += 30
        
        y += 30
        
        # Creature Breakdown
        y = self._render_section(content, "Creature Performance", screen_width // 2, y)
        
        # Column headers
        header_y = y
        col_x = [100, 300, 420, 540, 660, 780]
        headers = ["Name", "Status", "HP", "Kills", "Damage", "Achievements"]
        
        for i, header in enumerate(headers):
            if i < len(col_x):
                header_text = self.small_font.render(header, True, self.highlight_color)
                content.blit(header_text, (col_x[i], header_y))
        
        y += 30
        
        # Creature rows
        for creature_stat in self.stats['creatures'][:20]:  # Show top 20
            # Color indicator
            pygame.draw.circle(content, creature_stat['color'], (80, y + 10), 8)
            
            # Name
            name_text = self.text_font.render(creature_stat['name'][:15], True, self.text_color)
            content.blit(name_text, (col_x[0], y))
            
            # Status
            status = "✓ Alive" if creature_stat['alive'] else "✗ Dead"
            status_color = self.success_color if creature_stat['alive'] else self.error_color
            status_text = self.small_font.render(status, True, status_color)
            content.blit(status_text, (col_x[1], y))
            
            # HP
            hp_text = f"{int(creature_stat['final_hp'])}/{creature_stat['max_hp']}"
            hp_surface = self.small_font.render(hp_text, True, self.text_color)
            content.blit(hp_surface, (col_x[2], y))
            
            # Kills
            kills_text = self.small_font.render(str(creature_stat['kills']), True, self.text_color)
            content.blit(kills_text, (col_x[3], y))
            
            # Damage
            dmg_text = f"{int(creature_stat['damage_dealt'])}"
            dmg_surface = self.small_font.render(dmg_text, True, self.text_color)
            content.blit(dmg_surface, (col_x[4], y))
            
            # Achievements
            ach_count = len(creature_stat['achievements'])
            if ach_count > 0:
                ach_text = self.small_font.render(f"⭐ {ach_count}", True, self.warning_color)
                content.blit(ach_text, (col_x[5], y))
            
            y += 28
        
        y += 40
        
        # Calculate max scroll
        self.max_scroll = max(0, y - screen_height + 200)
        
        # Blit scrolled content to screen
        screen.blit(content, (0, -self.scroll_offset))
        
        # Buttons (fixed at bottom)
        self._render_buttons(screen)
        
        # Controls hint
        hint_text = self.small_font.render(
            "R - Replay  •  E - Export Stats  •  ESC - Continue  •  Scroll with mouse wheel",
            True, (200, 200, 200)
        )
        hint_rect = hint_text.get_rect(center=(screen_width // 2, screen_height - 20))
        screen.blit(hint_text, hint_rect)
    
    def _render_section(self, surface: pygame.Surface, title: str, center_x: int, y: int) -> int:
        """
        Render a section header.
        
        Args:
            surface: Surface to draw on
            title: Section title
            center_x: Center X position
            y: Y position
            
        Returns:
            New Y position after header
        """
        text = self.header_font.render(title, True, self.highlight_color)
        rect = text.get_rect(center=(center_x, y))
        surface.blit(text, rect)
        
        # Underline
        line_width = 300
        pygame.draw.line(
            surface,
            self.highlight_color,
            (center_x - line_width // 2, y + 25),
            (center_x + line_width // 2, y + 25),
            2
        )
        
        return y + 50
    
    def _render_buttons(self, screen: pygame.Surface):
        """Render action buttons at the bottom."""
        screen_width, screen_height = screen.get_size()
        button_y = screen_height - 80
        
        buttons = [
            ('replay', 'Replay Battle', 'R'),
            ('export', 'Export Stats', 'E'),
            ('menu', 'Continue', 'ESC'),
        ]
        
        button_width = 180
        button_height = 50
        total_width = len(buttons) * button_width + (len(buttons) - 1) * 20
        start_x = (screen_width - total_width) // 2
        
        self.button_rects = {}
        
        for i, (button_id, label, key) in enumerate(buttons):
            x = start_x + i * (button_width + 20)
            
            button_rect = pygame.Rect(x, button_y, button_width, button_height)
            self.button_rects[button_id] = button_rect
            
            # Determine colors
            if self.hovered_button == button_id:
                bg_color = (80, 120, 180)
                text_color = (255, 255, 255)
            else:
                bg_color = (50, 70, 120)
                text_color = (200, 200, 200)
            
            # Draw button
            pygame.draw.rect(screen, bg_color, button_rect, border_radius=8)
            pygame.draw.rect(screen, self.highlight_color, button_rect, 2, border_radius=8)
            
            # Draw label
            label_text = self.text_font.render(label, True, text_color)
            label_rect = label_text.get_rect(center=button_rect.center)
            screen.blit(label_text, label_rect)
            
            # Draw key hint
            key_text = self.small_font.render(f"[{key}]", True, (150, 150, 150))
            key_rect = key_text.get_rect(center=(button_rect.centerx, button_rect.bottom + 15))
            screen.blit(key_text, key_rect)
