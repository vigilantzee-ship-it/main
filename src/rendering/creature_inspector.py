"""
Creature Inspector UI - Display detailed creature information on click.

Shows comprehensive creature details including history, skills, personality,
relationships, and achievements in an interactive panel.
"""

import pygame
from typing import Optional, List
from ..models.creature import Creature
from ..models.history import EventType
from ..models.skills import SkillType
from ..models.relationships import RelationshipType


class CreatureInspector:
    """
    Interactive UI panel for inspecting creature details.
    
    Displays:
    - Basic stats and status
    - Personality traits
    - Skill proficiency
    - Battle history and statistics
    - Achievements and titles
    - Relationships
    - Recent event timeline
    """
    
    def __init__(self):
        """Initialize the creature inspector."""
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 28)
        self.header_font = pygame.font.Font(None, 22)
        self.text_font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 16)
        
        # Colors
        self.bg_color = (30, 30, 40, 230)
        self.header_color = (50, 50, 70)
        self.text_color = (255, 255, 255)
        self.highlight_color = (100, 150, 255)
        self.stat_color = (150, 200, 255)
        self.warning_color = (255, 150, 100)
        self.success_color = (100, 255, 150)
        
        # State
        self.selected_creature: Optional[Creature] = None
        self.visible = False
        self.scroll_offset = 0
        self.max_scroll = 0
        
        # Panel dimensions (percentage of screen)
        self.panel_width_pct = 0.35  # 35% of screen width
        self.panel_height_pct = 0.85  # 85% of screen height
        self.margin = 20
        self.line_height = 20
        self.section_spacing = 15
    
    def select_creature(self, creature: Optional[Creature]):
        """
        Select a creature to inspect.
        
        Args:
            creature: The creature to inspect, or None to deselect
        """
        self.selected_creature = creature
        self.visible = creature is not None
        self.scroll_offset = 0
    
    def toggle_visibility(self):
        """Toggle inspector visibility."""
        self.visible = not self.visible
    
    def handle_scroll(self, direction: int):
        """
        Handle scroll input.
        
        Args:
            direction: -1 for up, 1 for down
        """
        scroll_speed = 20
        self.scroll_offset = max(0, min(self.max_scroll, 
                                       self.scroll_offset + direction * scroll_speed))
    
    def render(self, screen: pygame.Surface):
        """
        Render the inspector panel.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.visible or not self.selected_creature:
            return
        
        creature = self.selected_creature
        screen_width, screen_height = screen.get_size()
        
        # Calculate panel dimensions
        panel_width = int(screen_width * self.panel_width_pct)
        panel_height = int(screen_height * self.panel_height_pct)
        panel_x = screen_width - panel_width - 20
        panel_y = (screen_height - panel_height) // 2
        
        # Create panel surface with transparency
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill(self.bg_color)
        
        # Draw border
        pygame.draw.rect(panel, self.highlight_color, panel.get_rect(), 2)
        
        # Render content with scrolling
        content_surface = self._render_content(creature, panel_width)
        
        # Calculate max scroll
        self.max_scroll = max(0, content_surface.get_height() - panel_height + 40)
        
        # Blit scrolled content
        panel.blit(content_surface, (0, -self.scroll_offset))
        
        # Draw scroll indicators if needed
        if self.max_scroll > 0:
            if self.scroll_offset > 0:
                # Up arrow
                pygame.draw.polygon(panel, self.highlight_color, [
                    (panel_width - 20, 15),
                    (panel_width - 10, 25),
                    (panel_width - 30, 25)
                ])
            if self.scroll_offset < self.max_scroll:
                # Down arrow
                pygame.draw.polygon(panel, self.highlight_color, [
                    (panel_width - 20, panel_height - 15),
                    (panel_width - 10, panel_height - 25),
                    (panel_width - 30, panel_height - 25)
                ])
        
        # Draw to screen
        screen.blit(panel, (panel_x, panel_y))
        
        # Draw close button
        close_text = self.small_font.render("[ESC to close]", True, self.text_color)
        screen.blit(close_text, (panel_x + 10, panel_y - 20))
    
    def _render_content(self, creature: Creature, panel_width: int) -> pygame.Surface:
        """
        Render all content for the inspector panel.
        
        Args:
            creature: The creature to display
            panel_width: Width of the panel
            
        Returns:
            Surface with all content rendered
        """
        # Estimate height (will create larger surface if needed)
        estimated_height = 2000
        content = pygame.Surface((panel_width, estimated_height), pygame.SRCALPHA)
        
        y = self.margin
        x_margin = self.margin
        content_width = panel_width - (2 * x_margin)
        
        # Title - Creature Name
        title = self.title_font.render(creature.name, True, self.highlight_color)
        content.blit(title, (x_margin, y))
        y += title.get_height() + 5
        
        # Subtitle - Level and Type
        subtitle = self.text_font.render(
            f"Level {creature.level} {creature.creature_type.name}",
            True, self.text_color
        )
        content.blit(subtitle, (x_margin, y))
        y += subtitle.get_height() + self.section_spacing
        
        # === Stats Section ===
        y = self._render_section_header(content, "Stats", x_margin, y)
        
        hp_pct = (creature.stats.hp / creature.stats.max_hp * 100) if creature.stats.max_hp > 0 else 0
        hp_color = self.success_color if hp_pct > 70 else self.warning_color if hp_pct > 30 else (255, 50, 50)
        
        stats_lines = [
            f"HP: {creature.stats.hp:.0f}/{creature.stats.max_hp} ({hp_pct:.0f}%)",
            f"Attack: {creature.stats.attack}  Defense: {creature.stats.defense}",
            f"Speed: {creature.stats.speed}  Energy: {creature.energy}/{creature.max_energy}"
        ]
        
        for i, line in enumerate(stats_lines):
            color = hp_color if i == 0 else self.stat_color
            text = self.text_font.render(line, True, color)
            content.blit(text, (x_margin + 10, y))
            y += self.line_height
        
        y += self.section_spacing
        
        # === Personality Section ===
        y = self._render_section_header(content, "Personality", x_margin, y)
        
        personality_text = creature.personality.get_description()
        y = self._render_wrapped_text(content, personality_text, x_margin + 10, y, 
                                       content_width - 20, self.text_font, self.text_color)
        
        combat_style = f"Combat Style: {creature.personality.get_combat_style()}"
        style_text = self.small_font.render(combat_style, True, self.stat_color)
        content.blit(style_text, (x_margin + 10, y))
        y += self.line_height + self.section_spacing
        
        # === Skills Section ===
        y = self._render_section_header(content, "Skills", x_margin, y)
        
        top_skills = creature.skills.get_highest_skills(5)
        if top_skills:
            for skill_type, level in top_skills:
                skill = creature.skills.get_skill(skill_type)
                prof = skill.get_proficiency().value
                skill_line = f"{skill.config.name}: Lv.{level} ({prof})"
                
                # Color based on proficiency
                if level >= 80:
                    color = (255, 215, 0)  # Gold for legendary
                elif level >= 60:
                    color = (200, 100, 255)  # Purple for master
                elif level >= 40:
                    color = (100, 200, 255)  # Blue for expert
                else:
                    color = self.text_color
                
                text = self.text_font.render(skill_line, True, color)
                content.blit(text, (x_margin + 10, y))
                y += self.line_height
        else:
            text = self.small_font.render("No skills developed yet", True, (150, 150, 150))
            content.blit(text, (x_margin + 10, y))
            y += self.line_height
        
        y += self.section_spacing
        
        # === Battle History Section ===
        y = self._render_section_header(content, "Battle Record", x_margin, y)
        
        history = creature.history
        win_rate = history.get_win_rate() * 100
        
        history_lines = [
            f"Battles: {history.battles_fought} ({history.battles_won}W-{history.battles_fought - history.battles_won}L)",
            f"Win Rate: {win_rate:.1f}%",
            f"Kills: {len(history.kills)}  Deaths: {history.deaths}",
            f"Damage: {history.total_damage_dealt:.0f} dealt, {history.total_damage_received:.0f} taken"
        ]
        
        for line in history_lines:
            text = self.text_font.render(line, True, self.stat_color)
            content.blit(text, (x_margin + 10, y))
            y += self.line_height
        
        if history.deaths > 0:
            kd = history.get_kill_death_ratio()
            kd_text = self.text_font.render(f"K/D Ratio: {kd:.2f}", True, self.stat_color)
            content.blit(kd_text, (x_margin + 10, y))
            y += self.line_height
        
        y += self.section_spacing
        
        # === Achievements Section ===
        if history.achievements:
            y = self._render_section_header(content, "Achievements", x_margin, y)
            
            for achievement in history.achievements[:5]:  # Show top 5
                # Star rating based on rarity
                stars = "⭐" * int(achievement.rarity * 5)
                ach_text = f"{stars} {achievement.name}"
                text = self.text_font.render(ach_text, True, (255, 215, 0))
                content.blit(text, (x_margin + 10, y))
                y += self.line_height
                
                # Description
                desc = self.small_font.render(achievement.description, True, (200, 200, 200))
                content.blit(desc, (x_margin + 20, y))
                y += self.line_height
            
            y += self.section_spacing
        
        # === Titles Section ===
        if history.titles:
            y = self._render_section_header(content, "Titles", x_margin, y)
            
            titles_str = ", ".join(history.titles)
            y = self._render_wrapped_text(content, titles_str, x_margin + 10, y,
                                         content_width - 20, self.text_font, (255, 215, 0))
            y += self.section_spacing
        
        # === Relationships Section ===
        allies = creature.relationships.get_allies()
        enemies = creature.relationships.get_enemies()
        family = creature.relationships.get_family()
        
        if allies or enemies or family:
            y = self._render_section_header(content, "Relationships", x_margin, y)
            
            if family:
                text = self.text_font.render(f"Family: {len(family)}", True, self.success_color)
                content.blit(text, (x_margin + 10, y))
                y += self.line_height
            
            if allies:
                text = self.text_font.render(f"Allies: {len(allies)}", True, (100, 200, 255))
                content.blit(text, (x_margin + 10, y))
                y += self.line_height
            
            if enemies:
                text = self.text_font.render(f"Rivals/Enemies: {len(enemies)}", True, (255, 100, 100))
                content.blit(text, (x_margin + 10, y))
                y += self.line_height
            
            # Show revenge targets specifically
            revenge_targets = creature.relationships.get_revenge_targets()
            if revenge_targets:
                text = self.text_font.render(f"Revenge Targets: {len(revenge_targets)}", True, (255, 50, 50))
                content.blit(text, (x_margin + 10, y))
                y += self.line_height
            
            y += self.section_spacing
        
        # === Recent Events Section ===
        y = self._render_section_header(content, "Recent Events", x_margin, y)
        
        recent_events = history.get_recent_events(8)
        if recent_events:
            for event in recent_events:
                # Event type indicator
                event_icon = self._get_event_icon(event.event_type)
                icon_text = self.small_font.render(event_icon, True, self.highlight_color)
                content.blit(icon_text, (x_margin + 10, y))
                
                # Event description
                desc = self.small_font.render(event.description[:50], True, self.text_color)
                content.blit(desc, (x_margin + 30, y))
                y += self.line_height
        else:
            text = self.small_font.render("No events recorded", True, (150, 150, 150))
            content.blit(text, (x_margin + 10, y))
            y += self.line_height
        
        y += self.margin
        
        # Crop content to actual used height
        actual_content = pygame.Surface((panel_width, y), pygame.SRCALPHA)
        actual_content.blit(content, (0, 0))
        
        return actual_content
    
    def _render_section_header(self, surface: pygame.Surface, title: str, x: int, y: int) -> int:
        """
        Render a section header.
        
        Args:
            surface: Surface to draw on
            title: Header title
            x: X position
            y: Y position
            
        Returns:
            New Y position after header
        """
        # Draw header background
        header_rect = pygame.Rect(x, y, surface.get_width() - 2 * x, 25)
        pygame.draw.rect(surface, self.header_color, header_rect)
        
        # Draw header text
        text = self.header_font.render(title, True, self.text_color)
        surface.blit(text, (x + 5, y + 3))
        
        return y + 30
    
    def _render_wrapped_text(
        self,
        surface: pygame.Surface,
        text: str,
        x: int,
        y: int,
        max_width: int,
        font: pygame.font.Font,
        color: tuple
    ) -> int:
        """
        Render text with word wrapping.
        
        Args:
            surface: Surface to draw on
            text: Text to render
            x: X position
            y: Starting Y position
            max_width: Maximum width before wrapping
            font: Font to use
            color: Text color
            
        Returns:
            Final Y position after text
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, color)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for line in lines:
            line_surface = font.render(line, True, color)
            surface.blit(line_surface, (x, y))
            y += self.line_height
        
        return y
    
    def _get_event_icon(self, event_type: EventType) -> str:
        """
        Get an icon/emoji for an event type.
        
        Args:
            event_type: Type of event
            
        Returns:
            Icon string
        """
        icons = {
            EventType.BIRTH: "🐣",
            EventType.DEATH: "💀",
            EventType.BATTLE_START: "⚔️",
            EventType.BATTLE_WIN: "🏆",
            EventType.BATTLE_LOSS: "💔",
            EventType.ATTACK: "⚡",
            EventType.CRITICAL_HIT: "💥",
            EventType.KILL: "🗡️",
            EventType.REVENGE_KILL: "☠️",
            EventType.OFFSPRING_BORN: "👶",
            EventType.FIRST_KILL: "🎯",
            EventType.MILESTONE_REACHED: "🎖️",
        }
        return icons.get(event_type, "•")
