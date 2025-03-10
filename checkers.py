import tkinter as tk
from tkinter import messagebox
import random


class Checkers(tk.Tk):
    """This is the core functionality of the game."""

    def __init__(self):
        """Constructor Method"""
        super().__init__()
        self.title("Checkers")
        self.geometry("800x850")

        # This renders the toolbar that appears above the checkerboard.
        self.toolbar = tk.Frame(self, height=50, bg='grey')
        self.toolbar.pack(side="top", fill="x")

        # This creates the Rules button on the toolbar.
        rules_button = tk.Button(self.toolbar,
                                 text="Show Rules",
                                 command=self.display_rules)
        rules_button.pack(side="left", padx=5, pady=5)

       # This creates the Rules button on the toolbar.
        difficulty_button = tk.Button(self.toolbar,
                                      text="Change Difficulty",
                                      command=self.difficulty_selector)
        difficulty_button.pack(side="left", padx=10, pady=10)
        self.canvas = tk.Canvas(self, bg="white", height=800, width=800)
        self.canvas.pack()
        self.board_rendering()
        self.checker_placement()
        self.canvas.bind("<Button-1>", self.click_mechanics)
        self.selected_piece = None
        self.current_turn = "black"
        self.turn_count = 1
        self.move_stack = []
        self.drag_data = {"x": 0, "y": 0, "piece": None}
        self.canvas.bind("<B1-Motion>", self.drag_mechanics)
        self.canvas.bind("<ButtonRelease-1>", self.drop_mechanics)
        self.difficulty = None
        self.difficulty_selector()
        self.valid_ai_moves = True

    def display_rules(self):
        "This displays the rules when the button is clicked."
        rules_window = tk.Toplevel(self)
        rules_window.title("Game Rules")
        rules_window.geometry("400x300")
        rules_text = tk.Text(rules_window, wrap="word")
        rules_text.pack(expand=True, fill="both")
        rules = """
        Checkers Game Rules:

        01. Players take turns, moving one piece per turn. A move must be made every turn.

        02. Pieces can only move diagonally on black squares. White squares are not valid.

        03. If a piece is captured, it is removed from the board

        04. If a capture is available, it MUST be made. 

        05. If multiple captures are available to the same piece, they may be made after the first capture.

        06. If a piece reaches the furthest row on the opponent's side, it becomes a king.
        
        07. Once crowned king, the turn ends, even if additional captures are possible.

        08. Kings can move backwards or forwards; all other pieces can only move forwards.

        09. Regicide: If a piece captures a king, it then becomes a king. The turn ends.

        10. If all pieces are removed from either player's side, they lose.

        11. If a player is unable to make a valid move, they lose.
        """
        rules_text.insert("1.0", rules)
        rules_text.config(state="disabled")

    def board_rendering(self):
        """This draws the checkerboard at the beginning of the game."""
        self.squares = {}
        # This iterates over each square and randers it on the board.
        for row in range(8):
            for col in range(8):
                x1, y1 = col * 100, row * 100
                x2, y2 = x1 + 100, y1 + 100
                # Alternates color on every other square.
                color = "black" if (row + col) % 2 else "white"
                self.squares[(row, col)] = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=color, tags="square")

    def checker_creation(self, row, col, color):
        """This creates every checker."""
        x1, y1 = col * 100 + 25, row * 100 + 25
        x2, y2 = x1 + 50, y1 + 50
        checker_id = self.canvas.create_oval(x1,
                                             y1,
                                             x2,
                                             y2,
                                             fill=color,
                                             tags="checker")
        self.checkers[checker_id] = (row, col, color, False
                                     )  # False => not a king.

    def checker_placement(self):
        """This places every checker on the board at the beginning."""
        self.checkers = {}
        # This renders the red checkers on the board.
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    self.checker_creation(row, col, "red")
        # This renders the black checkers on the board.
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    self.checker_creation(row, col, "black")

    def difficulty_selector(self):
        """This controls the difficulty level of the game."""
        dialogue = difficulty_window(self)
        self.wait_window(dialogue)
        while dialogue.difficulty is None:
            messagebox.showwarning("Warning",
                                   "First, please select a difficulty level.")
            dialogue = difficulty_window(self)
            self.wait_window(dialogue)
        self.difficulty = dialogue.difficulty

    def drag_mechanics(self, event):
        """This is the 'drag' half of drag and drop mechanics."""
        if self.drag_data["piece"]:
            # Figures out how much the mouse has moved.
            delta_x = event.x - self.drag_data["x"]
            delta_y = event.y - self.drag_data["y"]
            # Moves the checker along with the mouse.
            self.canvas.move(self.drag_data["piece"], delta_x, delta_y)
            # Stores the position.
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def drop_mechanics(self, event):
        """This is the 'drop' half of drag and drop mechanics."""
        if not self.drag_data["piece"]:
            return

        col = event.x // 100
        row = event.y // 100
        target_square = (row, col)

        valid_move = target_square in self.valid_moves_for_piece
        required_capture = (self.mandatory_capture and any(
            abs(move[0] - self.checkers[self.selected_piece][0]) == 2
            for move in self.valid_moves_for_piece))

        # First checks validity and then makes a capture if available.
        if valid_move and (not self.mandatory_capture or required_capture):
            x1, y1 = col * 100 + 25, row * 100 + 25
            self.canvas.coords(self.drag_data["piece"], x1, y1, x1 + 50,
                               y1 + 50)
            self.checker_movement(target_square, is_subsequent_jump=False)
            self.turn_count += 1
            self.after(500, self.AI_movement)
            print(f"Moved piece to {target_square}.")
        else:
            if self.search_for_captures(self.current_turn) == True:
                messagebox.showinfo("Mandatory Capture",
                                    "You must make a capture this turn!")
            else:
                messagebox.showinfo("Invalid Move",
                                    "You must move to a valid square!")
            original_x, original_y = self.drag_data["original_pos"]
            self.canvas.coords(self.drag_data["piece"], original_x, original_y,
                               original_x + 50, original_y + 50)
            print(f"Invalid move attempted to {target_square}, reverting.")

        # This resets the Drag data.
        self.drag_data = {"x": 0, "y": 0, "piece": None, "original_pos": None}

    def click_mechanics(self, event):
        """This click event is triggered when the player clicks a checker."""
        # At the start of each round, check to see if the game is over.
        if self.game_over():
            return

        col = event.x // 100
        row = event.y // 100
        clicked_square = (row, col)
        clicked_checker = self.checker_locator(row, col)
        print("Clicked square:", clicked_square, "Checker ID:",
              clicked_checker)

        if clicked_checker and self.checkers[clicked_checker][
                2] == self.current_turn:
            self.selected_piece = clicked_checker
            self.drag_data["piece"] = clicked_checker
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.drag_data["original_pos"] = (col * 100 + 25, row * 100 + 25)
            self.valid_moves_for_piece = self.move_validator(clicked_checker)
            self.mandatory_capture = self.search_for_captures(
                self.current_turn)
            self.valid_move_highlighter(clicked_checker)

        if self.turn_count == 1 and clicked_checker and self.checkers[
                clicked_checker][2] == "red":
            messagebox.showinfo("Start of Game", "Black moves first!")
        elif clicked_checker and self.checkers[clicked_checker][
                2] != self.current_turn:
            messagebox.showwarning("Wrong Turn", "It's not your turn!")
        else:
            mandatory_capture = self.search_for_captures(self.current_turn)
            if clicked_checker and self.checkers[clicked_checker][
                    2] == self.current_turn:
                if self.selected_piece:
                    possible_moves = self.move_validator(self.selected_piece)
                    if clicked_square in possible_moves:
                        if mandatory_capture and not any(
                                abs(row -
                                    self.checkers[self.selected_piece][0]) == 2
                                for row, col in possible_moves):
                            messagebox.showwarning("Mandatory Jump",
                                                   "You must make a capture!")
                            self.selected_piece = None
                        else:
                            print("Moving checker to:", clicked_square)
                            self.checker_movement(clicked_square,
                                              is_subsequent_jump=False)
                            self.turn_count += 1
                            self.after(500, self.AI_movement)
                else:
                    print("Selecting checker:", clicked_checker)
                    self.checker_selector(clicked_checker, row, col)
            elif self.selected_piece:
                possible_moves = self.move_validator(self.selected_piece)
                if clicked_square in possible_moves:
                    if mandatory_capture and not any(
                            abs(row -
                                self.checkers[self.selected_piece][0]) == 2
                            for row, _ in possible_moves):
                        messagebox.showwarning("Mandatory Jump",
                                               "You must make a capture!")
                        self.selected_piece = None
                    else:
                        print("Moving checker to:", clicked_square)
                        self.checker_movement(clicked_square,
                                          is_subsequent_jump=False)
                        self.turn_count += 1
                        self.after(500, self.AI_movement)

    def checker_locator(self, row, col):
        """This searches for a checker at a specific location."""
        for checker_id, (checker_row, checker_col, _,
                         _) in self.checkers.items():
            if (checker_row, checker_col) == (row, col):
                return checker_id
        return None

    def checker_selector(self, checker_id, row, col):
        """This selects a specific checker."""
        if (row + col) % 2 == 1:
            self.selected_piece = checker_id
            # Stores the valid moves.
            self.valid_moves_for_piece = self.move_validator(checker_id)

    def valid_move_highlighter(self, checker_id):
        """This highlights valid moves for the player's checker."""
        self.highlight_remover()
        move_validator = self.move_validator(checker_id)
        for move in move_validator:
            row, col = move
            self.canvas.itemconfig(self.squares[(row, col)],
                                   outline="gold",
                                   width=2)

    def highlight_remover(self):
        """This removes highlights after a move is chosen."""
        for key in self.squares:
            self.canvas.itemconfig(self.squares[key], outline="black", width=1)

    def checker_movement(self, target_square, is_subsequent_jump=False):
        """This actually moves the checker after the player makes a choice."""
        if self.selected_piece:

            # Before making a move, the old position is stored.
            old_row, old_col, color, is_king = self.checkers[
                self.selected_piece]

            # The piece is moved on the canvas.
            row, col = target_square
            x1, y1 = col * 100 + 25, row * 100 + 25
            self.canvas.coords(self.selected_piece, x1, y1, x1 + 50, y1 + 50)
            self.highlight_remover()

            # Does this move make the piece a king?
            becoming_king = False
            if not is_king and ((color == "red" and row == 7) or
                                (color == "black" and row == 0)):
                is_king = True
                becoming_king = True
                self.canvas.itemconfig(self.selected_piece,
                                       outline="gold",
                                       width=2)
                print(f"Piece {self.selected_piece} has been kinged.")

            # Updates the position and king status in the dictionary.
            self.checkers[self.selected_piece] = (row, col, color, is_king)

            # Was the move a capture?
            if abs(row - old_row) == 2 and abs(col - old_col) == 2:
                jumped_row = (old_row + row) // 2
                jumped_col = (old_col + col) // 2
                jumped_piece = self.checker_locator(jumped_row, jumped_col)
                if jumped_piece:
                    _, _, _, jumped_is_king = self.checkers[jumped_piece]
                    # Removes the captured piece.
                    self.canvas.delete(jumped_piece)
                    del self.checkers[jumped_piece]

                    # Regicide: If the piece captures a king then it becomes a king.
                    if jumped_is_king:
                        is_king = True
                        becoming_king = True
                        self.canvas.itemconfig(self.selected_piece,
                                               outline="gold",
                                               width=2)
                        print(
                            f"Piece {self.selected_piece} has been kinged due to Regicide."
                        )

                    # Checks to see if another capture is possible.
                    if not becoming_king:  # If the piece has just reached king's row, it is excluded.
                        additional_jumps = self.additional_captures(
                            self.selected_piece, is_subsequent_jump)
                        if additional_jumps:
                            self.valid_move_highlighter(self.selected_piece)
                            print("Additional jumps available.")
                            # Does the player want to make the second capture?
                            if is_subsequent_jump:
                                print(
                                    "Player may choose to continue jumping or end their turn."
                                )
                                return
                            else:
                                player_wants_to_continue = self.additional_capture_prompt(
                                )
                                if player_wants_to_continue:
                                    print(
                                        "Player chooses to continue jumping.")
                                    return
                                else:
                                    print("Player chooses to end their turn.")
                                    self.highlight_remover()

                        else:
                            print("No additional jumps available.")

                    # Update the dictionary with the piece's new status.
                    self.checkers[self.selected_piece] = (row, col, color,
                                                          is_king)

            # If there are no other captures available or the piece was just kinged, turn ends.
            self.current_turn = "red" if self.current_turn == "black" else "black"
            # Deselects the piece after making the move.
            self.selected_piece = None
            if self.current_turn == "red":
                self.after(500, self.AI_movement)

    def move_validator(self, checker_id):
        """This is the logic for checking the validity of moves."""
        current_row, current_col, color, is_king = self.checkers[checker_id]
        moves = set()
        captures = set()
        enemy_color = "black" if color == "red" else "red"

        # Movement directions determined by color and whether kinged.
        directions = [-1, 1] if is_king else ([1] if color == "red" else [-1])

        for row_diff in directions:
            for col_diff in [-1, 1]:
                new_row, new_col = current_row + row_diff, current_col + col_diff
                if 0 <= new_row < 8 and 0 <= new_col < 8 and (
                        new_row + new_col) % 2 == 1:
                    target = self.checker_locator(new_row, new_col)
                    if target is None:
                        moves.add((new_row, new_col))
                    elif self.checkers[target][2] == enemy_color:
                        # Are captures available?
                        jump_row, jump_col = new_row + row_diff, new_col + col_diff
                        if 0 <= jump_row < 8 and 0 <= jump_col < 8 and (
                                jump_row + jump_col) % 2 == 1:
                            if self.checker_locator(jump_row,
                                                    jump_col) is None:
                                captures.add((jump_row, jump_col))

        # If a capture is available, it is the only valid move.
        return captures if captures else moves

    def additional_captures(self, checker_id, is_subsequent_jump=False):
        """This looks for additional captures after the player makes a capture."""
        _, _, color, is_king = self.checkers[checker_id]
        moves = self.move_validator(checker_id)
        # Searches for available captures.
        jumps = {
            move
            for move in moves
            if abs(move[0] - self.checkers[checker_id][0]) == 2
        }
        return jumps

    def AI_movement(self):
        # Triggers first if game is over
        if self.game_over():
            return
        if self.current_turn != "red":
            print("Not AI's turn.")
            return
        print("AI's turn to move.")

        # Are there required captures for AI?
        if self.search_for_captures("red"):
            # Locate the first capture and execute it.
            for checker_id, details in self.checkers.items():
                if details[2] == 'red':
                    move_validator = self.move_validator(checker_id)
                    capture_moves = [
                        move for move in move_validator
                        if abs(move[0] - details[0]) == 2
                    ]
                    if capture_moves:
                        best_move = capture_moves[0]
                        self.checker_selector(checker_id,
                                            *self.checkers[checker_id][:2])
                        self.checker_movement(best_move, is_subsequent_jump=False)
                        print(
                            f"AI performing forced capture with piece {checker_id} to {best_move}"
                        )

                        # Are there additional captures available?
                        additional_jumps = self.additional_captures(
                            checker_id, False)
                        if additional_jumps:
                            next_jump = next(iter(additional_jumps))
                            print("AI has additional jumps available.")
                            self.after(
                                1000, lambda: self.AI_capture(
                                    checker_id, next_jump))
                        break
        else:
            # If no captures available, then minimax is invoked.
            print("AI is thinking...")
            _, best_move = self.minimax(self.difficulty, True, float('-inf'),
                                        float('inf'))
            if best_move:
                selected_piece, move = best_move
                self.checker_selector(selected_piece,
                                    *self.checkers[selected_piece][:2])
                self.checker_movement(move, is_subsequent_jump=False)
                print(f"AI selected move: {move} for piece {selected_piece}")
                print(f"Turn: {self.turn_count}")
                print(f"AI move: {move}")

                # Checks for additional captures if needed.
                if abs(move[0] - self.checkers[selected_piece][0]) == 2:
                    self.after(
                        1000, lambda: self.AI_additional_captures(
                            selected_piece, True))
            else:
                print("AI has no valid moves.")
                self.valid_ai_moves = False
                self.game_over()

        print(f"AI completed its turn.")

    def AI_additional_captures(self, selected_piece, is_subsequent_jump):
        """This performs subsequent captures for the AI."""
        if selected_piece in self.checkers:
            additional_jumps = self.additional_captures(
                selected_piece, is_subsequent_jump)
            if additional_jumps:
                print("AI has additional jumps available.")
                next_jump = random.choice(list(additional_jumps))
                print(f"AI preparing for additional jump to: {next_jump}")
                self.after(
                    1000,
                    lambda: self.AI_capture(selected_piece, next_jump))
            else:
                # No further captures? Switch turns.
                print("No additional jumps available.")
                self.turn_switcher()
        else:
            # If piece was removed, switch turns.
            print("Selected piece no longer exists.")
            self.turn_switcher()

    def AI_capture(self, selected_piece, next_jump):
        """This is how the AI executes captures."""
        # Does the piece still exist?
        if selected_piece in self.checkers:
            self.checker_movement(next_jump, is_subsequent_jump=True)
            # Check for additional captures.
            self.after(
                1000,
                lambda: self.AI_additional_captures(selected_piece, True))
        else:
            print("Jumping piece has been removed.")
            self.turn_switcher()

    def search_for_captures(self, color):
        """This determines is captures are open for the chosen checker."""
        for checker_id, details in self.checkers.items():
            if details[2] == color:
                moves = self.move_validator(checker_id)
                # Check if any capture moves are available.
                for move in moves:
                    current_row, _ = self.checkers[checker_id][:2]
                    if abs(move[0] - current_row) == 2:
                        return True
        return False

    def search_for_valid_moves(self, color):
        """This checks to see if any valid moves exist for the chosen checker."""
        for checker_id, details in self.checkers.items():
            if details[2] == color:
                if self.move_validator(checker_id):
                    return True
        return False

    def additional_capture_prompt(self):
        """This prompts the player to make a second jump if one is available."""
        # AI will automatically continue jumping.
        if self.current_turn == "red":
            return True
        else:
            response = messagebox.askyesno(
                "Continue Jumping?",
                "You can make another jump. Do you want to continue jumping?")

            return response

    def minimax(self, depth, maximizing_player, alpha, beta):
        """This is the minimax algorithm with alpha-beta pruning."""
        if depth == 0 or self.game_over():
            return self.evaluation_function(), None

        if maximizing_player:
            max_eval = float('-inf')
            best_move = None
            successors = self.successor_function("red")
            for checker_id, move in successors:
                self.simulation(checker_id, move)
                eval, _ = self.minimax(depth - 1, False, alpha, beta)
                self.clear_simulation()
                if eval > max_eval:
                    max_eval = eval
                    best_move = (checker_id, move)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            successors = self.successor_function("black")
            for checker_id, move in successors:
                self.simulation(checker_id, move)
                eval, _ = self.minimax(depth - 1, True, alpha, beta)
                self.clear_simulation()
                if eval < min_eval:
                    min_eval = eval
                    best_move = (checker_id, move)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def successor_function(self, color):
        """This is the successor function for minimax."""
        print("Generating successors for color:", color)
        successors = []
        for checker_id in self.checkers:
            if self.checkers[checker_id][2] == color:
                move_validator = self.move_validator(checker_id)
                for move in move_validator:
                    successors.append((checker_id, move))
        return successors

    def simulation(self, checker_id, target_square):
        """Evaluates potential moves by simulating the movement of checkers."""
        print("Simulating move for checker:", checker_id, "to", target_square)
        if checker_id:
            old_row, old_col, color, is_king = self.checkers[checker_id]
            new_row, new_col = target_square

            # Adds original state onto stack, then changes.
            self.move_stack.append(
                (checker_id, (old_row, old_col, color, is_king)))

            # Updates the position and king status of the piece.
            becoming_king = not is_king and (
                (color == "red" and new_row == 7) or
                (color == "black" and new_row == 0))
            if becoming_king:
                is_king = True

            self.checkers[checker_id] = (new_row, new_col, color, is_king)

            # Implements the capturing.
            if abs(new_row - old_row) == 2 and abs(new_col - old_col) == 2:
                jumped_row = (old_row + new_row) // 2
                jumped_col = (old_col + new_col) // 2
                jumped_piece = self.checker_locator(jumped_row, jumped_col)
                if jumped_piece:
                    self.move_stack.append(
                        (jumped_piece, self.checkers[jumped_piece]))
                    del self.checkers[jumped_piece]

    def clear_simulation(self):
        """Erases the moves after they are made in the simulation."""
        print("Undoing move")
        while self.move_stack:
            checker_id, old_state = self.move_stack.pop()
            self.checkers[checker_id] = old_state

    def evaluation_function(self):
        """Evaluates the board by counting piece difference."""
        print("Evaluating board")
        # A basic evaluation based on counting the pieces.
        red_pieces = sum(1 for piece in self.checkers.values()
                            if piece[2] == "red")
        black_pieces = sum(1 for piece in self.checkers.values()
                            if piece[2] == "black")
        return red_pieces - black_pieces  

    def find_every_move(self, color):
        """Produces a list of every move that is valid for the given player."""
        print("Getting all moves for color:", color)
        move_validator = {}
        for checker_id, details in self.checkers.items():
            if details[2] == color:
                moves = self.move_validator(checker_id)
                if moves:
                    move_validator[checker_id] = moves
        return move_validator

    def turn_switcher(self):
        self.current_turn = "red" if self.current_turn == "black" else "black"
        self.selected_piece = None
        if self.current_turn == "red":
            self.after(500, self.AI_movement)
        print(f"Turn switched to {self.current_turn}.")

    def game_over(self):
        # Sums remaining pieces for each color.
        red_pieces = sum(1 for piece in self.checkers.values()
                         if piece[2] == "red")
        black_pieces = sum(1 for piece in self.checkers.values()
                           if piece[2] == "black")

        # Should the game end?
        if red_pieces == 0:
            messagebox.showinfo("Game Over", "Black wins!")
            return True
        elif black_pieces == 0:
            messagebox.showinfo("Game Over", "Red wins!")
            return True
        elif self.valid_ai_moves == False:
            messagebox.showinfo("Game Over",
                                "Game over! AI has no valid moves.")
            return True
        return False


class difficulty_window(tk.Toplevel):
    """This class is needed for rendering the difficulty selection dialogue box."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Select Difficulty")
        self.geometry("300x200")
        self.difficulty = None

        tk.Button(self, text="Easy",
                  command=lambda: self.set_difficulty(4)).pack(pady=5)
        tk.Button(self, text="Medium",
                  command=lambda: self.set_difficulty(6)).pack(pady=5)
        tk.Button(self, text="Hard",
                  command=lambda: self.set_difficulty(8)).pack(pady=5)
        tk.Button(self,
                  text="Inhuman",
                  command=lambda: self.set_difficulty(10)).pack(pady=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def set_difficulty(self, level):
        """Sets the difficulty."""
        self.difficulty = level
        self.destroy()

    def on_close(self):
        """What happens when the dialogue box is closed."""
        self.difficulty = None
        self.destroy()


if __name__ == "__main__":
    game = Checkers()
    game.mainloop()
