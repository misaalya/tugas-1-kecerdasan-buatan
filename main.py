SIZE = 4

world = [[set() for _ in range(SIZE)] for _ in range(SIZE)]
percepts = [[set() for _ in range(SIZE)] for _ in range(SIZE)]

# world objects
START = (3, 0)
WUMPUS = (1, 0)
PITS = [
    (0, 3),
    (1, 2),
    (3, 2),
]
GOLD = (1, 1)

#assign object ke world
world[WUMPUS[0]][WUMPUS[1]].add("WUMPUS")
for row, col in PITS:
    world[row][col].add("PIT")
world[GOLD[0]][GOLD[1]].add("GOLD")

def get_neighbors(position):
    row, col = position

    directions = [
        (-1, 0), # atas
        (0, 1), # kanan
        (1, 0), # bawah
        (0, -1), # kiri
    ]

    neighbors = []

    for dr, dc in directions:
        new_row = row + dr
        new_col = col + dc

        # hanya append jika kordinat masih didalam rentang kolom / baris di world
        if (new_row >= 0 and new_row < SIZE) and (new_col >= 0 and new_col < SIZE ):
            neighbors.append((new_row, new_col))

    return neighbors


# assign semua percepts ke list percepts 

for row, col in get_neighbors(WUMPUS):
    percepts[row][col].add("STENCH")

for pit in PITS:
    for row, col in get_neighbors(pit):
        percepts[row][col].add("BREEZE")

percepts[GOLD[0]][GOLD[1]].add("GLITTER")




#DEBUG
# def print_world():
#     for row in world:
#         print(row)
#     for row in percepts:
#         print(row)


# print_world()