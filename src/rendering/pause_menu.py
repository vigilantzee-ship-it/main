"""
Pause Menu - Interactive pause screen with game controls.

Provides a pause overlay with options to resume, restart, or quit
the game with confirmation dialogs to prevent accidental exits.
"""

import pygame
from typing import Optional, Callable
from enum import Enum


class PauseMenuAction(Enum):
    """Actions that can be taken from the pause menu."""
    NONE = "none"
    RESUME = "resume"
    RESTART = "restart"
    QUIT = "quit"


class PauseMenu:
    """
    Interactive pause menu with button controls.
    
    Displays when the game is paused and provides options to:
    - Resume gameplay
    - Restart battle
    - Quit to main menu (with confirmation)
    
    Attributes:
        visible: Whether the menu is currently visible
        selected_index: Currently selected menu option
        quit_confirm_visible: Whether quit confirmation dialog is showing
    """
    
    def __init__(self):
        """Initialize the pause menu."""
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 48)
        self.option_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 24)
        
        # Colors
        self.bg_color = (0, 0, 0, 180)
        self.text_color = (255, 255, 255)
        self.selected_color = (255, 255, 100)
        self.button_bg = (50, 50, 70)
        self.button_selected_bg = (80, 80, 120)
        
        # State
        self.visible = False
        self.selected_index = 0
        self.quit_confirm_visible = False
        
        # Menu options
        self.options = ["Resume", "Restart", "Quit to Menu"]
        self.option_rects = []
        
    def show(self):
        """Show the pause menu."""
        self.visible = True
        self.selected_index = 0
        self.quit_confirm_visible = False
    
    def hide(self):
        """Hide the pause menu."""
        self.visible = False
        self.quit_confirm_visible = False
    
    def toggle(self):
        """Toggle pause menu visibility."""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def handle_input(self, event: pygame.event.Event) -> PauseMenuAction:
        """
        Handle input events for the pause menu.
        
        Args:
            event: Pygame event
            
        Returns:
            Action to take (resume, restart, quit, or none)
        """
        if not self.visible:
            return PauseMenuAction.NONE
        
        if self.quit_confirm_visible:
            # Handle quit confirmation dialog
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_y:
                    self.visible = False
                    return PauseMenuAction.QUIT
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_n:
                    self.quit_confirm_visible = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Check confirm buttons (will be set during render)
                if hasattr(self, '_yes_button_rect') and self._yes_button_rect.collidepoint(mouse_pos):
                    self.visible = False
                    return PauseMenuAction.QUIT
                elif hasattr(self, '_no_button_rect') and self._no_button_rect.collidepoint(mouse_pos):
                    self.quit_confirm_visible = False
        else:
            # Handle main menu
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return self._select_option()
                elif event.key == pygame.K_ESCAPE:
                    self.hide()
                    return PauseMenuAction.RESUME
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_index = i
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_index = i
                        return self._select_option()
        
        return PauseMenuAction.NONE
    
    def _select_option(self) -> PauseMenuAction:
        """
        Handle option selection.
        
        Returns:
            Action to take based on selected option
        """
        option = self.options[self.selected_index]
        
        if option == "Resume":
            self.hide()
            return PauseMenuAction.RESUME
        elif option == "Restart":
            self.hide()
            return PauseMenuAction.RESTART
        elif option == "Quit to Menu":
            # Show quit confirmation
            self.quit_confirm_visible = True
            return PauseMenuAction.NONE
        
        return PauseMenuAction.NONE
    
    def render(self, screen: pygame.Surface):
        """
        Render the pause menu.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.visible:
            return
        
        screen_width, screen_height = screen.get_size()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill(self.bg_color)
        screen.blit(overlay, (0, 0))
        
        if self.quit_confirm_visible:
            self._render_quit_confirmation(screen)
        else:
            self._render_main_menu(screen)
    
    def _render_main_menu(self, screen: pygame.Surface):
        """Render the main pause menu."""
        screen_width, screen_height = screen.get_size()
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        # Title
        title_text = self.title_font.render("PAUSED", True, self.selected_color)
        title_rect = title_text.get_rect(center=(center_x, center_y - 150))
        screen.blit(title_text, title_rect)
        
        # Menu options
        self.option_rects = []
        button_width = 300
        button_height = 60
        button_spacing = 20
        
        for i, option in enumerate(self.options):
            y = center_y - 50 + i * (button_height + button_spacing)
            
            # Button background
            button_rect = pygame.Rect(
                center_x - button_width // 2,
                y,
                button_width,
                button_height
            )
            self.option_rects.append(button_rect)
            
            # Determine colors based on selection
            if i == self.selected_index:
                bg_color = self.button_selected_bg
                text_color = self.selected_color
            else:
                bg_color = self.button_bg
                text_color = self.text_color
            
            # Draw button
            pygame.draw.rect(screen, bg_color, button_rect, border_radius=8)
            pygame.draw.rect(screen, text_color, button_rect, 2, border_radius=8)
            
            # Draw text
            option_text = self.option_font.render(option, True, text_color)
            option_rect = option_text.get_rect(center=button_rect.center)
            screen.blit(option_text, option_rect)
        
        # Controls hint
        hint_text = self.text_font.render(
            "Use arrow keys or mouse to select • ENTER to confirm • ESC to resume",
            True, (200, 200, 200)
        )
        hint_rect = hint_text.get_rect(center=(center_x, screen_height - 50))
        screen.blit(hint_text, hint_rect)
    
    def _render_quit_confirmation(self, screen: pygame.Surface):
        """Render the quit confirmation dialog."""
        screen_width, screen_height = screen.get_size()
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        # Dialog background
        dialog_width = 500
        dialog_height = 250
        dialog_rect = pygame.Rect(
            center_x - dialog_width // 2,
            center_y - dialog_height // 2,
            dialog_width,
            dialog_height
        )
        
        pygame.draw.rect(screen, (40, 40, 60), dialog_rect, border_radius=12)
        pygame.draw.rect(screen, self.selected_color, dialog_rect, 3, border_radius=12)
        
        # Title
        title_text = self.option_font.render("Quit to Menu?", True, self.text_color)
        title_rect = title_text.get_rect(center=(center_x, center_y - 60))
        screen.blit(title_text, title_rect)
        
        # Warning message
        warning_text = self.text_font.render(
            "Current battle progress will be lost.",
            True, (255, 200, 100)
        )
        warning_rect = warning_text.get_rect(center=(center_x, center_y - 20))
        screen.blit(warning_text, warning_rect)
        
        # Buttons
        button_width = 120
        button_height = 50
        button_spacing = 30
        
        # Yes button
        yes_x = center_x - button_width - button_spacing // 2
        yes_y = center_y + 30
        self._yes_button_rect = pygame.Rect(yes_x, yes_y, button_width, button_height)
        
        pygame.draw.rect(screen, (200, 80, 80), self._yes_button_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 100, 100), self._yes_button_rect, 2, border_radius=8)
        
        yes_text = self.option_font.render("Yes", True, self.text_color)
        yes_text_rect = yes_text.get_rect(center=self._yes_button_rect.center)
        screen.blit(yes_text, yes_text_rect)
        
        # No button
        no_x = center_x + button_spacing // 2
        no_y = center_y + 30
        self._no_button_rect = pygame.Rect(no_x, no_y, button_width, button_height)
        
        pygame.draw.rect(screen, (80, 120, 80), self._no_button_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 200, 100), self._no_button_rect, 2, border_radius=8)
        
        no_text = self.option_font.render("No", True, self.text_color)
        no_text_rect = no_text.get_rect(center=self._no_button_rect.center)
        screen.blit(no_text, no_text_rect)
        
        # Hint
        hint_text = self.text_font.render(
            "Y = Yes  •  N / ESC = No",
            True, (180, 180, 180)
        )
        hint_rect = hint_text.get_rect(center=(center_x, center_y + 110))
        screen.blit(hint_text, hint_rect)
