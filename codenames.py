"""
Codenames AI Game
A micro Python implementation of the famous board game Codenames with AI players.
"""

import random
import sys
import time
from typing import List, Tuple, Optional

# Word pool for the game
WORD_POOL = [
    "APPLE", "BALL", "BANK", "BEACH", "BEAR", "BED", "BOOK", "BOTTLE", "BRIDGE",
    "BROTHER", "CAT", "CHINA", "CHURCH", "CIRCLE", "CLOUD", "CODE", "COOK", "CROSS",
    "CROWN", "DANCE", "DIAMOND", "DOCTOR", "DRAGON", "DRESS", "DRILL", "DROP", "DUCK",
    "EGG", "EGYPT", "ELEPHANT", "ENGINE", "ENGLAND", "EYE", "FACE", "FAIR", "FALL",
    "FAN", "FENCE", "FIELD", "FIGHTER", "FIGURE", "FILE", "FILM", "FIRE", "FISH",
    "FLUTE", "FLY", "FOOT", "FORCE", "FOREST", "FORK", "FRANCE", "GAME", "GAS",
    "GENIUS", "GERMANY", "GHOST", "GIANT", "GLASS", "GLOVE", "GOLD", "GRACE", "GRASS",
    "GREEN", "GROUND", "HAMMER", "HAND", "HAT", "HAWK", "HEAD", "HEART", "HELICOPTER",
    "HIMALAYAS", "HOLE", "HOLLYWOOD", "HONEY", "HORN", "HORSE", "HOSPITAL", "HOTEL",
    "ICE", "ICON", "IGLOO", "INDIA", "IRON", "IVORY", "JACK", "JAM", "JET",
    "JUPITER", "KANGAROO", "KETCHUP", "KEY", "KING", "KIWI", "KNIFE", "KNIGHT",
    "LAB", "LAP", "LASER", "LAWYER", "LEAD", "LEMON", "LEPRECHAUN", "LIFE", "LIGHT",
    "LIMOUSINE", "LINE", "LINK", "LION", "LITTER", "LOCH", "LOCK", "LOG", "LONDON",
    "LUCK", "MAIL", "MAMMOTH", "MAPLE", "MARCH", "MASS", "MATCH", "MERCURY", "MEXICO",
    "MICROSCOPE", "MILLIONAIRE", "MINE", "MINT", "MISSILE", "MODEL", "MOLE", "MOON",
    "MOSCOW", "MOUNT", "MOUSE", "MOUTH", "MUG", "NAIL", "NEEDLE", "NET", "NEW YORK",
    "NIGHT", "NINJA", "NOTE", "NOVEL", "NURSE", "NUT", "OCTOPUS", "OIL", "OLIVE",
    "OLYMPUS", "OPERA", "ORANGE", "ORGAN", "PALM", "PAN", "PANTS", "PAPER", "PARACHUTE",
    "PARK", "PART", "PASS", "PASTE", "PENGUIN", "PHOENIX", "PIANO", "PIE", "PILOT",
    "PIN", "PIPE", "PIRATE", "PISTOL", "PIT", "PITCH", "PLANE", "PLANT", "PLASTIC",
    "PLATE", "PLAY", "PLOT", "POINT", "POISON", "POLE", "POLICE", "POOL", "PORT",
    "POST", "POUND", "PRESS", "PRINCESS", "PUMPKIN", "PUPIL", "PYRAMID", "QUEEN",
    "QUILL", "RABBIT", "RACKET", "RAY", "REVOLUTION", "RING", "ROBIN", "ROCK", "ROME",
    "ROOT", "ROSE", "ROULETTE", "ROUND", "ROW", "ROYAL", "RUBBER", "RULE", "SATELLITE",
    "SATURN", "SCALE", "SCHOOL", "SCIENTIST", "SCORPION", "SCREEN", "SCUBA", "SEAL",
    "SERVER", "SHADOW", "SHAKESPEARE", "SHARK", "SHIP", "SHOE", "SHOP", "SHOT", "SINK",
    "SKATE", "SKI", "SKULL", "SLIP", "SLUG", "SMUGGLER", "SNOW", "SNOWMAN", "SOCK",
    "SOLDIER", "SOUL", "SPACE", "SPELL", "SPIDER", "SPIKE", "SPINE", "SPOT", "SPRING",
    "SPY", "SQUARE", "STADIUM", "STAFF", "STAMP", "STAR", "STATE", "STICK", "STOCK",
    "STORM", "STOVE", "STRAW", "STREAM", "STRIKE", "STRING", "SUB", "SUIT", "SUPERHERO",
    "SWING", "SWITCH", "TABLE", "TABLET", "TAG", "TAIL", "TAP", "TASTE", "THIEF",
    "THUMB", "TICK", "TIE", "TIGER", "TIME", "TOKYO", "TOOTH", "TORCH", "TOWER",
    "TRACK", "TRAIN", "TRIANGLE", "TRIP", "TRUNK", "TUBE", "TURKEY", "UNDERTAKER",
    "UNICORN", "VACUUM", "VAN", "VET", "WAKE", "WALL", "WAR", "WASHER", "WASHINGTON",
    "WATCH", "WATER", "WAVE", "WEB", "WELL", "WHALE", "WHIP", "WIND", "WITCH",
    "WIZARD", "WOLF", "WOOD", "WOOL", "WORLD", "WORM", "YARD"
]


class CodenamesGame:
    """Main game class for Codenames AI."""
    
    def __init__(self):
        self.board_size = 5
        self.words = []
        self.board = []  # 5x5 grid
        self.card_types = []  # 'RED', 'BLUE', 'NEUTRAL', 'ASSASSIN'
        self.revealed = []  # Which cards have been revealed
        self.turn = 'RED'  # RED starts
        self.red_remaining = 9
        self.blue_remaining = 8
        self.game_over = False
        self.winner = None

    def setup_board(self):
        """Initialize the game board with random words and card assignments."""
        # Select 25 random words
        self.words = random.sample(WORD_POOL, self.board_size ** 2)
        
        # Create board structure
        self.board = [[self.words[i * self.board_size + j] 
                      for j in range(self.board_size)]
                     for i in range(self.board_size)]
        
        # Assign card types: 9 RED, 8 BLUE, 7 NEUTRAL, 1 ASSASSIN
        card_assignments = (['RED'] * 9 + ['BLUE'] * 8 + 
                           ['NEUTRAL'] * 7 + ['ASSASSIN'] * 1)
        random.shuffle(card_assignments)
        self.card_types = {}
        
        # Random starting team
        first_team = random.choice(['RED', 'BLUE'])
        if first_team == 'RED':
            card_assignments = (['RED'] * 9 + ['BLUE'] * 8 + 
                               ['NEUTRAL'] * 7 + ['ASSASSIN'] * 1)
        else:
            card_assignments = (['RED'] * 8 + ['BLUE'] * 9 + 
                               ['NEUTRAL'] * 7 + ['ASSASSIN'] * 1)
        random.shuffle(card_assignments)
        
        for idx, word in enumerate(self.words):
            self.card_types[word] = card_assignments[idx]
        
        # Count remaining cards
        self.red_remaining = sum(1 for ct in card_assignments if ct == 'RED')
        self.blue_remaining = sum(1 for ct in card_assignments if ct == 'BLUE')
        
        self.revealed = set()
        self.turn = first_team
        self.game_over = False
        self.winner = None
        
    def get_card_type(self, word: str) -> str:
        """Get the type of a card (what team it belongs to)."""
        return self.card_types.get(word, 'UNKNOWN')
    
    def reveal_card(self, word: str) -> Tuple[bool, str]:
        """
        Reveal a card and return (success, card_type).
        success is False if word not found or already revealed.
        """
        if word not in self.words or word in self.revealed:
            return False, None
        
        self.revealed.add(word)
        card_type = self.get_card_type(word)
        
        if card_type == 'RED':
            self.red_remaining -= 1
        elif card_type == 'BLUE':
            self.blue_remaining -= 1
        
        return True, card_type
    
    def check_win_condition(self) -> Optional[str]:
        """Check if game is over and return winner, or None."""
        if self.red_remaining == 0:
            return 'RED'
        if self.blue_remaining == 0:
            return 'BLUE'
        return None
    
    def display_board(self, show_all=False):
        """Display the game board."""
        print("\n" + "=" * 70)
        print(f"CODENAMES BOARD - Turn: {self.turn}")
        print(f"Red remaining: {self.red_remaining} | Blue remaining: {self.blue_remaining}")
        print("=" * 70 + "\n")
        
        # Header
        print("   ", end="")
        for j in range(self.board_size):
            print(f" {j+1:2} ", end="")
        print()
        
        # Board rows
        for i in range(self.board_size):
            print(f"{chr(65+i)}  ", end="")  # A, B, C, D, E
            for j in range(self.board_size):
                word = self.board[i][j]
                if show_all:
                    # Show card types
                    card_type = self.get_card_type(word)
                    symbols = {'RED': '[R]', 'BLUE': '[B]', 'NEUTRAL': '[N]', 'ASSASSIN': '[X]'}
                    symbol = symbols.get(card_type, '[?]')
                    print(f"{symbol}{word[:3]:3}", end=" ")
                elif word in self.revealed:
                    card_type = self.get_card_type(word)
                    symbols = {'RED': '[R]', 'BLUE': '[B]', 'NEUTRAL': '[N]', 'ASSASSIN': '[X]'}
                    symbol = symbols.get(card_type, '[?]')
                    print(f"{symbol}{word[:3]:3}", end=" ")
                else:
                    print(f" ? {word[:3]:3}", end=" ")
            print()
        print()


class AISpymaster:
    """AI that generates clues for the team."""
    
    def __init__(self, team: str):
        self.team = team
        
    def generate_clue(self, game: CodenamesGame) -> Tuple[str, int]:
        """
        Generate a clue (word, number) for the team's cards.
        Returns (clue_word, number_of_associated_words)
        """
        # Get unrevealed cards for this team
        team_words = []
        for word in game.words:
            if word not in game.revealed and game.get_card_type(word) == self.team:
                team_words.append(word)
        
        if not team_words:
            return ("PASS", 0)
        
        # Simple strategy: look for words that could connect team words
        # Find common themes or associations
        clue_scores = {}
        
        # For each team word, try to find connecting clues
        for word in team_words:
            # Simple word associations (you could make this smarter with word embeddings)
            potential_clues = self._get_potential_clues(word)
            for clue in potential_clues:
                if clue not in clue_scores:
                    clue_scores[clue] = []
                clue_scores[clue].append(word)
        
        # Find the clue that connects the most words
        best_clue = None
        best_count = 0
        
        for clue, associated_words in clue_scores.items():
            # Make sure clue isn't on the board
            if clue.upper() not in game.words:
                unique_words = len(set(associated_words))
                if unique_words > best_count and unique_words <= len(team_words):
                    best_count = unique_words
                    best_clue = clue
        
        if best_clue and best_count > 0:
            return (best_clue.upper(), min(best_count, len(team_words)))
        
        # Fallback: single word clues
        if team_words:
            return (team_words[0], 1)
        
        return ("PASS", 0)
    
    def _get_potential_clues(self, word: str) -> List[str]:
        """Generate potential clue words based on a target word."""
        word_lower = word.lower()
        
        # Simple associations (micro version - expandable)
        associations = {
            'animal': ['cat', 'dog', 'bear', 'tiger', 'lion', 'elephant', 'rabbit'],
            'body': ['hand', 'head', 'eye', 'foot', 'face', 'heart'],
            'nature': ['tree', 'forest', 'river', 'mountain', 'ocean', 'beach'],
            'building': ['house', 'school', 'hospital', 'bank', 'hotel', 'church'],
            'color': ['red', 'blue', 'green', 'yellow', 'black', 'white'],
            'food': ['apple', 'bread', 'cake', 'cheese', 'meat'],
            'sport': ['ball', 'game', 'player', 'team', 'field'],
            'water': ['water', 'ocean', 'river', 'lake', 'beach', 'fish'],
            'royal': ['king', 'queen', 'crown', 'royal', 'prince'],
            'war': ['soldier', 'war', 'gun', 'battle', 'army'],
            'space': ['moon', 'star', 'planet', 'space', 'rocket'],
            'music': ['song', 'music', 'piano', 'note', 'sound'],
            'time': ['clock', 'time', 'hour', 'minute', 'day'],
            'round': ['ball', 'circle', 'ring', 'round', 'wheel'],
            'sharp': ['knife', 'sword', 'needle', 'point', 'blade']
        }
        
        potential = []
        for category, words in associations.items():
            if word_lower in words:
                # Use category name or related words
                potential.append(category)
                potential.extend([w for w in words if w != word_lower])
        
        # Add some generic clues based on word characteristics
        if len(word) > 4:
            potential.append(word[:4] + "ING")  # Simple transform
        if 'er' in word_lower:
            potential.append(word_lower.replace('er', ''))
        
        return potential[:5]  # Limit to top 5


class AIGuesser:
    """AI that makes guesses based on clues."""
    
    def __init__(self, team: str):
        self.team = team
        self.recent_clue = None
        self.recent_count = 0
        
    def make_guess(self, game: CodenamesGame, clue: str, count: int) -> Optional[str]:
        """
        Make a guess based on the clue.
        Returns word to guess, or None to pass.
        """
        self.recent_clue = clue
        self.recent_count = count
        
        if clue == "PASS" or count == 0:
            return None
        
        # Get unrevealed words
        available = [w for w in game.words if w not in game.revealed]
        
        if not available:
            return None
        
        # Score words based on relevance to clue
        scores = {}
        clue_lower = clue.lower()
        
        for word in available:
            score = self._score_word(clue_lower, word.lower())
            scores[word] = score
        
        # Sort by score
        sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Make best guess (top scoring word)
        if sorted_words:
            best_word, best_score = sorted_words[0]
            if best_score > 0:  # Only guess if there's some relevance
                return best_word
        
        return None
    
    def _score_word(self, clue: str, word: str) -> float:
        """Score how well a word matches a clue."""
        score = 0.0
        
        # Exact match
        if clue == word:
            return 100.0
        
        # Substring match
        if clue in word or word in clue:
            score += 30.0
        
        # Character overlap
        clue_chars = set(clue)
        word_chars = set(word)
        overlap = len(clue_chars & word_chars)
        score += overlap * 5.0
        
        # Length similarity
        length_diff = abs(len(clue) - len(word))
        score += max(0, 10 - length_diff)
        
        # Semantic associations (simple keyword matching)
        associations = {
            'animal': ['cat', 'dog', 'bear', 'tiger', 'lion', 'elephant'],
            'body': ['hand', 'head', 'eye', 'foot', 'face'],
            'nature': ['tree', 'forest', 'river', 'mountain'],
            'water': ['water', 'ocean', 'river', 'beach', 'fish'],
            'royal': ['king', 'queen', 'crown', 'royal'],
            'round': ['ball', 'circle', 'ring', 'wheel'],
        }
        
        for category, words in associations.items():
            if category == clue and word in words:
                score += 50.0
            if word in words and any(w == clue for w in words):
                score += 30.0
        
        return score


def get_mode_selection():
    """Get game mode from player."""
    print("=" * 70)
    print("CODENAMES AI GAME")
    print("=" * 70)
    print("\nSelect game mode:")
    print("1. AI vs AI (Watch the AI play)")
    print("2. Player as Field Operative (You guess, AI gives clues)")
    print("3. Player as Spymaster (You give clues, AI guesses)")
    
    while True:
        try:
            choice = input("\nEnter choice (1-3): ").strip()
            if choice in ['1', '2', '3']:
                return int(choice)
            print("Invalid choice. Please enter 1, 2, or 3.")
        except (EOFError, KeyboardInterrupt):
            return 1  # Default to AI vs AI


def get_team_selection():
    """Get team selection from player."""
    print("\nSelect your team:")
    print("1. RED Team")
    print("2. BLUE Team")
    
    while True:
        try:
            choice = input("\nEnter choice (1-2): ").strip()
            if choice == '1':
                return 'RED'
            elif choice == '2':
                return 'BLUE'
            print("Invalid choice. Please enter 1 or 2.")
        except (EOFError, KeyboardInterrupt):
            return 'RED'  # Default to RED


def player_input_clue(game: CodenamesGame, team: str) -> Tuple[str, int]:
    """Get clue input from player spymaster."""
    print(f"\n[YOUR TURN - {team} SPYMASTER]")
    print("You can see all card assignments (shown above). Give a clue that connects your team's words!")
    print("Enter 'PASS' to skip this turn.\n")
    
    while True:
        try:
            clue_input = input("Enter your clue (word): ").strip().upper()
            if not clue_input:
                print("Please enter a clue word.")
                continue
            
            if clue_input == "PASS":
                return ("PASS", 0)
            
            # Check if clue is on the board (not allowed)
            if clue_input in game.words:
                print(f"Error: '{clue_input}' is on the board! You cannot use board words as clues.")
                continue
            
            # Get number of words
            while True:
                try:
                    count_input = input("How many words does this clue relate to? (1-9): ").strip()
                    count = int(count_input)
                    if 1 <= count <= 9:
                        return (clue_input, count)
                    print("Please enter a number between 1 and 9.")
                except ValueError:
                    print("Please enter a valid number.")
                except (EOFError, KeyboardInterrupt):
                    return ("PASS", 0)
                    
        except (EOFError, KeyboardInterrupt):
            return ("PASS", 0)


def player_input_guess(game: CodenamesGame, clue: str, count: int) -> Optional[str]:
    """Get guess input from player field operative."""
    print(f"\n[YOUR TURN - FIELD OPERATIVE]")
    print(f"Clue: '{clue}' ({count} words)")
    print(f"You can make up to {count + 1} guesses.")
    print("Enter a word from the board, or 'PASS' to stop guessing.\n")
    
    # Show available words
    available = [w for w in game.words if w not in game.revealed]
    print("Available words:", ", ".join(available))
    
    while True:
        try:
            guess = input("\nEnter your guess (or 'PASS'): ").strip().upper()
            
            if guess == "PASS" or not guess:
                return None
            
            if guess not in game.words:
                print(f"'{guess}' is not on the board. Please enter a valid word.")
                continue
            
            if guess in game.revealed:
                print(f"'{guess}' has already been revealed. Please choose another word.")
                continue
            
            return guess
            
        except (EOFError, KeyboardInterrupt):
            return None


def play_game():
    """Main game loop."""
    # Get game mode
    mode = get_mode_selection()
    
    game = CodenamesGame()
    game.setup_board()
    
    # Determine player team if in player modes
    player_team = None
    if mode in [2, 3]:
        player_team = get_team_selection()
    
    # Create AI players
    red_spymaster = AISpymaster('RED')
    red_guesser = AIGuesser('RED')
    blue_spymaster = AISpymaster('BLUE')
    blue_guesser = AIGuesser('BLUE')
    
    turn_count = 0
    max_turns = 50  # Prevent infinite loops
    
    # Show initial board based on mode
    if mode == 1:
        # AI vs AI - show secret view
        print("\n[Initial board - Secret view]")
        game.display_board(show_all=True)
    elif mode == 2:
        # Player as operative - don't show secret (they'll see regular board)
        print("\n[Game starting! You are a field operative for", player_team, "team.]")
        print("The AI spymaster will give you clues. Good luck!")
    elif mode == 3:
        # Player as spymaster - show secret view
        print("\n[Initial board - Your secret view as spymaster]")
        game.display_board(show_all=True)
    
    # Wait for user input if interactive, otherwise auto-start
    if sys.stdin.isatty():
        try:
            input("\nPress Enter to start the game...")
        except (EOFError, KeyboardInterrupt):
            pass
    else:
        time.sleep(1)
    
    while not game.game_over and turn_count < max_turns:
        turn_count += 1
        print(f"\n{'=' * 70}")
        print(f"TURN {turn_count} - {game.turn} TEAM")
        print('=' * 70)
        
        # Get current team's AI
        if game.turn == 'RED':
            spymaster = red_spymaster
            guesser = red_guesser
            current_team = 'RED'
        else:
            spymaster = blue_spymaster
            guesser = blue_guesser
            current_team = 'BLUE'
        
        # Show current board (show secret if player is spymaster, otherwise regular board)
        if mode == 3 and current_team == player_team:
            # Player spymaster sees secret board on their turn
            print("\n[Secret Board - Your View]")
            game.display_board(show_all=True)
        else:
            # Regular board view
            game.display_board()
        
        # Spymaster gives clue
        is_player_spymaster = (mode == 3 and current_team == player_team)
        
        if is_player_spymaster:
            clue, count = player_input_clue(game, current_team)
        else:
            clue, count = spymaster.generate_clue(game)
            print(f"[AI SPYMASTER] gives clue: '{clue}' ({count} words)")
        
        if clue == "PASS":
            print("   Spymaster passes this turn.")
            game.turn = 'BLUE' if game.turn == 'RED' else 'RED'
            continue
        
        # Guesser makes guesses
        guesses_made = 0
        max_guesses = count + 1  # Can guess one more than the number
        turn_ended = False
        turn_already_switched = False
        
        # Check if player is the guesser
        is_player_operative = (mode == 2 and current_team == player_team)
        
        while guesses_made < max_guesses and not game.game_over and not turn_ended:
            if is_player_operative:
                guess = player_input_guess(game, clue, count)
                if guess is None:
                    print(f"   You pass this turn.")
                    turn_ended = True
                    break
                print(f"   You guess: {guess}")
            else:
                guess = guesser.make_guess(game, clue, count)
                if guess is None:
                    print(f"   AI Guesser passes (no confident guess)")
                    turn_ended = True
                    break
                print(f"   AI Guesser guesses: {guess}")
            
            success, card_type = game.reveal_card(guess)
            
            if not success:
                print(f"   ❌ Invalid guess!")
                turn_ended = True
                break
            
            guesses_made += 1
            
            # Show result
            symbols = {'RED': '[RED]', 'BLUE': '[BLUE]', 'NEUTRAL': '[NEUTRAL]', 'ASSASSIN': '[ASSASSIN]'}
            symbol = symbols.get(card_type, '[?]')
            print(f"   {symbol} Revealed: {guess} ({card_type})")
            
            # Check win condition
            winner = game.check_win_condition()
            if winner:
                game.game_over = True
                game.winner = winner
                print(f"\n{'=' * 70}")
                print(f"*** {winner} TEAM WINS! ***")
                print('=' * 70)
                break
            
            # If wrong team or neutral/assassin, turn ends
            if card_type != game.turn:
                if card_type == 'ASSASSIN':
                    # Assassin revealed - other team wins
                    other_team = 'BLUE' if game.turn == 'RED' else 'RED'
                    game.game_over = True
                    game.winner = other_team
                    print(f"\n[X] ASSASSIN REVEALED! {other_team} TEAM WINS!")
                    break
                else:
                    print(f"   Wrong card! Turn ends.")
                    # Switch turn
                    game.turn = 'BLUE' if game.turn == 'RED' else 'RED'
                    turn_ended = True
                    turn_already_switched = True
                    break
            
            # If correct card and we've reached max guesses, turn ends
            if guesses_made >= max_guesses:
                print(f"   Reached maximum guesses ({max_guesses}). Turn ends.")
                turn_ended = True
        
        # Switch turn if turn ended naturally (passed or reached max guesses with correct cards)
        # Don't switch if wrong card was revealed (already switched above) or game is over
        if not game.game_over and turn_ended and not turn_already_switched:
            game.turn = 'BLUE' if game.turn == 'RED' else 'RED'
        
        # Wait for user input if interactive, otherwise auto-continue
        if sys.stdin.isatty():
            try:
                input("\nPress Enter to continue...")
            except (EOFError, KeyboardInterrupt):
                pass
        else:
            time.sleep(0.5)
    
    # Show final board
    print("\n[Final Board]")
    game.display_board(show_all=True)
    
    if game.game_over:
        print(f"\n*** Game Over! Winner: {game.winner} TEAM ***")
    else:
        print("\n*** Game ended (max turns reached) ***")


if __name__ == "__main__":
    play_game()

