import pygame

pygame.init()

# setup grid & window
SIZE = 4
WINDOW_SIZE = 600
CELL_SIZE = WINDOW_SIZE // SIZE  # 150

screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Agent Grid")

font_emoji = pygame.font.SysFont("notocoloremoji", 18)
font_text = pygame.font.SysFont("arial", 18)
font_label = pygame.font.SysFont("arial", 22, bold=True)

# world objects (row, col), row 0 di atas
WUMPUS = (1, 0)
PITS = [
    (0, 3),
    (1, 2),
    (3, 2),
]
GOLD = (1, 1)

agent_state = {
    "position": [3, 0],
    "step": 1,
    "visited": set(),
    "percepts": {},            # {(r, c): {"stench": bool, "breeze": bool}}  -> fakta di KB
    "not_pit": set(),          # hasil deduksi: kotak pasti bukan pit
    "not_wumpus": set(),       # hasil deduksi: kotak pasti bukan wumpus
    "confirmed_pit": set(),    # hasil deduksi: kotak pasti pit
    "confirmed_wumpus": set(), # hasil deduksi: kotak pasti wumpus
    "path_history": [],        # stack untuk backtrack & jalan pulang
    "has_gold": False,
    "has_arrow": True,
    "wumpus_alive": True,
    "finish": False,
    "game_over": False,
}

# Timer untuk pergerakan otomatis agent (tiap 500ms)
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


def infer(state):
    changed = True
    while changed:
        changed = False

        for pos, p in state["percepts"].items():
            nbrs = get_neighbors(pos)

            # --- aturan arah ¬percept -> tetangga aman ---
            if not p["stench"]:
                for n in nbrs:
                    if n not in state["not_wumpus"]:
                        state["not_wumpus"].add(n)
                        changed = True

            if not p["breeze"]:
                for n in nbrs:
                    if n not in state["not_pit"]:
                        state["not_pit"].add(n)
                        changed = True

            # --- aturan arah percept -> salah satu tetangga berbahaya ---
            if p["stench"] and state["wumpus_alive"]:
                cand = [n for n in nbrs if n not in state["not_wumpus"]]
                if len(cand) == 1 and cand[0] not in state["confirmed_wumpus"]:
                    state["confirmed_wumpus"].add(cand[0])
                    print(f"[INFERENSI] Wumpus terkonfirmasi di {cand[0]} (dari stench di {pos})")
                    changed = True

            if p["breeze"]:
                cand = [n for n in nbrs if n not in state["not_pit"]]
                if len(cand) == 1 and cand[0] not in state["confirmed_pit"]:
                    state["confirmed_pit"].add(cand[0])
                    print(f"[INFERENSI] Pit terkonfirmasi di {cand[0]} (dari breeze di {pos})")
                    changed = True


def step_agent(state):
    # Hentikan jika sudah tamat (kalah ataupun menang)
    if state["game_over"] or state["finish"]:
        return

    curr_pos = tuple(state["position"])

    # Mati jika masuk kotak Wumpus yang masih hidup atau kotak Pit
    if state["wumpus_alive"] and curr_pos == WUMPUS:
        print(f"[MATI] Agen dimakan Wumpus di {curr_pos}")
        state["game_over"] = True
        return
    if curr_pos in PITS:
        print(f"[MATI] Agen jatuh ke pit di {curr_pos}")
        state["game_over"] = True
        return

    # 1. Tandai posisi saat ini sebagai pasti aman (agen hidup di sini)
    state["visited"].add(curr_pos)
    state["not_pit"].add(curr_pos)
    state["not_wumpus"].add(curr_pos)

    # 2. Cek Emas
    if curr_pos == GOLD:
        state["has_gold"] = True

    # 3. Mode Pulang (Jika sudah dapat emas)
    if state["has_gold"]:
        if curr_pos == (3, 0):
            state["finish"] = True  # Berhasil pulang membawa emas (SUCCESS)
            return
        if state["path_history"]:
            prev_pos = state["path_history"].pop()
            state["position"][0], state["position"][1] = prev_pos
        return
    else:
        print(f"langkah ke-{state['step']}")
        state["step"] += 1

    # 4. Terima percept dari lingkungan (sensor)
    curr_block_has_stench = state["wumpus_alive"] and (curr_pos in get_neighbors(WUMPUS))
    curr_block_has_breeze = any(curr_pos in get_neighbors(pit) for pit in PITS)

    # 5. Simpan percept sebagai fakta KB, lalu jalankan inferensi atas seluruh KB
    state["percepts"][curr_pos] = {
        "stench": curr_block_has_stench,
        "breeze": curr_block_has_breeze,
    }
    infer(state)

    # 5b. Panah: tembak jika salah satu tetangga adalah confirmed wumpus
    if state["has_arrow"] and state["wumpus_alive"]:
        for n in get_neighbors(curr_pos):
            if n in state["confirmed_wumpus"]:
                state["has_arrow"] = False
                state["wumpus_alive"] = False
                state["confirmed_wumpus"].discard(n)
                state["not_wumpus"].add(n)
                print(f"[PANAH] Menembak Wumpus di {n} dari {curr_pos}. Wumpus mati.")
                break

    # 6. Hitung Safe Tiles & Tentukan Pergerakan
    safe_tiles = state["not_pit"].intersection(state["not_wumpus"])
    safe_tiles -= state["confirmed_pit"]
    safe_tiles -= state["confirmed_wumpus"]
    neighbors = get_neighbors(curr_pos)
    unvisited_safe = [n for n in neighbors if n in safe_tiles and n not in state["visited"]]

    if unvisited_safe:
        next_pos = unvisited_safe[0]
        state["path_history"].append(curr_pos)
        state["position"][0], state["position"][1] = next_pos
    else:
        # Backtrack jika buntu
        if state["path_history"]:
            prev_pos = state["path_history"].pop()
            state["position"][0], state["position"][1] = prev_pos
        else:
            state["game_over"] = True  # Benar-benar buntu (FAILED)


def draw_confirmed_marker(pos, color, label):
    row, col = pos
    x = col * CELL_SIZE
    y = row * CELL_SIZE
    pygame.draw.rect(screen, color, (x + 4, y + 4, CELL_SIZE - 8, CELL_SIZE - 8), 4)
    text = font_label.render(label, True, color)
    screen.blit(text, (x + 10, y + 8))


running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == MOVE_EVENT:
            step_agent(agent_state)

    screen.fill("white")

    # 1. Gambar grid
    for row in range(SIZE):
        for col in range(SIZE):
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            pygame.draw.rect(screen, "black", (x, y, CELL_SIZE, CELL_SIZE), 2)

    # 2. Gambar stench (hanya jika wumpus masih hidup)
    if agent_state["wumpus_alive"]:
        for wp_row, wp_col in get_neighbors(WUMPUS):
            x = wp_col * CELL_SIZE
            y = wp_row * CELL_SIZE
            text = font_text.render("<<", True, "black")
            screen.blit(text, text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2)))

    # 3. Gambar breeze
    for pit in PITS:
        for pit_row, pit_col in get_neighbors(pit):
            x = pit_col * CELL_SIZE
            y = pit_row * CELL_SIZE
            text = font_text.render("~~", True, "black")
            screen.blit(text, text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 3)))

    # 4. Gambar gold (hanya jika belum diambil)
    if not agent_state["has_gold"]:
        x = GOLD[1] * CELL_SIZE
        y = GOLD[0] * CELL_SIZE
        text_gold = font_emoji.render("💰", True, "black")
        text = pygame.transform.scale(text_gold, (30, 30))
        screen.blit(text, text.get_rect(center=(x + CELL_SIZE // 2, y + ((CELL_SIZE // 2) + 30))))

    # 5. Gambar pit
    for pit in PITS:
        x = pit[1] * CELL_SIZE
        y = pit[0] * CELL_SIZE
        text = font_emoji.render("⚫", True, "black")
        screen.blit(text, text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2)))

    # 6. Gambar wumpus (hanya jika wumpus masih hidup)
    if agent_state["wumpus_alive"]:
        x = WUMPUS[1] * CELL_SIZE
        y = WUMPUS[0] * CELL_SIZE
        text = font_emoji.render("💀", True, "black")
        screen.blit(text, text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2)))

    # 7. Tandai hasil deduksi agen (kotak yang SUDAH terbukti lewat inferensi)
    for pos in agent_state["confirmed_wumpus"]:
        draw_confirmed_marker(pos, "red", "W")
    for pos in agent_state["confirmed_pit"]:
        draw_confirmed_marker(pos, "orange", "P")

    # 8. Gambar Agent
    current_agent_row, current_agent_col = agent_state["position"]
    x = current_agent_col * CELL_SIZE
    y = current_agent_row * CELL_SIZE

    if agent_state["game_over"]:
        agent_icon = "💀"
    else:
        agent_icon = "🧍"

    text = font_emoji.render(agent_icon, True, "black")
    screen.blit(text, text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2)))

    pygame.display.flip()

pygame.quit()