import networkx as nx
import numpy as np
import random, sys
import ant

def friender( (actor1, actor2) ):
    return actor1

def friendee( (actor1, actor2) ):
    return actor2

class FriendingActor(ant.Actor):
    def __init__(self, nplayers, nodeid, grade, race, scode, sex, totalnoms, status=None):
        self.nplayers = nplayers
        self.nodeid = nodeid
        self.grade = int(grade)
        self.race = int(race)
        self.scode = int(scode)
        self.sex = int(sex)
        self.totalnoms = int(totalnoms)

        # what this actor thinks about the status of other actors,
        # including themselves
        self.status_values = np.zeros(nplayers)

    def __repr__(self):
        status = self.status_values[self.nodeid]
        return 'n%d (status=%0.2f) (grade%d race%d scode%d sex%d noms%d' % (
            self.nodeid, status, self.grade, self.race, self.scode, 
            self.sex, self.totalnoms)

    def get_strategy_vector(self, move):
        assert(self == friender(move))
        status_diff = (self.status_values[friendee(move).nodeid] - 
                       self.status_values[self.nodeid])
        return np.array([status_diff])

    def get_preferences_vector(self, game):
        # assume for the moment that your desire for people to like
        # you is immutable and does not depend on the identity of the
        # person in question
        return np.array([ 1.0 for x in xrange(self.nplayers) ])

    def mutate_strategy(self):
        self.old_status_values = self.status_values.copy()
        self.status_values = self.status_values + np.random.randn(len(self.status_values))

    def unmutate_strategy(self):
        self.status_values = self.old_status_values

class FriendingGame(ant.Game): 
    def __init__(self, actors):
        self.actors = actors

    def all_moves_iter(self):
        for actor in self.actors:
            for actor2 in self.actors:
                if actor2 != actor:
                    yield (actor, actor2)
                
    def player_moves_iter(self, actor):
        for actor2 in self.actors:
            if actor2 != actor:
                yield (actor, actor2)

    def player_rewards_iter(self, actor):
        for actor2 in self.actors:
            if actor2 != actor:
                yield (actor2, actor)

    def get_rules_vector(self, actor, move):
        return np.array([1.0])

    def get_scores_vector(self, actor, game_day, reward):
        assert(friendee(reward) == actor)
        if game_day.move_exists(reward):
            return np.array([1.0])
        else:
            return np.array([-1.0])

    def get_easiness_vector(self, actor, reward):
        assert(friendee(reward) == actor)
        # easiness is set to infinity because the friending move will
        # definitely exist, and that's all we care about in our
        # current model
        return np.array([np.infty])

    def get_rewards_vector(self, actor, game_day):
        reward_bits = np.zeros(len(self.actors))
        for i, actor2 in enumerate(self.actors):
            if actor2 != actor and game_day.move_exists( (actor2, actor) ):
                reward_bits[i] = 1.0
                
        return reward_bits


def make_game_day(gf, actors):
    game_day = ant.GameDay()

    for actor1 in actors:
        for actor2 in actors:
            if actor2.nodeid in gf[actor1.nodeid]:
                game_day.play_move( (actor1, actor2) )
            else:
                game_day.play_non_move( (actor1, actor2) )
                
    return game_day


def run(prefix, fname):
    gf = nx.read_gml(fname)

    vdata = [ x for x in gf.nodes() ]
    actors = [ FriendingActor(nplayers = len(vdata),
                              nodeid = nodeid,
                              grade = gf.node[nodeid][prefix + 'grade'],
                              race = gf.node[nodeid][prefix + 'race'],
                              scode = gf.node[nodeid][prefix + 'scode'],
                              sex = gf.node[nodeid][prefix + 'sex'],
                              totalnoms = gf.node[nodeid][prefix + 'totalnoms'])
               for nodeid in vdata ]

    game = FriendingGame(actors)
    game_day = make_game_day(gf, actors)

    # start with dreaming, since we have data
    print 'INITIAL DREAMING'
    for actor in actors:
        actor.retrain(game, game_day, num_dreams=10)

    sys.exit()

    game.simulate(num_days=10, num_dreams=10)

prefix = sys.argv[1] # comm10_
fname = sys.argv[2]  # data/comm10.gml

run(prefix, fname)
