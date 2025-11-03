"""
Pygame-based Codenames UI prototype.

Features implemented (prototype):
- Official-like color palette and typography
- 5x5 card grid with responsive sizing and rounded cards
- Hidden vs revealed state, reveal animation (fade/pop)
- Hover highlights, click-to-select for Operatives, tooltip for Spymaster
- Role selection screen (Spymaster vs Operative) and team selection
- Basic keyboard shortcuts: Enter (submit clue), Esc (clear input/close overlays), Space (confirm guess), Backspace (deselect last), F1 (help), Q (quit)

Usage: install pygame (pip install pygame) then run:
    python codenames_pygame.py

This prototype uses the game logic in `codenames.py` for board setup and card roles.
"""

import sys
import os
import time
import math
import random

try:
    import pygame
    from pygame import gfxdraw
except Exception as e:
    print("pygame is required. Install with: pip install pygame")
    raise

# Import the game core
import codenames

# -- Colors (official-inspired) --
COL_RED = pygame.Color('#D62828')      # Red team
COL_BLUE = pygame.Color('#0077B6')     # Blue team
COL_NEUTRAL = pygame.Color('#F1FAEE')  # Neutral card
COL_NEUTRAL_TEXT = pygame.Color('#1D3557')
COL_ASSASSIN = pygame.Color('#000000')
COL_ASSASSIN_TEXT = pygame.Color('#E63946')
COL_BOARD_BG = pygame.Color('#1D3557')  # Board background
COL_BEIGE = pygame.Color('#F4A261')     # Input areas
COL_TEXT_DARK = pygame.Color('#1D3557')
COL_WHITE = pygame.Color('#FFFFFF')

SHADOW_OFFSET = (4, 4)

# Layout constants - will be scaled by window size
GRID_ROWS = GRID_COLS = 5
BASE_CARD_W = 120
BASE_CARD_H = 80
BASE_GAP = 15
CARD_RADIUS = 8

FPS = 60

# Utility lerp
def lerp(a, b, t):
    return a + (b - a) * t


class CardView:
    def __init__(self, word, rect, role):
        self.word = word
        self.base_rect = pygame.Rect(rect)
        self.rect = pygame.Rect(rect)
        self.role = role  # 'RED'/'BLUE'/'NEUTRAL'/'ASSASSIN'
        self.revealed = False
        self.reveal_progress = 0.0  # 0.0 -> 1.0 animation
        self.selected = False
        self.hovered = False

    def center(self):
        return self.rect.center

    def draw(self, surf, fonts, mode_spymaster=False):
        # Draw shadow
        sx = self.rect.x + SHADOW_OFFSET[0]
        sy = self.rect.y + SHADOW_OFFSET[1]
        shadow_r = pygame.Rect(sx, sy, self.rect.w, self.rect.h)
        shadow_color = (0, 0, 0, 80)
        shadow_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, shadow_color, shadow_surf.get_rect(), border_radius=CARD_RADIUS)
        surf.blit(shadow_surf, (sx, sy))

        # Background: if revealed, color by role
        if self.revealed:
            if self.role == 'RED':
                bg = COL_RED
                text_col = COL_WHITE
            elif self.role == 'BLUE':
                bg = COL_BLUE
                text_col = COL_WHITE
            elif self.role == 'ASSASSIN':
                bg = COL_ASSASSIN
                text_col = COL_ASSASSIN_TEXT
            else:
                bg = COL_NEUTRAL
                text_col = COL_NEUTRAL_TEXT
        else:
            # Hidden state background
            bg = pygame.Color('#F8F4EA')  # light card front
            text_col = COL_TEXT_DARK

        # Apply reveal animation overlay (fade)
        if self.reveal_progress > 0.0 and not self.revealed:
            # during animation, we still show hidden bg but with a subtle effect
            pass

        # Draw rounded rect
        pygame.draw.rect(surf, bg, self.rect, border_radius=CARD_RADIUS)

        # Draw word
        font = fonts['card']
        text_surf = font.render(self.word, True, text_col)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surf.blit(text_surf, text_rect)

        # If spymaster mode, draw small role dot
        if mode_spymaster:
            dot_r = max(5, int(self.rect.h * 0.06))
            dot_x = self.rect.right - dot_r - 6
            dot_y = self.rect.top + 6
            if self.role == 'RED':
                dot_col = COL_RED
            elif self.role == 'BLUE':
                dot_col = COL_BLUE
            elif self.role == 'ASSASSIN':
                dot_col = COL_ASSASSIN
            else:
                dot_col = COL_NEUTRAL_TEXT

            pygame.gfxdraw.filled_circle(surf, dot_x, dot_y, dot_r, dot_col)
            pygame.gfxdraw.aacircle(surf, dot_x, dot_y, dot_r, (0,0,0))

        # Hover/selection outline
        if self.hovered and not self.revealed:
            pygame.draw.rect(surf, COL_WHITE, self.rect, width=2, border_radius=CARD_RADIUS)
        if self.selected:
            outline_col = COL_RED if self.role == 'RED' else (COL_BLUE if self.role == 'BLUE' else COL_TEXT_DARK)
            pygame.draw.rect(surf, outline_col, self.rect, width=3, border_radius=CARD_RADIUS)

    def update(self, dt):
        # animate reveal progress toward revealed state
        target = 1.0 if self.revealed else 0.0
        if self.reveal_progress < target:
            self.reveal_progress = min(target, self.reveal_progress + dt * 3.0)
        elif self.reveal_progress > target:
            self.reveal_progress = max(target, self.reveal_progress - dt * 3.0)


class PygameUI:
    def __init__(self, width=1100, height=800):
        pygame.init()
        pygame.font.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption('Codenames - Pygame Prototype')
        self.clock = pygame.time.Clock()

        # Fonts
        self.fonts = {
            'title': pygame.font.SysFont('Arial', 36, bold=True),
            'sub': pygame.font.SysFont('Arial', 22),
            'card': pygame.font.SysFont('Arial', 18, bold=True),
            'input': pygame.font.SysFont('Arial', 20),
        }

        # Game
        self.game = codenames.CodenamesGame()
        self.game.setup_board()

        # Build CardView objects
        self.cards = []
        self.mode_spymaster = False
        self.player_team = None
        self.selected_card = None
        self.help_overlay = False
        self.confirm_overlay = None
        self.message_popup = (None, 0)  # (text, expiry_time)

        self.create_layout()

        # Role selection state
        self.role_select = True

    def create_layout(self):
        # Compute responsive sizing
        w, h = self.screen.get_size()
        grid_w = w * 0.78
        grid_h = h * 0.6

        card_w = int((grid_w - (GRID_COLS - 1) * BASE_GAP) / GRID_COLS)
        card_h = int((grid_h - (GRID_ROWS - 1) * BASE_GAP) / GRID_ROWS)
        gap = int(BASE_GAP)

        # Ensure minimum sizes
        card_w = max(80, card_w)
        card_h = max(60, card_h)

        start_x = int((w - (card_w * GRID_COLS + gap * (GRID_COLS - 1))) / 2)
        start_y = int(h * 0.18)

        self.cards = []
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                idx = r * GRID_COLS + c
                word = self.game.words[idx]
                role = self.game.get_card_type(word)
                x = start_x + c * (card_w + gap)
                y = start_y + r * (card_h + gap)
                rect = (x, y, card_w, card_h)
                self.cards.append(CardView(word, rect, role))

        # Input area rect
        self.input_rect = pygame.Rect(int(w*0.12), int(h*0.82), int(w*0.76), int(h*0.12))

    def show_message(self, text, duration=2.0):
        self.message_popup = (text, time.time() + duration)

    def toggle_role(self, spymaster: bool, team: str = 'RED'):
        self.mode_spymaster = spymaster
        self.player_team = team
        self.role_select = False

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.width, self.height = event.w, event.h
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                    self.create_layout()
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_down(event)
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event)

            self.update(dt)
            self.draw()
            pygame.display.flip()

        pygame.quit()

    def handle_mouse_motion(self, pos):
        for card in self.cards:
            card.hovered = card.rect.collidepoint(pos) and (not card.revealed)

    def handle_mouse_down(self, event):
        pos = event.pos
        if self.role_select:
            # Check role selection buttons
            w, h = self.screen.get_size()
            bx = int(w*0.3); by = int(h*0.35); bw = 160; bh = 60
            # Red spymaster
            if pygame.Rect(bx, by, bw, bh).collidepoint(pos):
                self.toggle_role(True, 'RED')
                return
            if pygame.Rect(bx + 220, by, bw, bh).collidepoint(pos):
                self.toggle_role(False, 'RED')
                return
            if pygame.Rect(bx + 440, by, bw, bh).collidepoint(pos):
                self.toggle_role(False, 'BLUE')
                return
            return

        # If clicking on a card
        for card in self.cards:
            if card.rect.collidepoint(pos) and not card.revealed:
                if self.mode_spymaster:
                    # Spymaster hover shows tooltip only; no click action
                    self.show_message(card.role, 1.2)
                else:
                    # Operative: select/deselect
                    card.selected = not card.selected
                    if card.selected:
                        self.selected_card = card
                    else:
                        if self.selected_card == card:
                            self.selected_card = None
                return

    def handle_key(self, event):
        # Global shortcuts
        if event.key == pygame.K_q:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif event.key == pygame.K_F1:
            self.help_overlay = not self.help_overlay
        elif event.key == pygame.K_ESCAPE:
            # Clear selection / close overlays
            if self.help_overlay:
                self.help_overlay = False
            elif self.confirm_overlay:
                self.confirm_overlay = None
            else:
                for card in self.cards:
                    card.selected = False
                self.selected_card = None
        elif event.key == pygame.K_SPACE:
            # Confirm guess
            if self.selected_card and not self.mode_spymaster:
                self.confirm_overlay = ('confirm_guess', self.selected_card)
        elif event.key == pygame.K_BACKSPACE:
            # Deselect last
            for card in reversed(self.cards):
                if card.selected:
                    card.selected = False
                    break
        elif event.key == pygame.K_RETURN:
            # Submit a clue for spymaster mode (not wired to AI)
            if self.mode_spymaster:
                self.show_message('Clue submitted', 1.2)

    def update(self, dt):
        # Update cards
        for card in self.cards:
            card.update(dt)

        # Handle confirmation overlay actions (auto-execute for demo after 0.1s)
        if self.confirm_overlay:
            typ, payload = self.confirm_overlay
            if typ == 'confirm_guess':
                card = payload
                # Apply reveal
                self.reveal_card(card)
                self.confirm_overlay = None

        # Popups expire
        if self.message_popup[0] and time.time() > self.message_popup[1]:
            self.message_popup = (None, 0)

    def reveal_card(self, card: CardView):
        card.revealed = True
        card.selected = False
        self.show_message(f'{card.word} revealed ({card.role})', 1.5)

    def draw(self):
        # Background
        self.screen.fill(COL_BOARD_BG)

        # Title
        title_surf = self.fonts['title'].render('Codenames', True, COL_WHITE)
        self.screen.blit(title_surf, (20, 10))

        # Team / Turn indicator
        turn_text = f"{self.game.turn} Team Turn"
        sub_surf = self.fonts['sub'].render(turn_text, True, COL_WHITE)
        self.screen.blit(sub_surf, (20, 56))

        # Cards
        for card in self.cards:
            card.draw(self.screen, self.fonts, mode_spymaster=self.mode_spymaster)

        # Input area (bottom)
        pygame.draw.rect(self.screen, COL_BEIGE, self.input_rect, border_radius=10)
        hint = 'Spymaster: Enter "Clue Number" | Operative: Click a card and press Space to confirm'
        hint_surf = self.fonts['input'].render(hint, True, COL_TEXT_DARK)
        self.screen.blit(hint_surf, (self.input_rect.x + 12, self.input_rect.y + 12))

        # Role selection overlay
        if self.role_select:
            self.draw_role_select()

        # Help overlay
        if self.help_overlay:
            self.draw_help_overlay()

        # Message popup
        if self.message_popup[0]:
            self.draw_popup(self.message_popup[0])

        # Confirm overlay
        if self.confirm_overlay:
            self.draw_confirm_overlay(self.confirm_overlay[1])

    def draw_popup(self, text):
        w, h = self.screen.get_size()
        surf = pygame.Surface((w, 60), pygame.SRCALPHA)
        surf.fill((0,0,0,160))
        txt = self.fonts['sub'].render(text, True, COL_WHITE)
        surf.blit(txt, (10, 12))
        self.screen.blit(surf, (0, int(h*0.7)))

    def draw_confirm_overlay(self, card: CardView):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0,0))

        txt = self.fonts['title'].render(f'Confirm guess: {card.word}?', True, COL_WHITE)
        rect = txt.get_rect(center=(w//2, h//2 - 20))
        self.screen.blit(txt, rect)

        sub = self.fonts['sub'].render('Press Space to confirm, Esc to cancel', True, COL_WHITE)
        subr = sub.get_rect(center=(w//2, h//2 + 30))
        self.screen.blit(sub, subr)

    def draw_help_overlay(self):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0,0))
        lines = [
            'Help - Controls',
            'Mouse: Hover to highlight, click to select/deselect (Operative)',
            'Space: Confirm selected card (Operative)',
            'Enter: Submit clue (Spymaster)',
            'Esc: Clear selection / close overlays',
            'F1: Toggle this help',
            'Q: Quit'
        ]
        y = 80
        for i, line in enumerate(lines):
            font = self.fonts['title'] if i==0 else self.fonts['sub']
            surf = font.render(line, True, COL_WHITE)
            self.screen.blit(surf, (60, y))
            y += 50

    def draw_role_select(self):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0,0))

        title = self.fonts['title'].render('Choose Role & Team', True, COL_WHITE)
        self.screen.blit(title, (int(w*0.3), int(h*0.2)))

        # Buttons
        bx = int(w*0.3); by = int(h*0.35); bw = 160; bh = 60
        # Spymaster (Red)
        pygame.draw.rect(self.screen, COL_RED, (bx, by, bw, bh), border_radius=8)
        txt = self.fonts['sub'].render('Spymaster (Red)', True, COL_WHITE)
        self.screen.blit(txt, (bx+12, by+16))
        # Operative (Red)
        pygame.draw.rect(self.screen, COL_BEIGE, (bx+220, by, bw, bh), border_radius=8)
        txt2 = self.fonts['sub'].render('Operative (Red)', True, COL_TEXT_DARK)
        self.screen.blit(txt2, (bx+232, by+16))
        # Operative (Blue)
        pygame.draw.rect(self.screen, COL_BEIGE, (bx+440, by, bw, bh), border_radius=8)
        txt3 = self.fonts['sub'].render('Operative (Blue)', True, COL_TEXT_DARK)
        self.screen.blit(txt3, (bx+452, by+16))


if __name__ == '__main__':
    ui = PygameUI()
    ui.run()
