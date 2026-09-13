import numpy as np

M = 1e6

def big_m_simplex(A, b, c, constraint_types):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    c = np.array(c, dtype=float)

    rows, cols = A.shape

    tableau = []
    var_names = [f"x{i+1}" for i in range(cols)]
    artificial = []

    for i in range(rows):
        row = list(A[i])

        if constraint_types[i] == "<=":
            row += [0] * rows
            row[cols + i] = 1
            var_names.append(f"s{i+1}")

        elif constraint_types[i] == ">=":
            row += [0] * rows
            row[cols + i] = -1

            art_index = len(row)
            row.append(1)
            artificial.append(art_index)
            var_names.append(f"a{i+1}")

        elif constraint_types[i] == "=":
            row += [0] * rows

            art_index = len(row)
            row.append(1)
            artificial.append(art_index)
            var_names.append(f"a{i+1}")

        tableau.append(row)

    max_cols = max(len(row) for row in tableau)

    for row in tableau:
        while len(row) < max_cols:
            row.append(0)

    tableau = np.array(tableau, dtype=float)

    total_vars = tableau.shape[1]

    objective = np.zeros(total_vars)

    for i in range(cols):
        objective[i] = c[i]

    for index in artificial:
        objective[index] = -M

    tableau = np.column_stack((tableau, b))

    objective_row = np.append(-objective, 0)
    tableau = np.vstack((tableau, objective_row))

    basis = []

    for i in range(rows):
        basic = None

        for j in range(total_vars):
            column = tableau[:rows, j]

            if abs(column[i] - 1) < 1e-9 and \
               np.count_nonzero(abs(column) > 1e-9) == 1:
                basic = j
                break

        basis.append(basic)

    for i in range(rows):
        if basis[i] in artificial:
            tableau[-1] += M * tableau[i]

    while True:
        objective_row = tableau[-1, :-1]

        entering = np.argmin(objective_row)

        if objective_row[entering] >= -1e-9:
            break

        ratios = []

        for i in range(rows):
            if tableau[i, entering] > 1e-9:
                ratios.append(tableau[i, -1] / tableau[i, entering])
            else:
                ratios.append(np.inf)

        leaving = np.argmin(ratios)

        if ratios[leaving] == np.inf:
            raise ValueError("The problem is unbounded.")

        pivot = tableau[leaving, entering]

        tableau[leaving] /= pivot

        for i in range(rows + 1):
            if i != leaving:
                tableau[i] -= tableau[i, entering] * tableau[leaving]

        basis[leaving] = entering

    solution = np.zeros(total_vars)

    for i in range(rows):
        if basis[i] is not None:
            solution[basis[i]] = tableau[i, -1]

    for index in artificial:
        if solution[index] > 1e-6:
            raise ValueError("The problem is infeasible")

    return solution, tableau[-1, -1]


def solve():
    A = [[2, 1],[1, 1],[1, 2]]
    b = [300,80,200]
    c = [40,30]
    constraint_types = ["<=",">=","="]

    solution, objective = big_m_simplex(A,b,c,constraint_types)

    print("Optimal Solution")
    print("-----------------")
    print(f"Product A = {solution[0]:.2f}")
    print(f"Product B = {solution[1]:.2f}")
    print(f"\nMaximum Profit = ₹{objective:.2f}")


solve()