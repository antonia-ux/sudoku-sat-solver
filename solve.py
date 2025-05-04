import argparse
import time
import copy

def parse_puzzle(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    puzzle = []
    for line in lines:
        row = []
        for ch in line.strip():
            if ch in '123456789':
                row.append(int(ch))
            else:
                row.append(0)
        puzzle.append(row)
    return puzzle

def varnum(i, j, d):
    return 81 * (i - 1) + 9 * (j - 1) + d

def sudoku_to_cnf(puzzle):
    cnf = []

    # Each cell must contain at least one number
    for i in range(1, 10):
        for j in range(1, 10):
            cnf.append([varnum(i, j, d) for d in range(1, 10)])

    # Each cell must contain at most one number
    for i in range(1, 10):
        for j in range(1, 10):
            for d in range(1, 10):
                for dp in range(d + 1, 10):
                    cnf.append([-varnum(i, j, d), -varnum(i, j, dp)])

    # Each number must appear once in each row
    for i in range(1, 10):
        for d in range(1, 10):
            cnf.append([varnum(i, j, d) for j in range(1, 10)])
            for j in range(1, 10):
                for jp in range(j + 1, 10):
                    cnf.append([-varnum(i, j, d), -varnum(i, jp, d)])

    # Each number must appear once in each column
    for j in range(1, 10):
        for d in range(1, 10):
            cnf.append([varnum(i, j, d) for i in range(1, 10)])
            for i in range(1, 10):
                for ip in range(i + 1, 10):
                    cnf.append([-varnum(i, j, d), -varnum(ip, j, d)])

    # Each number must appear once in each 3x3 subgrid
    for block_i in range(0, 3):
        for block_j in range(0, 3):
            for d in range(1, 10):
                block = []
                for i in range(1, 4):
                    for j in range(1, 4):
                        block.append(varnum(3 * block_i + i, 3 * block_j + j, d))
                cnf.append(block)
                for m in range(len(block)):
                    for n in range(m + 1, len(block)):
                        cnf.append([-block[m], -block[n]])

    # Add clues
    for i in range(9):
        for j in range(9):
            d = puzzle[i][j]
            if d != 0:
                cnf.append([varnum(i + 1, j + 1, d)])

    return cnf

# ========== SAT Solvers ==========

def unit_propagate(clauses, assignment):
    changed = True
    while changed:
        changed = False
        unit_clauses = [c for c in clauses if len(c) == 1]
        for unit in unit_clauses:
            lit = unit[0]
            if -lit in assignment:
                return None
            if lit not in assignment:
                assignment.append(lit)
                clauses = simplify(clauses, lit)
                changed = True
    return clauses, assignment

def simplify(clauses, lit):
    new_clauses = []
    for clause in clauses:
        if lit in clause:
            continue
        if -lit in clause:
            new_clause = [l for l in clause if l != -lit]
            if not new_clause:
                return None
            new_clauses.append(new_clause)
        else:
            new_clauses.append(clause)
    return new_clauses

def dpll(clauses, assignment=[]):
    res = unit_propagate(copy.deepcopy(clauses), assignment[:])
    if res is None:
        return None
    clauses, assignment = res
    if not clauses:
        return assignment
    for clause in clauses:
        for lit in clause:
            new_assignment = assignment[:]
            new_assignment.append(lit)
            result = dpll(simplify(clauses, lit), new_assignment)
            if result is not None:
                return result
    return None

def dp(clauses):
    symbols = set(abs(lit) for clause in clauses for lit in clause)
    return dp_helper(clauses, list(symbols))

def dp_helper(clauses, symbols):
    if not clauses:
        return True
    if [] in clauses:
        return False
    if not symbols:
        return False
    p = symbols[0]
    symbols = symbols[1:]
    pos = simplify(copy.deepcopy(clauses), p)
    if pos is not None and dp_helper(pos, symbols):
        return True
    neg = simplify(copy.deepcopy(clauses), -p)
    if neg is not None and dp_helper(neg, symbols):
        return True
    return False

def resolution(clauses):
    new = set()
    clauses = [frozenset(c) for c in clauses]
    while True:
        n = len(clauses)
        for i in range(n):
            for j in range(i + 1, n):
                ci = clauses[i]
                cj = clauses[j]
                for lit in ci:
                    if -lit in cj:
                        resolvent = ci.union(cj) - {lit, -lit}
                        if not resolvent:
                            return False
                        new.add(frozenset(resolvent))
        if new.issubset(set(clauses)):
            return True
        clauses.extend(new)

# ========== Utilities ==========

def time_solver(method_name, clauses, puzzle):
    print(f"\n[*] Running {method_name}...")

    start = time.time()

    if method_name == "DPLL":
        model = dpll(clauses)
        end = time.time()
        print("[+] DPLL:", "SAT" if model else "UNSAT")
    elif method_name == "DP":
        model = dp(clauses)
        end = time.time()
        print("[+] DP:", "SAT" if model else "UNSAT")
    elif method_name == "Resolution":
        result = resolution(clauses)
        end = time.time()
        print("[+] Resolution:", "SAT" if result else "UNSAT")

    print(f"[!] {method_name} time taken: {end - start:.4f} seconds")

# ========== Main ==========

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sudoku SAT Solver")
    parser.add_argument('--input', type=str, required=True)
    parser.add_argument('--method', type=str, choices=["DPLL", "DP", "Resolution"], help="Choose solving method")
    parser.add_argument('--compare', action='store_true', help="Compare all solvers")
    args = parser.parse_args()

    puzzle = parse_puzzle(args.input)
    clauses = sudoku_to_cnf(puzzle)

    if args.compare:
        for method in ["DPLL", "DP", "Resolution"]:
            time_solver(method, clauses, puzzle)
    elif args.method:
        time_solver(args.method, clauses, puzzle)
    else:
        print("Please specify --method or --compare")
