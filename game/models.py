from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
GAME_STATUS_CHOICES = (
    ('A', 'Active'),
    ('X', 'First Player Wins'),
    ('O', 'Second Player Wins'),
    ('D', 'Draw')
)

FIRST_PLAYER_MOVE = 'X'
SECOND_PLAYER_MOVE = 'O'
BOARD_SIZE = 8


class GamesManager(models.Manager):
    def games_for_user(self, user):
        """Return a queryset of games that this user participates in"""
        return super(GamesManager, self).get_query_set().filter(
            Q(first_player_id=user.id) | Q(second_player_id=user.id))
        
    def new_game(self, invitation):
        game = Game(first_player=invitation.to_user,
                    second_player=invitation.from_user,
                    next_to_move=invitation.to_user)
        return game

class Game(models.Model):
    first_player = models.ForeignKey(User, related_name="games_first_player")
    second_player = models.ForeignKey(User, related_name="games_second_player")
    next_to_move = models.ForeignKey(User, related_name="games_to_move")
    start_time = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=1, default='A',
                              choices=GAME_STATUS_CHOICES)
    objects = GamesManager()

    def as_board(self):
        """Return a representation of the game board as a two-dimensional list,
        so you can ask for the state of a square at position [y][x].
        
        It will contain a list of lines, where every line is a list of
        'X', 'O', or ''. For example, a 3x3 board position:
        
        [['', 'X', ''],
         ['O', '', ''],
         ['X', '', '']]"""
        board = [['' for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]
        for move in self.move_set.all():
            board[move.y][move.x] = FIRST_PLAYER_MOVE if move.by_first_player else SECOND_PLAYER_MOVE
            
        for x in range(8):
            blanks = False
            for y in range(7, -1, -1):
                if blanks:
                    board[y][x] = "M"
                if board[y][x] == "":
                    blanks = True
        
        return board

    def create_move(self):
        return Move(game=self, by_first_player=(self.next_to_move == self.first_player))

    def update_after_move(self, move):
        """Change game state after a move was made."""
        self.toggle_next_player()
        self.status = self.winner(move)
        
    def winner(self, last_move):
        """Return the status the game should have, given the position of the last move."""
        board = self.as_board()
        x = last_move.x
        y = last_move.y
        # make this function work even if last move was not saved yet
        board[y][x] = FIRST_PLAYER_MOVE if last_move.by_first_player else SECOND_PLAYER_MOVE
   
        # Check rows for winner
        for row in range(8):
            for col in range(5):
                if (board[row][col] == board[row][col + 1] == board[row][col + 2] ==\
                    board[row][col + 3]) and (board[row][col] != "" and board[row][col] != "M"):
                    return board[row][col]
     
        # Check columns for winner
        for col in range(8):
            for row in range(5):
                if (board[row][col] == board[row + 1][col] == board[row + 2][col] ==\
                    board[row + 3][col]) and (board[row][col] != "" and board[row][col] != "M"):
                    return board[row][col]
       
        # Check diagonal (top-left to bottom-right) for winner
       
        for row in range(5):
            for col in range(5):
                if (board[row][col] == board[row + 1][col + 1] == board[row + 2][col + 2] ==\
                    board[row + 3][col + 3]) and (board[row][col] != "" and board[row][col] != "M"):
                    return board[row][col]
               
       
        # Check diagonal (bottom-left to top-right) for winner
       
        for row in range(7, 2, -1):
            for col in range(5):
                if (board[row][col] == board[row - 1][col + 1] == board[row - 2][col + 2] ==\
                    board[row - 3][col + 3]) and (board[row][col] != "" and board[row][col] != "M"):
                    return board[row][col]
       
       
        if self.move_set.count() >= 64:
            return "D"
        
        return "A"

    def toggle_next_player(self):
        if self.next_to_move == self.first_player:
            self.next_to_move = self.second_player
        else:
            self.next_to_move = self.first_player
   
    def is_empty(self, x, y):
        return not self.move_set.filter(x=x, y=y).exists()

    def last_move(self):
        return self.move_set.latest()

    def get_absolute_url(self):
        return reverse('connect4_game_detail', args=[self.id])

    def is_users_move(self, user):
        return self.status == 'A' and self.next_to_move == user

    def __str__(self):
        return "{0} vs {1}".format(self.first_player, self.second_player)


class Move(models.Model):
    x = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(BOARD_SIZE-1)])
    y = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(BOARD_SIZE-1)])
    comment = models.CharField(max_length=300)
    game = models.ForeignKey(Game)
    by_first_player = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        get_latest_by = 'timestamp'

    def player(self):
        return self.game.first_player if self.by_first_player else self.game.second_player
    
    def __str__(self):
        return "{0}".format(self.by_first_player)

class Invitation(models.Model):
    from_user = models.ForeignKey(User, related_name="invitations_sent")
    to_user = models.ForeignKey(User, related_name="invitations_received",
                                verbose_name="User to invite",
                                help_text="Please select the user you want to play a game with")
    message = models.CharField("Optional Message", max_length=300, blank=True,
                               help_text="Adding a friendly message is never a bad idea!")
    timestamp = models.DateTimeField(auto_now_add=True)
