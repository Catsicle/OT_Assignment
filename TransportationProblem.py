
cost = [
    [19, 30, 50, 10],
    [70, 30, 40, 60],
    [40, 8, 70, 20]
]

supply = [7, 9, 18]
demand = [5, 8, 7, 14]

method = "VAM"


def print_table(allocation):
    print("\nAllocation Table:")
    for row in allocation:
        print(row)


def total_cost(allocation):
    total = 0

    for i in range(len(allocation)):
        for j in range(len(allocation[0])):
            total += allocation[i][j] * cost[i][j]

    return total


def northwest_corner():
    m = len(supply)
    n = len(demand)

    allocation = [[0] * n for _ in range(m)]

    s = supply[:]
    d = demand[:]

    i = 0
    j = 0

    while i < m and j < n:
        quantity = min(s[i], d[j])

        allocation[i][j] = quantity

        s[i] -= quantity
        d[j] -= quantity

        if s[i] == 0 and d[j] == 0:
            if i < m - 1 and j < n - 1:
                allocation[i + 1][j] = 0
            i += 1
            j += 1
        elif s[i] == 0:
            i += 1
        else:
            j += 1

    return allocation


def vogel():
    m = len(supply)
    n = len(demand)

    allocation = [[0] * n for _ in range(m)]

    s = supply[:]
    d = demand[:]

    active_rows = [True] * m
    active_cols = [True] * n

    while True:
        row_penalty = [-1] * m
        col_penalty = [-1] * n

        for i in range(m):
            if not active_rows[i]:
                continue

            values = []

            for j in range(n):
                if active_cols[j]:
                    values.append(cost[i][j])

            values.sort()

            if len(values) >= 2:
                row_penalty[i] = values[1] - values[0]
            elif len(values) == 1:
                row_penalty[i] = values[0]

        for j in range(n):
            if not active_cols[j]:
                continue

            values = []

            for i in range(m):
                if active_rows[i]:
                    values.append(cost[i][j])

            values.sort()

            if len(values) >= 2:
                col_penalty[j] = values[1] - values[0]
            elif len(values) == 1:
                col_penalty[j] = values[0]

        maximum = max(max(row_penalty), max(col_penalty))

        row_choices = []
        col_choices = []

        for i in range(m):
            if active_rows[i] and row_penalty[i] == maximum:
                minimum_cost = min(
                    cost[i][j] for j in range(n) if active_cols[j]
                )
                row_choices.append((minimum_cost, i))

        for j in range(n):
            if active_cols[j] and col_penalty[j] == maximum:
                minimum_cost = min(
                    cost[i][j] for i in range(m) if active_rows[i]
                )
                col_choices.append((minimum_cost, j))

        choose_row = False

        if row_choices and not col_choices:
            choose_row = True
        elif row_choices and col_choices:
            best_row = min(row_choices)
            best_col = min(col_choices)

            if best_row[0] <= best_col[0]:
                choose_row = True

        if choose_row:
            _, i = min(row_choices)

            j = min(
                (cost[i][j], j)
                for j in range(n)
                if active_cols[j]
            )[1]

        else:
            _, j = min(col_choices)

            i = min(
                (cost[i][j], i)
                for i in range(m)
                if active_rows[i]
            )[1]

        quantity = min(s[i], d[j])

        allocation[i][j] = quantity

        s[i] -= quantity
        d[j] -= quantity

        if s[i] == 0:
            active_rows[i] = False

        if d[j] == 0:
            active_cols[j] = False

        if sum(s) == 0:
            break

    return allocation


def get_basis(allocation):
    basis = set()

    for i in range(len(allocation)):
        for j in range(len(allocation[0])):
            if allocation[i][j] > 0:
                basis.add((i, j))

    return basis


def get_potentials(basis):
    m = len(cost)
    n = len(cost[0])

    u = [None] * m
    v = [None] * n

    u[0] = 0

    changed = True

    while changed:
        changed = False

        for i, j in basis:
            if u[i] is not None and v[j] is None:
                v[j] = cost[i][j] - u[i]
                changed = True

            elif v[j] is not None and u[i] is None:
                u[i] = cost[i][j] - v[j]
                changed = True

    return u, v


def find_path(basis, start, end):
    graph = {}

    for i, j in basis:
        row_node = ("r", i)
        col_node = ("c", j)

        if row_node not in graph:
            graph[row_node] = []

        if col_node not in graph:
            graph[col_node] = []

        graph[row_node].append(col_node)
        graph[col_node].append(row_node)

    start_node = ("c", start[1])
    end_node = ("r", end[0])

    stack = [(start_node, [start_node])]
    visited = {start_node}

    while stack:
        node, path = stack.pop()

        if node == end_node:
            cells = []

            for k in range(len(path) - 1):
                a = path[k]
                b = path[k + 1]

                if a[0] == "r":
                    cells.append((a[1], b[1]))
                else:
                    cells.append((b[1], a[1]))

            return cells

        for nxt in graph.get(node, []):
            if nxt not in visited:
                visited.add(nxt)
                stack.append((nxt, path + [nxt]))

    return []


def modi(allocation):
    basis = get_basis(allocation)

    m = len(cost)
    n = len(cost[0])

    while True:
        u, v = get_potentials(basis)

        opportunity = [[0] * n for _ in range(m)]
        most_negative = 0
        entering = None

        for i in range(m):
            for j in range(n):
                if (i, j) not in basis:
                    opportunity[i][j] = cost[i][j] - u[i] - v[j]

                    if opportunity[i][j] < most_negative:
                        most_negative = opportunity[i][j]
                        entering = (i, j)

        if entering is None:
            break

        path = find_path(basis, entering, entering)

        if not path:
            break

        cycle = [entering] + path

        plus_cells = []
        minus_cells = []

        for k, cell in enumerate(cycle):
            if k % 2 == 0:
                plus_cells.append(cell)
            else:
                minus_cells.append(cell)

        theta = min(allocation[i][j] for i, j in minus_cells)

        for i, j in plus_cells:
            allocation[i][j] += theta

        for i, j in minus_cells:
            allocation[i][j] -= theta

        basis.add(entering)

        leaving_candidates = []

        for i, j in minus_cells:
            if allocation[i][j] == 0:
                leaving_candidates.append((i, j))

        leaving = leaving_candidates[0]
        basis.remove(leaving)

    return allocation


print("Transportation Problem")

print("\nCost Matrix:")
for row in cost:
    print(row)

print("\nSupply:", supply)
print("Demand:", demand)

if sum(supply) != sum(demand):
    print("\nThe problem is unbalanced.")
else:
    if method == "VAM":
        print("\nInitial Basic Feasible Solution using VAM")
        allocation = vogel()

    elif method == "MODI":
        print("\nInitial Basic Feasible Solution using Northwest Corner")
        allocation = northwest_corner()

    else:
        print("\nInvalid method.")
        allocation = None

    if allocation is not None:
        print_table(allocation)

        print("\nInitial transportation cost:", total_cost(allocation))

        allocation = modi(allocation)

        print("\nOptimal Allocation:")
        print_table(allocation)

        print("\nMinimum Transportation Cost:", total_cost(allocation))

