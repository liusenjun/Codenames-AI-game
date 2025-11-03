import importlib, traceback, sys

try:
    game_mod = importlib.import_module('codenames')
    Game = getattr(game_mod, 'CodenamesGame', None)
    Spymaster = getattr(game_mod, 'AISpymaster', None)
    Guesser = getattr(game_mod, 'AIGuesser', None)
    if Game is None or Spymaster is None or Guesser is None:
        print('MISSING: CodenamesGame/AISpymaster/AIGuesser not found in codenames.py')
        sys.exit(2)

    g = Game()
    g.setup_board()
    team = g.turn
    print('Team to act:', team)
    sp = Spymaster(team)
    clue, count = sp.generate_clue(g)
    print(f'Clue from AISpymaster: {clue} / {count}')
    gu = Guesser(team)
    guess = gu.make_guess(g, clue, count)
    print('AIGuesser selected:', guess)
    print('Smoke test: OK')
except Exception:
    traceback.print_exc()
    sys.exit(1)
