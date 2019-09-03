# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 14:49:57 2019

@author: Jojo
"""

import gym

from gym import spaces

from gym.utils import seeding
from random import sample 

# read_csv with all the training set

class Sportify(gym.Env):
    def __init__(self, xtrain,xtest,training,train_id,test_id):

# Different actions Home(0) and bet size (20 40 60 80 100)
        
        self.action_space = spaces.Tuple([spaces.Discrete(3), spaces.Discrete(5)])
        self.observation_space = spaces.Box(len(xtrain.columns)-1)# Features + Odds 
        self.odds=1.05
        self.seed()
        self.training=training
        self.minutes=10 # generated randomly between 10 and 90
        self.match_id=145000 # get piked up randomly from the match dataset
        self.outcome=0 # 0 Home not winner at end of match
        self.df_train=xtrain
        self.df_test=xtest
        self.train_id=train_id
        self.test_id=test_id
        self.features=[*xtrain.columns,'Odds']# remove the outcome

    
    # Initialize Odds, minutes and match id and fetch cash
    def _get_obs():

        self.odds=1/(np.randomint(1,99)/100)
        self.minutes=np.randomint(10,90)
        if training==1:
            self.match_id=sample(train_id,1)[0]
            self.outcome=self.df_train[self.df_train['match_id']==self.match_id]['A Winner'].iloc[0]
            dfobs=self.df_train[(self.df_train['match_id']==self.match_id)&(self.df_train['minutes']==self.minutes)]
            dfobs['Odds']=self.odds
            self.observation=dfobs[self.features].drop(['A Winner','match_id'],axis=1)
            
        else:
            self.match_id=sample(test_id,1)[0]
            self.outcome=self.df_test[self.df_test['match_id']==self.match_id]['A Winner'].iloc[0]
            dfobs=self.df_test[(self.df_test['match_id']==self.match_id)&(self.df_test['minutes']==self.minutes)]
            dfobs['Odds']=self.odds
            self.observation=dfobs[self.features].drop(['A Winner','match_id'],axis=1)
        # extract the sample from file (training or testing)
        # etract outcome
    
    def seed(self, seed=None):

        self.np_random, seed = seeding.np_random(seed)

        return [seed]
    
    def step(self, action):
    
            assert self.action_space.contains(action)
            
    
            if action[0] == 0: # We Do no bet
    
                # observation, reward, done, info
    
                return self._get_obs(), 0, False, {}
            
            if action[0]==1: # We buy
                if self.outcome==1:
                    return self._get_obs(), 20*(action[1]+1)*(self.odds-1), False, {}
                else:
                    return self._get_obs(), -20*(action[1]+1), False, {}

            if action[0]==2: # We sell
                if self.outcome==1:
                    return self._get_obs(), -20*(action[1]+1), False, {}
                else:
                    return self._get_obs(), 20*(action[1]+1)*(1/(self.odds-1)), False, {}                                
        
        def reset(self):

        return self._get_obs()