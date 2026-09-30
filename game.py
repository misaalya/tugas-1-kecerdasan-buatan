import pygame

pygame.init()

# setup
SIZE = 4
WINDOW_SIZE = 600
CELL_SIZE = WINDOW_SIZE // SIZE  # 150

screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Agent Grid")

font_emoji = pygame.font.SysFont("notocoloremoji", 18)
font_text = pygame.font.SysFont("arial", 18)


# world objects
WUMPUS = (1, 0)
PITS = [
    (0, 3),
    (1, 2),
    (3, 2),
]
GOLD = (1, 1)

# start agent
agent_position = [3, 0]

#helper neighbors hanya mengembalikan neighbour yang bukan wall
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

running = True

while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            row, col = agent_position

            if event.key == pygame.K_UP and row > 0:
                agent_position[0] -= 1

            elif event.key == pygame.K_DOWN and row < SIZE - 1:
                agent_position[0] += 1

            elif event.key == pygame.K_LEFT and col > 0:
                agent_position[1] -= 1

            elif event.key == pygame.K_RIGHT and col < SIZE - 1:
                agent_position[1] += 1

    screen.fill("white")

    # gambar grid
    for row in range(SIZE):
        for col in range(SIZE):
            x = col * CELL_SIZE
            y = row * CELL_SIZE

            pygame.draw.rect(
                screen,
                "black",
                (x, y, CELL_SIZE, CELL_SIZE),
                2
            )

            #gambar pit
            for pit in PITS:
                if(pit[0] == row) and (pit[1] == col):
                    text = font_emoji.render(
                        f"⚫",
                        True,
                        "black"
                    )
                    
                    text_rect = text.get_rect(
                        center=(
                            # bagi dua biar tepat jadi 75 x dan y nya (ditengah CELL)
                            x + CELL_SIZE // 2,
                            y + CELL_SIZE // 2
                        )
                    )
                
                    screen.blit(text, text_rect)

            #gambar wumpus
            if(WUMPUS[0] == row) and (WUMPUS[1] == col):
                text = font_emoji.render(
                    f"💀",
                    True,
                    "black"
                )
                
                text_rect = text.get_rect(
                    center=(
                        # bagi dua biar tepat jadi 75 x dan y nya (ditengah CELL)
                        x + CELL_SIZE // 2,
                        y + CELL_SIZE // 2
                    )
                )
            
                screen.blit(text, text_rect)

            #gambar gold
            if(GOLD[0] == row) and (GOLD[1] == col):
                text_gold = font_emoji.render(
                    f"💰",
                    True,
                    "black"
                )

                small = (30, 30) 
                text = pygame.transform.scale(text_gold, small)
                
                text_rect = text.get_rect(
                    center=(
                        # bagi dua biar tepat jadi 75 x dan y nya (ditengah CELL)
                        x + CELL_SIZE // 2,
                        y + ((CELL_SIZE // 2) + 30)
                    )
                )
            
                screen.blit(text, text_rect)

            # gambar stench
            for wp_row, wp_col in get_neighbors(WUMPUS):
               
                if(wp_row == row) and (wp_col == col):
                    text = font_text.render(
                        f"<<",
                        True,
                        "black"
                    )
                    
                    text_rect = text.get_rect(
                        center=(
                            # bagi dua biar tepat jadi 75 x dan y nya (ditengah CELL)
                            x + CELL_SIZE // 2,
                            y + CELL_SIZE // 2
                        )
                    )
                
                    screen.blit(text, text_rect)

            # gambar breeze
            for pit in PITS:
                for pit_row, pit_col in get_neighbors(pit):
                
                    if(pit_row == row) and (pit_col == col):
                        text = font_text.render(
                            f"~~",
                            True,
                            "black"
                        )
                        
                        text_rect = text.get_rect(
                            center=(
                                # bagi dua biar tepat jadi 75 x dan y nya (ditengah CELL)
                                x + CELL_SIZE // 2,
                                y + CELL_SIZE // 3
                            )
                        )
                    
                        screen.blit(text, text_rect)



    current_agent_row, current_agent_col = agent_position


    x = current_agent_col * CELL_SIZE
    y = current_agent_row * CELL_SIZE

    text = font_emoji.render(
        f"🧍",
        True,
        "black"
    )

    text_rect = text.get_rect(
        center=(
            # bagi dua biar tepat jadi 75 x dan y nya (ditengah CELL)
            x + CELL_SIZE // 2,
            y + CELL_SIZE // 2
        )
    )

    screen.blit(text, text_rect)

    pygame.display.flip()

pygame.quit()