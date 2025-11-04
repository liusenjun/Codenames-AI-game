"""
Codenames AI Game - Modern GUI
A beautiful graphical interface for the Codenames game
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Tuple, Dict, List
import random
from codenames import (
    CodenamesGame, AISpymaster, AIGuesser, WORD_POOL
)

# Translation support
try:
    from googletrans import Translator, LANGUAGES
    TRANSLATION_AVAILABLE = True
except ImportError:
    TRANSLATION_AVAILABLE = False
    print("Note: Translation feature requires 'googletrans' library.")
    print("Install it with: pip install googletrans==4.0.0rc1")

# Common languages for translation
COMMON_LANGUAGES = {
    'Chinese (Simplified)': 'zh-cn',
    'Chinese (Traditional)': 'zh-tw',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Russian': 'ru',
    'Arabic': 'ar',
    'Hindi': 'hi',
    'Thai': 'th',
    'Vietnamese': 'vi',
    'Indonesian': 'id',
    'Turkish': 'tr',
    'Dutch': 'nl',
    'Polish': 'pl',
    'Greek': 'el',
    'Czech': 'cs'
}

# Official Codenames colors
COLORS = {
    'RED': '#DC143C',      # Crimson red
    'BLUE': '#1E90FF',     # Dodger blue
    'NEUTRAL': '#F5DEB3',  # Wheat/beige
    'ASSASSIN': '#2F2F2F', # Dark gray/black
    'HIDDEN': '#E8E8E8',   # Light gray for hidden cards
    'BACKGROUND': '#F0F0F0',
    'TEXT': '#2F2F2F',
    'BUTTON_BG': '#4A90E2',
    'BUTTON_HOVER': '#357ABD',
    'SUCCESS': '#28A745',
    'ERROR': '#DC3545'
}

class CodenamesGUI:
    """Modern GUI for Codenames game."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Codenames AI Game")
        self.root.geometry("1400x850")
        self.root.configure(bg=COLORS['BACKGROUND'])
        
        # Game state
        self.game: Optional[CodenamesGame] = None
        self.mode = 1  # 1: AI vs AI, 2: Player Operative, 3: Player Spymaster
        self.player_team: Optional[str] = None
        self.red_spymaster = None
        self.red_guesser = None
        self.blue_spymaster = None
        self.blue_guesser = None
        self.current_clue = None
        self.current_count = 0
        self.guesses_made = 0
        self.max_guesses = 0
        self.turn_in_progress = False
        
        # Game history for display
        self.game_history = []  # List of history entries
        self.current_turn_entry = None  # Current turn's history entry
        
        # Translation state
        self.translation_enabled = False
        self.translation_language = 'zh-cn'  # Default to Chinese Simplified
        self.translator = None
        self.translation_cache: Dict[str, str] = {}  # Cache translations
        self.translation_available = TRANSLATION_AVAILABLE  # Store as instance variable
        
        if self.translation_available:
            try:
                self.translator = Translator()
            except Exception as e:
                print(f"Translation initialization error: {e}")
                self.translation_available = False
        
        # UI Components
        self.card_buttons = []
        self.game_frame = None
        self.control_frame = None
        self.translate_toggle = None
        self.language_combo = None
        self.pass_button = None  # Pass button for player operative
        self.history_text = None  # History text widget
        
        self.show_menu()
    
    def show_menu(self):
        """Show main menu with mode selection."""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Reset game history
        self.game_history = []
        
        # Title
        title_frame = tk.Frame(self.root, bg=COLORS['BACKGROUND'])
        title_frame.pack(pady=50)
        
        title_label = tk.Label(
            title_frame,
            text="CODENAMES",
            font=('Arial', 48, 'bold'),
            bg=COLORS['BACKGROUND'],
            fg=COLORS['TEXT']
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="AI Game",
            font=('Arial', 24),
            bg=COLORS['BACKGROUND'],
            fg=COLORS['TEXT']
        )
        subtitle_label.pack(pady=(10, 0))
        
        # Mode selection
        mode_frame = tk.Frame(self.root, bg=COLORS['BACKGROUND'])
        mode_frame.pack(pady=50)
        
        tk.Label(
            mode_frame,
            text="Select Game Mode",
            font=('Arial', 18, 'bold'),
            bg=COLORS['BACKGROUND'],
            fg=COLORS['TEXT']
        ).pack(pady=20)
        
        # Place player modes first and AI vs AI at the bottom (user preference)
        modes = [
            ("AI vs AI", "Watch the AI play"),
            ("Player as Field Operative", "You guess, AI gives clues"),
            ("Player as Spymaster", "You give clues, AI guesses"),
            ("AI vs AI", "Watch the AI play")
        ]
        
        for i, (mode_name, description) in enumerate(modes, 1):
            btn = tk.Button(
                mode_frame,
                text=f"{mode_name}\n{description}",
                font=('Arial', 12),
                bg=COLORS['BUTTON_BG'],
                fg='white',
                activebackground=COLORS['BUTTON_HOVER'],
                activeforeground='white',
                relief=tk.RAISED,
                bd=3,
                width=30,
                height=3,
                command=lambda m=i: self.start_game(m)
            )
            btn.pack(pady=10)
            self.hover_effect(btn)
    
    def start_game(self, mode: int):
        """Start a new game with selected mode."""
        self.mode = mode
        
        # Get team selection for player modes
        self.player_team = None
        if mode in [2, 3]:
            self.player_team = self.select_team()
            if self.player_team is None:
                return  # User cancelled
        
        # Initialize game
        self.game = CodenamesGame()
        self.game.setup_board()
        
        # Create AI players
        self.red_spymaster = AISpymaster('RED')
        self.red_guesser = AIGuesser('RED')
        self.blue_spymaster = AISpymaster('BLUE')
        self.blue_guesser = AIGuesser('BLUE')
        
        # Reset history
        self.game_history = []
        
        # Show game board
        self.show_game_board()
        
        # Start first turn
        if mode == 1:
            # AI vs AI - always start AI turn
            self.root.after(1000, self.process_turn)
        elif mode == 2:
            # Player operative - start turn (AI spymaster will give clue if it's player's team turn)
            if self.game.turn == self.player_team:
                # Player's team turn - AI spymaster should give clue
                self.root.after(1000, self.process_turn)
            else:
                # Opponent's turn - AI plays
                self.root.after(1000, self.process_turn)
        elif mode == 3:
            # Player spymaster - start turn (player will input clue if it's their turn)
            if self.game.turn == self.player_team:
                # Player's turn - wait for player input
                self.setup_spymaster_input()
            else:
                # Opponent's turn - AI plays
                self.root.after(1000, self.process_turn)
    
    def select_team(self) -> Optional[str]:
        """Show team selection dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Team")
        dialog.geometry("400x250")
        dialog.configure(bg=COLORS['BACKGROUND'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"400x250+{x}+{y}")
        
        result = [None]
        
        tk.Label(
            dialog,
            text="Choose Your Team",
            font=('Arial', 20, 'bold'),
            bg=COLORS['BACKGROUND'],
            fg=COLORS['TEXT']
        ).pack(pady=20)
        
        team_frame = tk.Frame(dialog, bg=COLORS['BACKGROUND'])
        team_frame.pack(pady=20, fill=tk.X, padx=20)

        def select_team(team: str):
            result[0] = team
            dialog.destroy()

        # Use grid with two equally-weighted columns so both buttons expand to same width
        team_frame.columnconfigure(0, weight=1)
        team_frame.columnconfigure(1, weight=1)

        red_btn = tk.Button(
            team_frame,
            text="RED TEAM",
            font=('Arial', 16, 'bold'),
            bg=COLORS['RED'],
            fg='white',
            height=2,
            command=lambda: select_team('RED')
        )
        red_btn.grid(row=0, column=0, sticky='ew', padx=(0, 8), pady=10)

        blue_btn = tk.Button(
            team_frame,
            text="BLUE TEAM",
            font=('Arial', 16, 'bold'),
            bg=COLORS['BLUE'],
            fg='white',
            height=2,
            command=lambda: select_team('BLUE')
        )
        blue_btn.grid(row=0, column=1, sticky='ew', padx=(8, 0), pady=10)
        
        dialog.wait_window()
        return result[0]
    
    def show_game_board(self):
        """Display the game board."""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container with history panel
        container_frame = tk.Frame(self.root, bg=COLORS['BACKGROUND'])
        container_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left side: Game board
        main_frame = tk.Frame(container_frame, bg=COLORS['BACKGROUND'])
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=COLORS['BACKGROUND'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            header_frame,
            text="CODENAMES",
            font=('Arial', 32, 'bold'),
            bg=COLORS['BACKGROUND'],
            fg=COLORS['TEXT']
        )
        title_label.pack(side=tk.LEFT)
        
        # Status frame
        status_frame = tk.Frame(header_frame, bg=COLORS['BACKGROUND'])
        status_frame.pack(side=tk.RIGHT)
        
        self.red_label = tk.Label(
            status_frame,
            text="RED: 0",
            font=('Arial', 16, 'bold'),
            bg=COLORS['RED'],
            fg='white',
            padx=15,
            pady=5
        )
        self.red_label.pack(side=tk.LEFT, padx=5)
        
        self.blue_label = tk.Label(
            status_frame,
            text="BLUE: 0",
            font=('Arial', 16, 'bold'),
            bg=COLORS['BLUE'],
            fg='white',
            padx=15,
            pady=5
        )
        self.blue_label.pack(side=tk.LEFT, padx=5)
        
        self.turn_label = tk.Label(
            status_frame,
            text="TURN: RED",
            font=('Arial', 16, 'bold'),
            bg=COLORS['TEXT'],
            fg='white',
            padx=15,
            pady=5
        )
        self.turn_label.pack(side=tk.LEFT, padx=5)
        
        # Translation controls (always show, but may be disabled)
        translation_frame = tk.Frame(header_frame, bg=COLORS['BACKGROUND'])
        translation_frame.pack(side=tk.RIGHT, padx=20)
        
        # Translate toggle button
        toggle_text = "🌐 Translation: OFF"
        if not self.translation_available:
            toggle_text = "🌐 Translation (Not Available)"
        
        self.translate_toggle = tk.Button(
            translation_frame,
            text=toggle_text,
            font=('Arial', 10),
            bg=COLORS['BUTTON_BG'] if self.translation_available else COLORS['ERROR'],
            fg='white',
            command=self.toggle_translation,
            padx=10,
            pady=5,
            state=tk.NORMAL if self.translation_available else tk.DISABLED
        )
        self.translate_toggle.pack(side=tk.LEFT, padx=5)
        self.hover_effect(self.translate_toggle)
        
        # Language selection
        self.language_combo = ttk.Combobox(
            translation_frame,
            values=list(COMMON_LANGUAGES.keys()),
            state='readonly' if self.translation_available else 'disabled',
            width=20,
            font=('Arial', 10)
        )
        self.language_combo.set('Chinese (Simplified)')
        self.language_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        self.language_combo.pack(side=tk.LEFT, padx=5)
        if not self.translation_available:
            self.language_combo.config(state='disabled')
        
        # Game board frame
        board_frame = tk.Frame(main_frame, bg=COLORS['BACKGROUND'])
        board_frame.pack(expand=True)
        
        # Create card buttons
        self.card_buttons = []
        for i in range(5):
            row = []
            for j in range(5):
                word = self.game.board[i][j]
                btn = tk.Button(
                    board_frame,
                    text=word,
                    font=('Arial', 10, 'bold'),
                    width=15,
                    height=4,
                    relief=tk.RAISED,
                    bd=3,
                    command=lambda w=word: self.on_card_click(w),
                    wraplength=120  # Allow text wrapping for longer words
                )
                btn.grid(row=i, column=j, padx=3, pady=3)
                row.append(btn)
            self.card_buttons.append(row)
        
        # Control frame
        self.control_frame = tk.Frame(main_frame, bg=COLORS['BACKGROUND'])
        self.control_frame.pack(fill=tk.X, pady=20)
        
        self.clue_label = tk.Label(
            self.control_frame,
            text="Waiting for clue...",
            font=('Arial', 18, 'bold'),
            bg=COLORS['BACKGROUND'],
            fg=COLORS['TEXT'],
            wraplength=600  # Allow text wrapping
        )
        self.clue_label.pack(pady=10)
        
        # Pass button (will be shown/hidden as needed)
        self.pass_button = tk.Button(
            self.control_frame,
            text="Pass",
            font=('Arial', 14, 'bold'),
            bg=COLORS['ERROR'],
            fg='white',
            command=self.player_pass,
            padx=30,
            pady=10,
            state=tk.DISABLED
        )
        self.pass_button.pack(pady=5)
        self.hover_effect(self.pass_button)
        
        # Button frame for menu and pass
        button_frame = tk.Frame(self.control_frame, bg=COLORS['BACKGROUND'])
        button_frame.pack(pady=10)
        # Intentionally leave this area for control buttons (menu moved to history panel)
        
        # History panel on the right
        self.setup_history_panel(container_frame)
        
        self.update_display()
        
        # Setup player input if needed
        if self.mode == 3 and self.game.turn == self.player_team:
            self.setup_spymaster_input()
        elif self.mode == 2 and self.game.turn == self.player_team:
            # Will be set up when clue is given
            pass
    
    def setup_history_panel(self, container_frame):
        """Setup history panel on the right side."""
        # Right side: History panel
        history_frame = tk.Frame(container_frame, bg=COLORS['BACKGROUND'], width=350)
        history_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(20, 0))
        history_frame.pack_propagate(False)
        
        # History title
        history_title = tk.Label(
            history_frame,
            text="Game History",
            font=('Arial', 18, 'bold'),
            bg=COLORS['BACKGROUND'],
            fg=COLORS['TEXT']
        )
        history_title.pack(pady=(0, 10))
        
        # Scrollable text widget for history
        text_frame = tk.Frame(history_frame, bg=COLORS['BACKGROUND'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_text = tk.Text(
            text_frame,
            font=('Courier', 10),
            bg='white',
            fg=COLORS['TEXT'],
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED,
            width=40,
            height=35
        )
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_text.yview)
        
        # Add welcome message
        self.add_history_entry("=== Game Started ===")

        # Main Menu button placed below the history panel for easier access
        menu_bottom_frame = tk.Frame(history_frame, bg=COLORS['BACKGROUND'])
        menu_bottom_frame.pack(fill=tk.X, pady=10)

        menu_btn = tk.Button(
            menu_bottom_frame,
            text="Main Menu",
            font=('Arial', 12),
            bg=COLORS['BUTTON_BG'],
            fg='white',
            command=self.show_menu,
            padx=20,
            pady=8
        )
        menu_btn.pack()
        self.hover_effect(menu_btn)
    
    def add_history_entry(self, entry: str):
        """Add an entry to the history panel."""
        if self.history_text:
            self.history_text.config(state=tk.NORMAL)
            self.history_text.insert(tk.END, entry + "\n")
            self.history_text.see(tk.END)
            self.history_text.config(state=tk.DISABLED)
    
    def update_display(self):
        """Update the board display."""
        if self.game is None:
            return
        
        # Update status
        self.red_label.config(text=f"RED: {self.game.red_remaining}")
        self.blue_label.config(text=f"BLUE: {self.game.blue_remaining}")
        
        turn_color = COLORS['RED'] if self.game.turn == 'RED' else COLORS['BLUE']
        self.turn_label.config(
            text=f"TURN: {self.game.turn}",
            bg=turn_color
        )
        
        # Update cards
        for i in range(5):
            for j in range(5):
                word = self.game.board[i][j]
                card_type = self.game.get_card_type(word)
                btn = self.card_buttons[i][j]
                
                # Get translation if enabled
                translation = ""
                if self.translation_enabled:
                    translation = self.translate_text(word)
                
                # Format text with translation
                if translation:
                    display_text = f"{word}\n{translation}"
                else:
                    display_text = word
                
                if word in self.game.revealed:
                    # Revealed card
                    bg_color = COLORS.get(card_type, COLORS['NEUTRAL'])
                    fg_color = 'white' if card_type in ['RED', 'BLUE', 'ASSASSIN'] else COLORS['TEXT']
                    # Use larger font for translations - make it more readable
                    font_size = 11 if translation else 10
                    # Keep original card size
                    btn.config(
                        text=display_text,
                        bg=bg_color,
                        fg=fg_color,
                        state=tk.DISABLED,
                        relief=tk.SUNKEN,
                        font=('Arial', font_size, 'bold')
                    )
                else:
                    # Hidden card
                    if self.mode == 3 and self.game.turn == self.player_team:
                        # Spymaster sees secret
                        bg_color = COLORS.get(card_type, COLORS['NEUTRAL'])
                        fg_color = 'white' if card_type in ['RED', 'BLUE', 'ASSASSIN'] else COLORS['TEXT']
                        if translation:
                            spymaster_text = f"{word}\n({card_type[0]})\n{translation}"
                        else:
                            spymaster_text = f"{word}\n({card_type[0]})"
                        btn.config(
                            text=spymaster_text,
                            bg=bg_color,
                            fg=fg_color,
                            font=('Arial', 10 if translation else 9, 'bold'),
                            state=tk.DISABLED
                        )
                    else:
                        # Normal hidden card
                        # Enable if player operative turn and it's their turn
                        is_player_turn = (self.mode == 2 and 
                                         self.game.turn == self.player_team and 
                                         self.turn_in_progress)
                        # Use larger font for translations
                        font_size = 11 if translation else 10
                        btn.config(
                            text=display_text,
                            bg=COLORS['HIDDEN'],
                            fg=COLORS['TEXT'],
                            state=tk.NORMAL if is_player_turn else tk.DISABLED,
                            relief=tk.RAISED,
                            font=('Arial', font_size, 'bold')
                        )
    
    def on_card_click(self, word: str):
        """Handle card click."""
        if not self.turn_in_progress:
            return
        
        if self.mode == 2 and self.game.turn == self.player_team:
            # Player operative making guess
            self.make_guess(word)
        else:
            # AI turn or not player's turn
            return
    
    def player_pass(self):
        """Handle player passing their turn."""
        if not self.turn_in_progress:
            return
        
        # Confirm pass
        result = messagebox.askyesno("Pass Turn", "Are you sure you want to pass this turn?")
        if not result:
            return
        
        # Add to history
        if self.current_turn_entry:
            self.add_history_entry(f"  → Passed")
            self.current_turn_entry = None
        
        # End turn
        self.turn_in_progress = False
        self.game.turn = 'BLUE' if self.game.turn == 'RED' else 'RED'
        self.pass_button.config(state=tk.DISABLED)
        self.clue_label.config(text="You passed. Waiting for next clue...")
        self.update_display()
        self.root.after(1000, self.process_turn)
    
    def make_guess(self, word: str):
        """Process a guess."""
        if word in self.game.revealed:
            messagebox.showwarning("Already Revealed", f"'{word}' has already been revealed!")
            return
        
        if word not in self.game.words:
            messagebox.showerror("Invalid", f"'{word}' is not on the board!")
            return
        
        success, card_type = self.game.reveal_card(word)
        
        if not success:
            return
        
        self.guesses_made += 1
        
        # Add to history
        guesser = "You" if self.mode == 2 else "AI"
        result_symbol = "✓" if card_type == self.game.turn else "✗"
        self.add_history_entry(f"  {guesser} guessed: {word} {result_symbol} ({card_type})")
        
        # Show result
        color = COLORS.get(card_type, COLORS['NEUTRAL'])
        messagebox.showinfo(
            "Result",
            f"Revealed: {word}\nType: {card_type}"
        )
        
        # Check win condition
        winner = self.game.check_win_condition()
        if winner:
            self.game.game_over = True
            self.game.winner = winner
            self.add_history_entry(f"\n=== {winner} TEAM WINS! ===")
            messagebox.showinfo("Game Over", f"{winner} TEAM WINS!")
            self.show_menu()
            return
        
        # Check for assassin
        if card_type == 'ASSASSIN':
            other_team = 'BLUE' if self.game.turn == 'RED' else 'RED'
            self.game.game_over = True
            self.game.winner = other_team
            self.add_history_entry(f"\n=== ASSASSIN REVEALED! {other_team} TEAM WINS! ===")
            messagebox.showerror("Game Over", f"ASSASSIN REVEALED!\n{other_team} TEAM WINS!")
            self.show_menu()
            return
        
        # Update display
        self.update_display()
        
        # Check if turn should end
        if card_type != self.game.turn:
            # Wrong card - turn ends
            self.turn_in_progress = False
            self.game.turn = 'BLUE' if self.game.turn == 'RED' else 'RED'
            self.pass_button.config(state=tk.DISABLED)
            self.current_turn_entry = None
            self.clue_label.config(text="Turn ended. Waiting for next clue...")
            self.root.after(1000, self.process_turn)
        elif self.guesses_made >= self.max_guesses:
            # Reached max guesses
            self.turn_in_progress = False
            self.game.turn = 'BLUE' if self.game.turn == 'RED' else 'RED'
            self.pass_button.config(state=tk.DISABLED)
            self.current_turn_entry = None
            self.clue_label.config(text="Max guesses reached. Waiting for next clue...")
            self.root.after(1000, self.process_turn)
    
    def setup_spymaster_input(self):
        """Setup input for player spymaster."""
        # Clear control frame
        for widget in self.control_frame.winfo_children():
            widget.destroy()
        
        # Disable pass button during spymaster input (not applicable)
        if self.pass_button:
            self.pass_button.config(state=tk.DISABLED)
        
        tk.Label(
            self.control_frame,
            text="YOUR TURN - SPYMASTER",
            font=('Arial', 18, 'bold'),
            bg=COLORS['BACKGROUND'],
            fg=COLORS['TEXT']
        ).pack(pady=10)
        
        input_frame = tk.Frame(self.control_frame, bg=COLORS['BACKGROUND'])
        input_frame.pack(pady=10)
        
        tk.Label(
            input_frame,
            text="Clue Word:",
            font=('Arial', 12),
            bg=COLORS['BACKGROUND'],
            fg=COLORS['TEXT']
        ).pack(side=tk.LEFT, padx=5)
        
        clue_entry = tk.Entry(input_frame, font=('Arial', 12), width=20)
        clue_entry.pack(side=tk.LEFT, padx=5)
        clue_entry.focus()
        
        tk.Label(
            input_frame,
            text="Number:",
            font=('Arial', 12),
            bg=COLORS['BACKGROUND'],
            fg=COLORS['TEXT']
        ).pack(side=tk.LEFT, padx=5)
        
        count_entry = tk.Entry(input_frame, font=('Arial', 12), width=5)
        count_entry.pack(side=tk.LEFT, padx=5)
        
        def submit_clue():
            clue = clue_entry.get().strip().upper()
            try:
                count = int(count_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number!")
                return
            
            if not clue:
                messagebox.showerror("Error", "Please enter a clue word!")
                return
            
            if clue in self.game.words:
                messagebox.showerror("Error", "Clue cannot be a word on the board!")
                return
            
            self.current_clue = clue
            self.current_count = count
            self.max_guesses = count + 1
            self.guesses_made = 0
            self.turn_in_progress = True
            
            # Add to history
            self.current_turn_entry = f"Turn {self.game.turn}: You gave clue '{clue}' ({count})"
            self.add_history_entry(f"\n{self.current_turn_entry}")
            
            # Clear input
            for widget in self.control_frame.winfo_children():
                widget.destroy()
            
            clue_text = f"Clue: {clue} ({count} words)\nAI is guessing..."
            # Put translation inline after the clue instead of below it
            base_clue = f"Clue: {clue} ({count} words)"
            if self.translation_enabled:
                clue_translation = self.translate_text(clue)
                if clue_translation:
                    base_clue = f"{base_clue} — {clue_translation}"
            clue_text = f"{base_clue}\nAI is guessing..."
            
            self.clue_label = tk.Label(
                self.control_frame,
                text=clue_text,
                font=('Arial', 16, 'bold'),
                bg=COLORS['BACKGROUND'],
                fg=COLORS['TEXT'],
                wraplength=600
            )
            self.clue_label.pack(pady=10)
            
            self.update_display()
            self.root.after(500, self.ai_guesser_turn)
        
        submit_btn = tk.Button(
            input_frame,
            text="Submit Clue",
            font=('Arial', 12, 'bold'),
            bg=COLORS['SUCCESS'],
            fg='white',
            command=submit_clue,
            padx=20,
            pady=5
        )
        submit_btn.pack(side=tk.LEFT, padx=10)
        self.hover_effect(submit_btn)
        
        # Bind Enter key
        clue_entry.bind('<Return>', lambda e: submit_clue())
        count_entry.bind('<Return>', lambda e: submit_clue())
    
    def ai_turn(self):
        """Process AI turn (wrapper for compatibility)."""
        self.process_turn()
    
    def process_turn(self):
        """Process the current turn."""
        if self.game.game_over:
            return
        
        current_team = self.game.turn
        
        # Check if player is spymaster
        if self.mode == 3 and current_team == self.player_team:
            # Player spymaster turn
            self.setup_spymaster_input()
            return
        
        # AI spymaster gives clue
        if current_team == 'RED':
            spymaster = self.red_spymaster
        else:
            spymaster = self.blue_spymaster
        
        clue, count = spymaster.generate_clue(self.game)
        
        if clue == "PASS":
            self.clue_label.config(text="AI Spymaster passed. Switching turns...")
            self.add_history_entry(f"\nTurn {current_team}: AI Spymaster PASSED")
            self.game.turn = 'BLUE' if self.game.turn == 'RED' else 'RED'
            self.root.after(2000, self.process_turn)
            return
        
        self.current_clue = clue
        self.current_count = count
        self.max_guesses = count + 1
        self.guesses_made = 0
        self.turn_in_progress = True
        
        # Add to history
        spymaster_name = "You" if self.mode == 3 and current_team == self.player_team else "AI"
        self.current_turn_entry = f"Turn {current_team}: {spymaster_name} gave clue '{clue}' ({count})"
        self.add_history_entry(f"\n{self.current_turn_entry}")
        
        self.update_display()
        
        # AI or player guesses
        if self.mode == 2 and current_team == self.player_team:
            # Player operative guesses
            # Show translation inline after the clue
            base_clue = f"Clue: {clue} ({count} words)"
            if self.translation_enabled:
                clue_translation = self.translate_text(clue)
                if clue_translation:
                    base_clue = f"{base_clue} — {clue_translation}"
            clue_text = f"{base_clue}\nYour turn to guess! Click a card or pass."
            self.clue_label.config(text=clue_text, font=('Arial', 16, 'bold'))
            # Show pass button for player operative
            self.pass_button.config(state=tk.NORMAL)
            self.update_display()
        else:
            # AI guesses - hide pass button
            self.pass_button.config(state=tk.DISABLED)
            # Show translation inline after the AI clue
            base_clue = f"AI Clue: {clue} ({count} words)"
            if self.translation_enabled:
                clue_translation = self.translate_text(clue)
                if clue_translation:
                    base_clue = f"{base_clue} — {clue_translation}"
            clue_text = f"{base_clue}\nAI is guessing..."
            self.clue_label.config(text=clue_text, font=('Arial', 16, 'bold'))
            self.root.after(1000, self.ai_guesser_turn)
    
    def ai_guesser_turn(self):
        """Process AI guesser turn."""
        if self.game.game_over or not self.turn_in_progress:
            return
        
        if self.guesses_made >= self.max_guesses:
            # Turn over
            self.turn_in_progress = False
            self.game.turn = 'BLUE' if self.game.turn == 'RED' else 'RED'
            self.clue_label.config(text="Max guesses reached. Next turn...")
            self.update_display()
            self.current_turn_entry = None
            self.root.after(2000, self.process_turn)
            return
        
        current_team = self.game.turn
        if current_team == 'RED':
            guesser = self.red_guesser
        else:
            guesser = self.blue_guesser
        
        guess = guesser.make_guess(self.game, self.current_clue, self.current_count)
        
        if guess is None:
            # AI passes
            self.turn_in_progress = False
            self.game.turn = 'BLUE' if self.game.turn == 'RED' else 'RED'
            self.clue_label.config(text="AI passed. Next turn...")
            self.add_history_entry(f"  → AI passed")
            self.update_display()
            self.current_turn_entry = None
            self.root.after(2000, self.process_turn)
            return
        
        # Process guess
        success, card_type = self.game.reveal_card(guess)
        
        if not success:
            self.ai_guesser_turn()
            return
        
        self.guesses_made += 1
        
        # Update display
        self.update_display()
        
        # Add to history
        result_symbol = "✓" if card_type == current_team else "✗"
        self.add_history_entry(f"  AI guessed: {guess} {result_symbol} ({card_type})")
        
        # Show result message
        result_text = f"AI guessed: {guess} → {card_type}"
        if self.translation_enabled:
            guess_translation = self.translate_text(guess)
            if guess_translation:
                result_text += f"\n({guess_translation})"
        self.clue_label.config(text=result_text)
        
        # Check win condition
        winner = self.game.check_win_condition()
        if winner:
            self.game.game_over = True
            self.game.winner = winner
            self.add_history_entry(f"\n=== {winner} TEAM WINS! ===")
            messagebox.showinfo("Game Over", f"{winner} TEAM WINS!")
            self.show_menu()
            return
        
        # Check for assassin
        if card_type == 'ASSASSIN':
            other_team = 'BLUE' if current_team == 'RED' else 'RED'
            self.game.game_over = True
            self.game.winner = other_team
            self.add_history_entry(f"\n=== ASSASSIN REVEALED! {other_team} TEAM WINS! ===")
            messagebox.showerror("Game Over", f"ASSASSIN REVEALED!\n{other_team} TEAM WINS!")
            self.show_menu()
            return
        
        # Check if turn continues
        if card_type != current_team:
            # Wrong card - turn ends
            self.turn_in_progress = False
            self.game.turn = 'BLUE' if self.game.turn == 'RED' else 'RED'
            self.clue_label.config(text=f"Wrong card ({card_type}). Turn ends.")
            self.update_display()
            self.current_turn_entry = None
            self.root.after(2000, self.process_turn)
        else:
            # Correct card - continue guessing
            self.root.after(1500, self.ai_guesser_turn)
    
    def translate_text(self, text: str) -> str:
        """Translate text to selected language."""
        if not self.translation_available or not self.translation_enabled or not text:
            return ""
        
        # Check cache
        cache_key = f"{text}_{self.translation_language}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        try:
            if self.translator is None:
                # Try to reinitialize translator
                try:
                    from googletrans import Translator
                    self.translator = Translator()
                except Exception as e:
                    print(f"Failed to initialize translator: {e}")
                    return ""
            
            if self.translator:
                # Use a smaller batch or single translation
                translation = self.translator.translate(text, dest=self.translation_language)
                if translation and translation.text:
                    translated = translation.text
                    self.translation_cache[cache_key] = translated
                    return translated
        except Exception as e:
            print(f"Translation error for '{text}': {e}")
            # Don't cache failed translations
            return ""
        
        return ""
    
    def toggle_translation(self):
        """Toggle translation on/off."""
        if not self.translation_available:
            result = messagebox.askyesno(
                "Translation Not Available",
                "Translation feature requires the 'googletrans' library.\n\n"
                "Would you like to install it now?\n"
                "(You can also install manually: pip install googletrans==4.0.0rc1)"
            )
            if result:
                import subprocess
                import sys
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "googletrans==4.0.0rc1"])
                    messagebox.showinfo("Success", "googletrans installed! Please restart the application.")
                    # Try to reimport
                    try:
                        from googletrans import Translator
                        self.translation_available = True
                        self.translator = Translator()
                        self.translate_toggle.config(
                            text="🌐 Translation: OFF",
                            bg=COLORS['BUTTON_BG'],
                            state=tk.NORMAL
                        )
                        self.language_combo.config(state='readonly')
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to initialize translator: {e}")
                except Exception as e:
                    messagebox.showerror("Installation Failed", f"Failed to install googletrans: {e}\n\nPlease install manually:\npip install googletrans==4.0.0rc1")
            return
        
        self.translation_enabled = not self.translation_enabled
        
        if self.translation_enabled:
            self.translate_toggle.config(text="🌐 Translation: ON", bg=COLORS['SUCCESS'])
            self.language_combo.config(state='readonly')
            # Clear cache and retranslate everything
            self.translation_cache.clear()
        else:
            self.translate_toggle.config(text="🌐 Translation: OFF", bg=COLORS['BUTTON_BG'])
            self.language_combo.config(state='disabled')
        
        # Update display with new translation state
        self.update_display()
        if self.current_clue:
            self.update_clue_display()
    
    def on_language_change(self, event=None):
        """Handle language selection change."""
        if self.translation_available:
            selected_lang = self.language_combo.get()
            if selected_lang in COMMON_LANGUAGES:
                self.translation_language = COMMON_LANGUAGES[selected_lang]
                # Clear cache for new language
                self.translation_cache.clear()
                # Update display
                self.update_display()
                if self.current_clue:
                    self.update_clue_display()
    
    def update_clue_display(self):
        """Update clue label with translation."""
        if not self.current_clue:
            return
        # Rebuild the clue label's first line and insert translation inline
        if self.translation_enabled:
            clue_translation = self.translate_text(self.current_clue)
        else:
            clue_translation = ""

        current_text = self.clue_label.cget('text')
        # Split first line (the clue) from the rest
        if '\n' in current_text:
            first_line, rest = current_text.split('\n', 1)
            rest = '\n' + rest
        else:
            first_line = current_text
            rest = ''

        # Remove any existing inline translation from the first line
        if ' — ' in first_line:
            first_line = first_line.split(' — ')[0]

        if clue_translation:
            first_line = f"{first_line} — {clue_translation}"

        self.clue_label.config(
            text=f"{first_line}{rest}",
            font=('Arial', 16, 'bold'),
            wraplength=600
        )
    
    def hover_effect(self, button):
        """Add hover effect to button."""
        original_bg = button.cget('bg')

        def on_enter(e):
            button.config(cursor="hand2")
        
        def on_leave(e):
            button.config(cursor="")
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def run(self):
        """Start the GUI."""
        self.root.mainloop()


if __name__ == "__main__":
    app = CodenamesGUI()
    app.run()

