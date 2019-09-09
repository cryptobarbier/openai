# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 14:49:57 2019

@author: Jojo
"""
import gym 
import numpy as np
#import gc

from gym import spaces

from gym.utils import seeding
from random import sample 

# read_csv with all the training set

class Sportify(gym.Env):
    def __init__(self, xtrain,xtest,training,train_id,test_id):

# Different actions Home(0) and bet size (20 40 60 80 100)
        
        #print(len(xtrain.columns)-1)
        
        self.action_space = spaces.Discrete(11)
        self.observation_space = spaces.Box(low=np.ones(51)*float(-1000.0),high=np.ones(51)*float(1000),dtype=np.float32)# Features + Odds 
        self.seed()
        self.training=training
        self.minutes=10 # generated randomly between 10 and 90
        self.outcome=0 # 0 Home not winner at end of match
        if training==1:
            self.df=xtrain.sample(20000)
        else:
            self.df=xtest.sample(20000)
        self.train_id=train_id
        self.test_id=test_id
        self.features=[*xtrain.columns,'Odds']# remove the outcome

    
    # Initialize Odds, minutes and match id and fetch cash
    def _get_obs(self):
        #gc.disable()
        self.odds=1/(self.np_random.randint(1,99)/100)
        sa=self.df.sample(1)
        sa['Odds']=self.odds
        #self.minutes=self.np_random.randint(10,90)
        self.outcome=sa['A Winner'].iloc[0]
        self.observation=sa.drop(['A Winner','match_id'],axis=1)
        del sa
        return np.array (self.observation).reshape(51)# extract the sample from file (training or testing)
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
    
