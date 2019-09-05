# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 14:49:57 2019

@author: Jojo
"""
import gym 
import numpy as np

from gym import spaces

from gym.utils import seeding
from random import sample 

# read_csv with all the training set

class Sportify(gym.Env):
    def __init__(self, xtrain,xtest,training,train_id,test_id):

# Different actions Home(0) and bet size (20 40 60 80 100)
        
        #print(len(xtrain.columns)-1)
        
        self.action_space = spaces.Discrete(11)
        self.observation_space = spaces.Box(low=float(-1000.0),high=float(90.0),dtype=np.float32)# Features + Odds 
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
    def _get_obs(self):

        self.odds=1/(self.np_random.randint(1,99)/100)
        self.minutes=self.np_random.randint(10,90)
        
        if self.training==1:
            self.match_id=sample(self.train_id,1)[0]
            self.outcome=self.df_train[self.df_train['match_id']==self.match_id]['A Winner'].iloc[0]
            dfobs=self.df_train.fillna(0)
            dfobs['Odds']=self.odds
            dfobs=dfobs[(dfobs['match_id']==self.match_id)&(dfobs['minutes']==self.minutes)]
            self.observation=dfobs.drop(['A Winner','match_id'],axis=1)
            
        else:
            self.match_id=sample(self.test_id,1)[0]
            self.outcome=self.df_test[self.df_test['match_id']==self.match_id]['A Winner'].iloc[0]
            dfobs=self.df_test.fillna(0)
            dfobs['Odds']=self.odds
            dfobs=dfobs[(dfobs['match_id']==self.match_id)&(dfobs['minutes']==self.minutes)]
            self.observation=dfobs.drop(['A Winner','match_id'],axis=1)
        return np.array (self.observation)# extract the sample from file (training or testing)
        # etract outcome
    
    def seed(self, seed=None):

        self.np_random, seed = seeding.np_random(seed)

        return [seed]
    
    def step(self, action):
    
            assert self.action_space.contains(action)
            
            acti=(action-5)*20
                        
            if acti>=0: # We buy
                if self.outcome==1:
                    return self._get_obs(), acti*(self.odds-1), False, {}
                else:
                    return self._get_obs(), -acti, False, {}
            else:

                if self.outcome==1:
                    return self._get_obs(),-acti, False, {}
                else:
                    return self._get_obs(), acti*(1/(self.odds-1)), False, {}          
                      
    def reset(self):
        return self._get_obs()