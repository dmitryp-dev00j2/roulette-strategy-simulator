import random

# european roulette layout
REDS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACKS = set(range(1, 37)) - REDS - {0}

def spin_wheel():
    return random.randint(0, 36)

def _bet_red():
    return lambda n: n in REDS

def _payout(bet, win):
    # even-money bet on red/black
    if win:
        return bet  # profit equal to bet, total returned = bet + profit
    return -bet

def _clamp_bet(bet, table_limit):
    if table_limit is None:
        return bet
    return min(bet, table_limit)

def martingale_session(bankroll, target, base_bet, max_spins, verbose=False, history=None, table_limit=None):
    current_bet = base_bet
    spins = 0
    log = []
    bet_on_red = _bet_red()
    hist_idx = 0

    while bankroll < target and spins < max_spins:
        if current_bet > bankroll:
            break
        current_bet = _clamp_bet(current_bet, table_limit)
        if current_bet > bankroll:
            break

        if history is not None and hist_idx < len(history):
            number = history[hist_idx]
            hist_idx += 1
        else:
            number = spin_wheel()

        win = bet_on_red(number)
        profit = _payout(current_bet, win)
        bankroll += profit
        spins += 1

        if verbose:
            log.append({
                "spin": spins,
                "number": number,
                "bet": current_bet,
                "win": win,
                "bankroll": bankroll,
            })

        if win:
            current_bet = base_bet
        else:
            current_bet *= 2

    return {
        "spins": spins,
        "final_bankroll": bankroll,
        "busted": bankroll < target and spins >= max_spins,
        "log": log,
    }

def fibonacci_session(bankroll, target, base_bet, max_spins, verbose=False, history=None, table_limit=None):
    fib = [base_bet, base_bet]
    idx = 0
    spins = 0
    log = []
    bet_on_red = _bet_red()
    hist_idx = 0

    while bankroll < target and spins < max_spins:
        if idx >= len(fib):
            fib.append(fib[-1] + fib[-2])
        current_bet = fib[idx]
        current_bet = _clamp_bet(current_bet, table_limit)
        if current_bet > bankroll:
            break

        if history is not None and hist_idx < len(history):
            number = history[hist_idx]
            hist_idx += 1
        else:
            number = spin_wheel()

        win = bet_on_red(number)
        profit = _payout(current_bet, win)
        bankroll += profit
        spins += 1

        if verbose:
            log.append({
                "spin": spins,
                "number": number,
                "bet": current_bet,
                "win": win,
                "bankroll": bankroll,
            })

        if win:
            idx = max(0, idx - 2)
        else:
            idx += 1

    return {
        "spins": spins,
        "final_bankroll": bankroll,
        "busted": bankroll < target and spins >= max_spins,
        "log": log,
    }

def flat_session(bankroll, target, base_bet, max_spins, verbose=False, history=None, table_limit=None):
    spins = 0
    log = []
    bet_on_red = _bet_red()
    hist_idx = 0

    while bankroll < target and spins < max_spins:
        current_bet = _clamp_bet(base_bet, table_limit)
        if current_bet > bankroll:
            break

        if history is not None and hist_idx < len(history):
            number = history[hist_idx]
            hist_idx += 1
        else:
            number = spin_wheel()

        win = bet_on_red(number)
        profit = _payout(current_bet, win)
        bankroll += profit
        spins += 1

        if verbose:
            log.append({
                "spin": spins,
                "number": number,
                "bet": current_bet,
                "win": win,
                "bankroll": bankroll,
            })

    return {
        "spins": spins,
        "final_bankroll": bankroll,
        "busted": bankroll < target and spins >= max_spins,
        "log": log,
    }
