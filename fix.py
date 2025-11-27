"""
fixed_interest_calculator.py
A single-file Python CLI utility for calculating fixed interest values.

Features:
- Simple Interest calculation
- Compound Interest calculation (compoundings per year)
- Loan monthly payment calculation (fixed-rate amortizing loan)
- Amortization schedule export to CSV
- Interactive menu when run with no arguments; argparse for scripted use

Usage examples:
  python fixed_interest_calculator.py --mode simple --principal 10000 --rate 5 --time 3
  python fixed_interest_calculator.py --mode compound --principal 10000 --rate 5 --time 3 --n 4
  python fixed_interest_calculator.py --mode loan --principal 250000 --rate 3.5 --years 30
  python fixed_interest_calculator.py --mode amortization --principal 250000 --rate 3.5 --years 30 --out schedule.csv

Author: ChatGPT
"""

import argparse
import math
import csv
import sys
from typing import List, Dict


def simple_interest(principal: float, rate_percent: float, time_years: float) -> Dict[str, float]:
    """Calculate simple interest.

    Args:
        principal: initial amount
        rate_percent: annual rate in percent (e.g., 5 for 5%)
        time_years: time in years

    Returns:
        dict with interest and total amount
    """
    rate = rate_percent / 100.0
    interest = principal * rate * time_years
    total = principal + interest
    return {"principal": principal, "interest": interest, "total": total}


def compound_interest(principal: float, rate_percent: float, time_years: float, n: int = 1) -> Dict[str, float]:
    """Calculate compound interest.

    Args:
        principal: initial amount
        rate_percent: annual rate in percent
        time_years: time in years
        n: number of compounding periods per year (1=annual, 12=monthly, 365=daily)

    Returns:
        dict with amount and interest earned
    """
    rate = rate_percent / 100.0
    amount = principal * ((1 + rate / n) ** (n * time_years))
    interest = amount - principal
    return {"principal": principal, "amount": amount, "interest": interest}


def monthly_payment(principal: float, annual_rate_percent: float, years: float) -> float:
    """Compute monthly payment for a fixed-rate amortizing loan.

    Formula: M = P * r / (1 - (1 + r)^-N)
      where r = monthly rate (decimal), N = total months
    """
    monthly_rate = annual_rate_percent / 100.0 / 12.0
    n_payments = int(round(years * 12))
    if monthly_rate == 0:
        return principal / n_payments
    m = principal * monthly_rate / (1 - (1 + monthly_rate) ** (-n_payments))
    return m


def amortization_schedule(principal: float, annual_rate_percent: float, years: float) -> List[Dict[str, float]]:
    """Return amortization schedule as a list of monthly payment dicts.

    Each entry contains: month, payment, principal_paid, interest_paid, remaining_balance
    """
    schedule = []
    monthly_rate = annual_rate_percent / 100.0 / 12.0
    n_payments = int(round(years * 12))
    payment = monthly_payment(principal, annual_rate_percent, years)
    balance = principal

    for month in range(1, n_payments + 1):
        interest = balance * monthly_rate
        principal_paid = payment - interest
        # protect against negative principal in final payment due to rounding
        if principal_paid > balance:
            principal_paid = balance
            payment = interest + principal_paid
        balance -= principal_paid
        schedule.append({
            "month": month,
            "payment": round(payment, 2),
            "principal_paid": round(principal_paid, 2),
            "interest_paid": round(interest, 2),
            "remaining_balance": round(max(balance, 0.0), 2)
        })
    return schedule


def export_schedule_to_csv(schedule: List[Dict[str, float]], filename: str) -> None:
    fieldnames = ["month", "payment", "principal_paid", "interest_paid", "remaining_balance"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in schedule:
            writer.writerow(row)


def format_currency(x: float) -> str:
    return f"{x:,.2f}"


def interactive_menu():
    print("Fixed Interest Calculator - Interactive Mode")
    print("Choose an option:")
    print(" 1) Simple Interest")
    print(" 2) Compound Interest")
    print(" 3) Loan monthly payment")
    print(" 4) Amortization schedule (exportable)")
    print(" 0) Exit")

    choice = input("Enter choice: ")
    try:
        choice = int(choice)
    except ValueError:
        print("Invalid choice")
        return

    if choice == 1:
        p = float(input("Principal: "))
        r = float(input("Annual rate (%, e.g. 5): "))
        t = float(input("Time (years): "))
        res = simple_interest(p, r, t)
        print(f"Interest: {format_currency(res['interest'])}")
        print(f"Total amount: {format_currency(res['total'])}")

    elif choice == 2:
        p = float(input("Principal: "))
        r = float(input("Annual rate (%, e.g. 5): "))
        t = float(input("Time (years): "))
        n = int(input("Compounding per year (1=annual,12=monthly): "))
        res = compound_interest(p, r, t, n)
        print(f"Amount: {format_currency(res['amount'])}")
        print(f"Interest earned: {format_currency(res['interest'])}")

    elif choice == 3:
        p = float(input("Loan principal: "))
        r = float(input("Annual rate (%, e.g. 3.5): "))
        y = float(input("Years: "))
        m = monthly_payment(p, r, y)
        print(f"Monthly payment: {format_currency(m)}")
        print(f"Total paid over {y} years: {format_currency(m * y * 12)}")

    elif choice == 4:
        p = float(input("Loan principal: "))
        r = float(input("Annual rate (%, e.g. 3.5): "))
        y = float(input("Years: "))
        out = input("CSV filename to export (e.g. schedule.csv): ")
        sched = amortization_schedule(p, r, y)
        export_schedule_to_csv(sched, out)
        print(f"Schedule exported to {out} (rows: {len(sched)})")

    elif choice == 0:
        print("Goodbye")
        sys.exit(0)

    else:
        print("Invalid choice")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Fixed Interest Calculator CLI")
    p.add_argument("--mode", choices=["simple", "compound", "loan", "amortization"],
                   help="Calculation mode")
    p.add_argument("--principal", type=float, help="Principal amount")
    p.add_argument("--rate", type=float, help="Annual interest rate (percent)")
    p.add_argument("--time", type=float, help="Time in years (for simple/compound)")
    p.add_argument("--n", type=int, default=1, help="Compounds per year for compound mode (default 1)")
    p.add_argument("--years", type=float, help="Years for loan/amortization modes")
    p.add_argument("--out", type=str, help="CSV output filename for amortization schedule")
    return p


def main(argv=None):
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    # If no args provided, enter interactive menu
    if len(sys.argv) == 1:
        try:
            while True:
                interactive_menu()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting")
            sys.exit(0)

    mode = args.mode
    if mode == "simple":
        if args.principal is None or args.rate is None or args.time is None:
            parser.error("--principal, --rate and --time are required for simple mode")
        res = simple_interest(args.principal, args.rate, args.time)
        print("Simple Interest Result")
        print(f"Principal: {format_currency(res['principal'])}")
        print(f"Interest: {format_currency(res['interest'])}")
        print(f"Total: {format_currency(res['total'])}")

    elif mode == "compound":
        if args.principal is None or args.rate is None or args.time is None:
            parser.error("--principal, --rate and --time are required for compound mode")
        res = compound_interest(args.principal, args.rate, args.time, args.n)
        print("Compound Interest Result")
        print(f"Principal: {format_currency(res['principal'])}")
        print(f"Amount: {format_currency(res['amount'])}")
        print(f"Interest earned: {format_currency(res['interest'])}")

    elif mode == "loan":
        if args.principal is None or args.rate is None or args.years is None:
            parser.error("--principal, --rate and --years are required for loan mode")
        m = monthly_payment(args.principal, args.rate, args.years)
        total = m * args.years * 12
        print("Loan Payment Result")
        print(f"Principal: {format_currency(args.principal)}")
        print(f"Monthly payment: {format_currency(m)}")
        print(f"Total paid: {format_currency(total)}")
        print(f"Total interest paid: {format_currency(total - args.principal)}")

    elif mode == "amortization":
        if args.principal is None or args.rate is None or args.years is None:
            parser.error("--principal, --rate and --years are required for amortization mode")
        sched = amortization_schedule(args.principal, args.rate, args.years)
        if args.out:
            export_schedule_to_csv(sched, args.out)
            print(f"Exported amortization schedule to {args.out}")
        else:
            print("Amortization schedule (first 12 rows):")
            for row in sched[:12]:
                print(row)
            print(f"... total months: {len(sched)}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
