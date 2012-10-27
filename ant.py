import numpy as np
import random

def sigmoid(z):
    ez = np.exp(z)
    emz = np.exp(-z)
    return ez / (ez + emz)

class MoveExistsCode:
    NO = 0 
    YES = 1 

class Actor: 
    '''
    Actor is a player in the game being played. We make no assumptions
    about its strategy or preferences, but we do assume that its
    strategies are directed towards maximizing its utility.
    '''
    def __init__(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def get_strategy_vector(self, move):
        raise NotImplementedError

    def get_preferences_vector(self, game):
        raise NotImplementedError

    def mutate_strategy(self):
        raise NotImplementedError
    
    def unmutate_strategy(self):
        raise NotImplementedError

    def retrain(self, game, game_day, num_dreams):
        old_utility = np.dot(self.get_preferences_vector(game), 
                             game.get_rewards_vector(self, game_day))

        for x in xrange(num_dreams):
            # Try out a new strategy in a dream
            self.mutate_strategy()
            utility = self.dream(game, game_day)

            # The more our new utility surpasses the old utility, the
            # more likely we are to keep our strategy switched
            if random.random() < sigmoid(old_utility-utility):
                self.unmutate_strategy()
            else:
                old_utility = utility

    def dream(self, game, game_day):
        dream = game_day.copy()

        for move in game.player_moves_iter(self):
            if random.random() < sigmoid(np.dot(self.get_strategy_vector(move), 
                                                  game.get_rules_vector(self, move))):
                dream.play_move(move)
            else:
                dream.play_non_move(move)

        for reward in game.player_rewards_iter(self):
            if random.random() < sigmoid(np.dot(game.get_scores_vector(self, dream, reward),
                                                  game.get_easiness_vector(self, reward))):
                dream.give_reward(self, reward)
            else:
                dream.give_no_reward(self, reward)
                                               
        utility = np.dot(self.get_preferences_vector(game), game.get_rewards_vector(self, dream))

        return utility

class Game: 
    '''The game being played. The implementation encodes rules, and
    also has generator functions that yield all possible moves.'''
    def __init__(self):
        raise NotImplementedError

    def player_moves_iter(self, actor):
        '''A generator over all moves for a particular actor.'''
        raise NotImplementedError

    def all_moves_iter(self):
        '''A generator over all moves for for all actors.'''
        raise NotImplementedError

    def player_rewards_iter(self, actor):
        '''A generator over all rewards for a particular actor.'''
        raise NotImplementedError

    def get_rules_vector(self, actor, move):
        '''Modeling the probability that actor will play move.'''
        raise NotImplementedError

    def get_scores_vector(self, actor, game_day, reward):
        '''Modeling the probability that actor will get reward given the moves in gameday.'''
        raise NotImplementedError

    def get_easiness_vector(self, actor, reward):
        '''Also modeling the probability that actor will get reward'''
        raise NotImplementedError

    def get_rewards_vector(self, actor, game_day):
        '''Just a zero-one vector to be dotted with the preferences
        vector of the actor.'''
        raise NotImplementedError

    def report_on_game_day(self, game_day):
        raise NotImplementedError

    def generate_game_day(self):
        game_day = GameDay()

        for actor in self.actors:
            for move in self.player_moves_iter(actor):
                if random.random() < sigmoid(np.dot(actor.get_strategy_vector(move), 
                                                      self.get_rules_vector(actor, move))):
                    game_day.play_move(move)
                else:
                    game_day.play_non_move(move)

        for actor in self.actors:
            for reward in self.player_rewards_iter(actor):
                if random.random() < sigmoid(np.dot(self.get_scores_vector(actor, game_day, reward),
                                                      self.get_easiness_vector(reward))):
                    game_day.give_reward(actor, reward)
                else:
                    game_day.give_no_reward(actor, reward)
                                               
        return game_day

    def simulate(self, num_days, num_dreams):
        for i in xrange(num_days):
            print 'DAY #%d' % i

            # waking
            game_day = self.generate_game_day()
            self.report_on_game_day(game_day)

            # dreaming
            for actor in self.actors:
                actor.retrain(self, game_day, num_dreams)
                
class GameDay:
    '''A particular execution of a game. Some moves may be
    hidden. Note that moves and rewards have to be something that
    always hashes to the same thing, and thus objects won't work (by
    default?).'''
    def __init__(self):
        self.moves = {}
        self.rewards = {}

    def copy(self):
        gd = GameDay()
        gd.moves = self.moves.copy()
        gd.rewards = self.rewards.copy()
        return gd

    def move_exists(self, move):
        if move in self.moves:
            return (self.moves[move] == MoveExistsCode.YES)
        else:
            return False

    def move_does_not_exist(self, move):
        if move in self.moves:
            return (self.moves[move] == MoveExistsCode.NO)
        else:
            return False

    def move_hidden(self, move):
        return not (move in self.moves)

    def play_move(self, move):
        self.moves[move] = MoveExistsCode.YES

    def play_non_move(self, move):
        self.moves[move] = MoveExistsCode.NO

    def play_hide_move(self, move):
        del self.moves[move]

    def reward_exists(self, reward):
        if reward in self.rewards:
            return (self.rewards[reward] == MoveExistsCode.YES)
        else:
            return False

    def reward_does_not_exist(self, reward):
        if reward in self.rewards:
            return (self.rewards[reward] == MoveExistsCode.NO)
        else:
            return False

    def give_reward(self, actor, reward):
        self.rewards[actor,reward] = MoveExistsCode.YES

    def give_no_reward(self, actor, reward):
        self.rewards[actor,reward] = MoveExistsCode.NO
