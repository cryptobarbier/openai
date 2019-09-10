# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 14:49:57 2019

@author: Jojo
"""
import gym 
import numpy as np
import gc

from gym import spaces

from gym.utils import seeding

# read_csv with all the training set

# Return random sample from dataframe
def Sampy(df):  
  u=int(np.random.random_sample()*len(df))
  return df.iloc[u]

class Sportify(gym.Env):
    def __init__(self, xtrain,xtest,training,train_id,test_id):

# Different actions Home(0) and bet size (20 40 60 80 100)
        
        #print(len(xtrain.columns)-1)
        
        self.action_space = spaces.Discrete(11)
        self.observation_space = spaces.Box(low=np.ones(51)*float(-1000.0),high=np.ones(51)*float(1000),dtype=np.float32)# Features + Odds 
        self.seed()
        self.features=[*xtrain.columns,'Odds']# remove the outcome
        self.odds=1.05
        self.training=training
        self.outcome=0 # 0 Home not winner at end of match
        if training==1:
            self.df=xtrain
        else:
            self.df=xtest

    
    # Initialize Odds, minutes and match id and fetch cash
    def _get_obs(self):
        self.odds=1/np.random.random_sample()
        self.samp=Sampy(self.df)
        self.outcome=int(self.samp['A Winner'])
        self.obs=self.samp.drop(['A Winner','match_id'])
        self.obs['Odds']=self.odds
        #del sa
        #gc.disable()
        #return np.ones(51)
        return np.array(self.obs).reshape(51)# extract the sample from file (training or testing)
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
    
