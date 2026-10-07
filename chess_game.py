import sys
import random
import chess
import pygame

# Khởi tạo Pygame
pygame.init()

# Kích thước màn hình & bàn cờ
WIDTH, HEIGHT = 512, 512
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15

# Màu sắc bàn cờ & ô highlight giống ảnh
COLOR_LIGHT = pygame.Color(238, 238, 210)
COLOR_DARK = pygame.Color(118, 150, 86)

# Bộ ký hiệu Unicode cờ vua đồng dạng chuẩn (Giúp quân đen và trắng cùng kiểu dáng)
PIECE_UNICODE = {
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟', # Quân đen
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'  # Quân trắng
}

def create_font(size):
    """Khởi tạo font chữ hỗ trợ ký hiệu cờ vua Unicode"""
    fonts = ["Segoe UI Symbol", "DejaVu Sans", "Arial Unicode MS", "FreeSerif", "Arial"]
    for font_name in fonts:
        if font_name.lower() in [f.lower() for f in pygame.font.get_fonts()]:
            return pygame.font.SysFont(font_name, size)
    return pygame.font.Font(None, size)

FONT = create_font(int(SQ_SIZE * 0.85))
MSG_FONT = pygame.font.SysFont("Arial", 30, bold=True)

def draw_board(screen, board, selected_sq, last_move):
    """Vẽ bàn cờ, nước đi vừa đi (highlight vàng) và các quân cờ"""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            # 1. Vẽ ô cờ nền sáng/tối
            color = COLOR_LIGHT if (r + c) % 2 == 0 else COLOR_DARK
            rect = pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(screen, color, rect)

            sq_index = chess.square(c, 7 - r)

            # Highlight ô vừa di chuyển (Màu vàng giống hệt trong ảnh)
            if last_move and (sq_index == last_move.from_square or sq_index == last_move.to_square):
                highlight_surface = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
                highlight_surface.fill((255, 255, 102, 180)) # Màu vàng tươi giống ảnh
                screen.blit(highlight_surface, (c * SQ_SIZE, r * SQ_SIZE))

            # Highlight ô đang được nhấp chọn
            if selected_sq == sq_index:
                highlight_surface = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
                highlight_surface.fill((0, 205, 0, 130))
                screen.blit(highlight_surface, (c * SQ_SIZE, r * SQ_SIZE))

            # 2. Vẽ quân cờ dạng Unicode đồng dạng
            piece = board.piece_at(sq_index)
            if piece:
                symbol = PIECE_UNICODE.get(piece.symbol(), piece.symbol())
                # Quân trắng tô màu trắng, Quân đen tô màu đen
                text_color = (255, 255, 255) if piece.color == chess.WHITE else (0, 0, 0)
                
                text_surface = FONT.render(symbol, True, text_color)
                text_rect = text_surface.get_rect(center=(c * SQ_SIZE + SQ_SIZE // 2, r * SQ_SIZE + SQ_SIZE // 2))
                screen.blit(text_surface, text_rect)

def get_ai_move(board):
    """Máy đi ngẫu nhiên nước đi hợp lệ"""
    legal_moves = list(board.legal_moves)
    if legal_moves:
        return random.choice(legal_moves)
    return None

def show_message(screen, text):
    """Hiển thị thông báo khi có bên thắng/thua"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    text_surface = MSG_FONT.render(text, True, (255, 215, 0))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game - Người (Trắng) vs Máy (Đen)")
    clock = pygame.time.Clock()

    board = chess.Board()
    selected_sq = None
    last_move = None
    game_over = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            # Lượt đi của Người (Quân Trắng)
            if not game_over and board.turn == chess.WHITE:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    col = event.pos[0] // SQ_SIZE
                    row = event.pos[1] // SQ_SIZE
                    clicked_sq = chess.square(col, 7 - row)

                    if selected_sq is None:
                        piece = board.piece_at(clicked_sq)
                        if piece and piece.color == chess.WHITE:
                            selected_sq = clicked_sq
                    else:
                        move = chess.Move(selected_sq, clicked_sq)
                        
                        # Phong cấp cho Tốt khi xuống hàng 8 (thành Hậu)
                        if board.piece_at(selected_sq) and board.piece_at(selected_sq).piece_type == chess.PAWN:
                            if chess.square_rank(clicked_sq) == 7:
                                move = chess.Move(selected_sq, clicked_sq, promotion=chess.QUEEN)

                        if move in board.legal_moves:
                            board.push(move)
                            last_move = move
                            selected_sq = None
                        else:
                            piece = board.piece_at(clicked_sq)
                            if piece and piece.color == chess.WHITE:
                                selected_sq = clicked_sq
                            else:
                                selected_sq = None

        # Lượt đi của Máy (Quân Đen)
        if not game_over and board.turn == chess.BLACK:
            pygame.time.wait(300)
            ai_move = get_ai_move(board)
            if ai_move:
                board.push(ai_move)
                last_move = ai_move

        # Kiểm tra ván đấu kết thúc
        if board.is_game_over() and not game_over:
            game_over = True

        # Vẽ giao diện
        draw_board(screen, board, selected_sq, last_move)
        pygame.display.flip()

        # Thông báo kết quả
        if game_over:
            if board.is_checkmate():
                if board.turn == chess.BLACK:
                    show_message(screen, "BẠN ĐÃ THẮNG (CHIẾU HẾT MÁY)!")
                else:
                    show_message(screen, "MÁY ĐÃ THẮNG!")
            elif board.is_stalemate() or board.is_insufficient_material():
                show_message(screen, "HÒA CỜ!")
            
            pygame.time.wait(3000)
            break

        clock.tick(MAX_FPS)

if __name__ == "__main__":
    main()
