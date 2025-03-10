## Minimax Checkers

This is an interactive checkers game I developed for the Intelligent Systems Techniques module at Sussex (Spring 2024). It uses the Tkinter toolkit to display an interactive GUI, where the human player competes with an AI.

---
### Features:

**Interactive checkers gameplay**

The game is interactive, with the human as Black and the AI as Red. Black always makes the first move and the turn is passed to the AI once all possible moves have been exhausted. Interactivity includes movement, capturing pieces, and having pieces crowned king at the King's Row or via regicide. Once a player captures their opponent's final piece, they win.

---

**Adjustable AI cleverness**

The user is first greeted by a window asking them to select a difficulty level: Easy, Medium, Hard, or Inhuman. These map to Minimax depths of 4, 6, 8, and 10, respectively. The user must make a selection before the game can start. Additionally, I implemented a grey toolbar appearing above the checkerboard. It contains a `Change Difficulty` button that allows the player to adjust the AI's difficulty mid-game if desired.

---

**State representation**

Each checker is given a unique identifier (`checker_id`) that is stored in a dictionary (`self.checkers`). Each `checker_id` serves as a key that's associated with a tuple containing row, column, color, and king status values. This allows the game to track checker positions, move the correct pieces, and bestow or revoke king status from pieces. Additionally, `self.current_turn` keeps track of whose turn it is.

---

**Successor func-on that generates AI moves**

My successor function is called `successor_function`. It accepts a color parameter because it needs to consider both players' possible moves. First, an empty list called `successors` is initialized, and then it iterates over every checker in the `self.checkers` dictionary. For the checkers of the appropriate color, it calls the `valid_moves` function to obtain every valid move for that piece. Next, all possible moves are generated and appended to the `successors` list as tuples containing the `checker_id` and destination square. Finally, the list is returned and used for evaluation by Minimax.

---

**Minimax evaluation and Alpha-Beta pruning**

A method called `minimax` handles Minimax evaluation and alpha-beta pruning. During the AI's turn, the `AI_movement` method calls `minimax` only when no possible captures are possible, since forced captures are in effect. While running, `minimax` has a base case that terminates the recursion when a depth of zero is reached, at which point the `evaluation_function` method is called and a numerical score is assigned to the current state. Alpha-Beta pruning is used to limit the number of nodes that need to be evaluated, optimizing performance. At the end of the evaluation process, the `best_move` is returned to the `AI_movement` method in the form of a `checker_id` and a `move` to make. The relevant piece is selected by `self.checker_selector` and then the move is made on the actual checkerboard GUI by the `checker_movement` method.

---

**Heuristics**

Heuristics are something I really struggled to implement correctly. I kept trying to add more complicated ones, such as evaluating the vulnerability of pieces, penalizing pieces for staying too close to the edge of the board, or priori9zing reaching King's Row. But these kept introducing serious slow-downs in gameplay and sometimes crashes. The only heuristic that I currently have in place considers the discrepancy between the counts of Red and Black pieces. Given that the objective of the game is to wipe out all pieces of the opposing side, it makes sense that the AI should want to maintain more pieces than Black.

---

**AI move validation**

The primary method that is used to ensure the validity of the AI is called `move_validator`. This computes valid moves for a given `checker_id` according to its position, color, and king status. The `AI_movement` method can only be executed during the AI's turn, and the first thing it checks is whether any captures are available. This forces the AI to make a capture.

---

**User move validation**

The user's moves are also checked by the `move_validator` method. When the player clicks a checker, the valid moves for that piece are highlighted on the board.

---

**Rejection of invalid user moves (with explanation)**

If the player attempts to move to any square other than the ones highlighted as valid, an error message will appear telling them it's an invalid move. If capture(s) are possible, the player must make one or an error message will appear that reminds them that captures are compulsory.

---

**Forced capture**

Forced capture is implemented for both human and AI players, but in different ways. In the `drop_mechanics` method, before a player can drop a piece on the board it is checked to make sure that `self.mandatory_capture` evaluates to False. If it evaluates to True, then the piece cannot be dropped and an error message appears. For the AI, before any subsequent logic can be applied, `search_for_captures` is called. If there are any `capture_moves`, the AI makes the capture and `minimax` is not called that turn. Multiple captures are possible to make in one turn if they're available.

---

**Multi-step capturing moves for User**

after the first capture is made, `addi9onal_captures` is called to see if another capture is possible. If there is one, `addi9onal_capture_prompt` is called, which causes a window to appear asking the player if they'd like to make another capture or if they'd rather pass to the AI's turn.

---

**Multi-step capturing moves for AI**

As with humans, after the first capture, `addi9onal_captures` is called to see if more are available. If there is another capture, the AI will automatically take it, and it's executed by `AI_capture`.

---

**King conversion at baseline**

When a player's piece reaches the opposite side of the board, it is instantly crowned king (denoted by a golden halo around the piece) and the turn ends, even if other captures are available. This is handled inside the `checker_movement` method, where an `if` statement evaluates whether a piece of either color has reached king's row. This sets the `is_king` and `becoming_king` Booleans to True and the piece is outlined in gold. Since `addi9onal_jumps` are only evaluated if `becoming_king` is False, multi-step captures are disabled and the turn ends.

---

**Regicide**

Inside `checker_movement`, within the capturing logic, an `if` statement checks if the captured piece was a king. If it was, then the `is_king` and `becoming_king` Booleans are set to True, which crowns the capturing piece king. Again, the `becoming_king` Boolean prevents further captures and the turn ends.

---

**Hints about available moves**

During Black's turn, the valid moves for a given piece are highlighted on the board when it's clicked on (`valid_move_highlighter`). These highlighted squares return to normal after a move is made (`highlight_remover`).

---

**Board representation**

The checkerboard is rendered in the GUI using only `Tkinter`. On startup, `board_rendering` is called by the constructor method and an 8x8 checkerboard is rendered on the screen. It is then populated by pieces by `checker_crea9on` and `checker_placement`.

---

**GUI updates display after completed moves**

after each move, the board is updated in line with the modified checker positions. This is achieved using `self.canvas.coords(self.selected_piece, x1, y1, x1 + 50, y1 +50)`. After captures, `self.canvas.delete(jumped_piece)` removes captured pieces from the board.

---

**In-game instructions**

instructions can be found in a window that displays when the `Show Rules` toolbar button is clicked. This describes valid moves, win conditions, kinging, and other mechanics.

---

**Game interaction**

I implemented a drag and drop mechanic to the GUI so that when the player clicks a piece, it is picked up un9l a destination square is clicked. If the destination is a valid move, then the piece is dropped. In the constructor method, `self.canvas.bind` is used to control what happens when the mouse is clicked, moved, and released. In `click_mechanics`, `drag_mechanics`, and `drop_mechanics`, `self.drag_data` is used to track the coordinates of the piece and place it in the destination square.

---

**System pauses to show the intermediate legs of multi-step moves**

I used Tkinter's `after` function in every place I could think of, but for some reason the AI s9ll makes multi-step captures without pausing. However, for the human there is a pause thanks to the window popping up to ask if they'd like to continue making captures.

---

**Dedicated display of the rules**

I added a `Show Rules` button to the toolbar above the checkerboard that displays a pop- up window containing the rules. The window appearance and the rules are defined by the `display_rules` method.

---
