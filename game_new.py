import pygame

pygame.init()

# 1. Setup Grid & Window
SIZE = 4
WINDOW_SIZE = 600
CELL_SIZE = WINDOW_SIZE // SIZE  # 150 px

screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Wumpus World Simulation")

font_emoji = pygame.font.SysFont("notocoloremoji", 28)
font_text = pygame.font.SysFont("arial", 20, bold=True)

# 2. Objek Dunia (Sesuai Peta Soal & Slide Dosen)
WUMPUS = (1, 0)
PITS = [
    (0, 3),
    (1, 2),
    (3, 2),
]
GOLD = (1, 1)

# 3. State Agen
agent_state = {
    "position": [3, 0],     # Start di kiri bawah (1,1 dalam koordinat kartesius)
    "visited": set(),
    "not_pit": set(),
    "not_wumpus": set(),
    "possibly_wumpus": {},
    "path_history": [],
    "has_gold": False,
    "has_arrow": True,
    "wumpus_alive": True,
    "wumpus_pos_deduced": None,
    "finish": False,
    "game_over": False,
}

# Timer pergerakan agen (tiap 500ms / 0.5 detik)
MOVE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(MOVE_EVENT, 500)


def get_neighbors(position):
    row, col = position
    directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]
    neighbors = []

    for dr, dc in directions:
        new_row = row + dr
        new_col = col + dc
        if (0 <= new_row < SIZE) and (0 <= new_col < SIZE):
            neighbors.append((new_row, new_col))

    return neighbors


def step_agent(state):
    # Hentikan simulasi jika sudah tamat (kalah / menang)
    if state["game_over"] or state["finish"]:
        return

    curr_pos = tuple(state["position"])

    # Edge Case: Menabrak Wumpus hidup -> KALAH
    if state["wumpus_alive"] and curr_pos == WUMPUS:
        state["game_over"] = True
        return

    # 1. Tandai posisi saat ini sebagai aman
    state["visited"].add(curr_pos)
    state["not_pit"].add(curr_pos)
    state["not_wumpus"].add(curr_pos)

    # 2. Cek Emas
    if curr_pos == GOLD:
        state["has_gold"] = True

    # 3. Mode Pulang (Jika sudah dapat emas)
    if state["has_gold"]:
        if curr_pos == (3, 0):
            state["finish"] = True  # Berhasil pulang ke start (MENANG)
            return
        if state["path_history"]:
            prev_pos = state["path_history"].pop()
            state["position"][0], state["position"][1] = prev_pos
        return

    # 4. Scan Persepsi Tetangga
    neighbors = get_neighbors(curr_pos)

    # Cek Stench
    curr_block_has_stench = state["wumpus_alive"] and (curr_pos in get_neighbors(WUMPUS))
    if not curr_block_has_stench and state["wumpus_alive"]:
        for n in neighbors:
            state["not_wumpus"].add(n)
    elif curr_block_has_stench and state["wumpus_alive"]:
        for n in neighbors:
            if n not in state["not_wumpus"] and n not in state["visited"]:
                state["possibly_wumpus"][n] = state["possibly_wumpus"].get(n, 0) + 1

    # Cek Breeze
    curr_block_has_breeze = False
    for pit in PITS:
        if curr_pos in get_neighbors(pit):
            curr_block_has_breeze = True
            break

    if not curr_block_has_breeze:
        for n in neighbors:
            state["not_pit"].add(n)

    # 5. Logika Deduksi Wumpus & Menembak Panah
    if state["wumpus_alive"]:
        # A. Deduksi pasti (tersisa 1 kandidat)
        if curr_block_has_stench and state["wumpus_pos_deduced"] is None:
            candidates = [n for n in neighbors if n not in state["not_wumpus"]]
            if len(candidates) == 1:
                state["wumpus_pos_deduced"] = candidates[0]

        # B. Deduksi Greedy (Tercium >= 2 kali)
        if state["wumpus_pos_deduced"] is None:
            for target_pos, count in state["possibly_wumpus"].items():
                if count >= 2:
                    state["wumpus_pos_deduced"] = target_pos
                    break

        # Tembak jika posisi Wumpus diketahui dan bersebelahan langsung
        if state["wumpus_pos_deduced"] and state["has_arrow"]:
            if state["wumpus_pos_deduced"] in neighbors:
                state["has_arrow"] = False
                state["wumpus_alive"] = False
                state["not_wumpus"].add(state["wumpus_pos_deduced"])

    # 6. Filtering & Penentuan Langkah (DFS Backtracking)
    safe_tiles = state["not_pit"].intersection(state["not_wumpus"])
    unvisited_safe = [n for n in neighbors if n in safe_tiles and n not in state["visited"]]

    if unvisited_safe:
        next_pos = unvisited_safe[0]
        state["path_history"].append(curr_pos)
        state["position"][0], state["position"][1] = next_pos
    else:
        # Mundur jika buntu
        if state["path_history"]:
            prev_pos = state["path_history"].pop()
            state["position"][0], state["position"][1] = prev_pos
        else:
            state["game_over"] = False


# --- GAME LOOP UTAMA ---
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == MOVE_EVENT:
            step_agent(agent_state)

    screen.fill("white")

    # A. Gambar Garis Grid 4x4
    for row in range(SIZE):
        for col in range(SIZE):
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            pygame.draw.rect(screen, "black", (x, y, CELL_SIZE, CELL_SIZE), 2)

    # B. Gambar Stench (hanya jika Wumpus masih hidup)
    if agent_state["wumpus_alive"]:
        for wp_row, wp_col in get_neighbors(WUMPUS):
            x = wp_col * CELL_SIZE
            y = wp_row * CELL_SIZE
            text = font_text.render("<<", True, "green")
            screen.blit(text, text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2)))

    # C. Gambar Breeze
    for pit in PITS:
        for pit_row, pit_col in get_neighbors(pit):
            x = pit_col * CELL_SIZE
            y = pit_row * CELL_SIZE
            text = font_text.render("~~", True, "blue")
            screen.blit(text, text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 3)))

    # D. Gambar Gold (hanya jika belum diambil)
    if not agent_state["has_gold"]:
        x = GOLD[1] * CELL_SIZE
        y = GOLD[0] * CELL_SIZE
        text_gold = font_emoji.render("💰", True, "black")
        screen.blit(text_gold, text_gold.get_rect(center=(x + CELL_SIZE // 2, y + ((CELL_SIZE // 2) + 25))))

    # E. Gambar Pits
    for pit in PITS:
        x = pit[1] * CELL_SIZE
        y = pit[0] * CELL_SIZE
        text = font_emoji.render("⚫", True, "black")
        screen.blit(text, text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2)))

    # F. Gambar Wumpus (💀 jika hidup, 😱 jika sudah dipanah)
    x = WUMPUS[1] * CELL_SIZE
    y = WUMPUS[0] * CELL_SIZE
    wumpus_icon = "💀" if agent_state["wumpus_alive"] else "😱"
    text = font_emoji.render(wumpus_icon, True, "black")
    screen.blit(text, text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2)))

    # G. Gambar Agent (💀 kalah, 🏆 menang, 🎒 bawa emas, 🧍 biasa)
    agent_row, agent_col = agent_state["position"]
    x = agent_col * CELL_SIZE
    y = agent_row * CELL_SIZE

    if agent_state["game_over"]:
        agent_icon = "💀"
    elif agent_state["finish"]:
        agent_icon = "🏆"
    elif agent_state["has_gold"]:
        agent_icon = "🎒"
    else:
        agent_icon = "🧍"

    text = font_emoji.render(agent_icon, True, "black")
    screen.blit(text, text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2)))

    pygame.display.flip()

pygame.quit()