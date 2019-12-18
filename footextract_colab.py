# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 20:13:31 2019

@author: PC
"""

import pandas as pd
import numpy as np
import time
from selenium import webdriver


def ExtractZoneY(qualif):
    try:
        for i in qualif:
            if i['type']['displayName']=='PassEndY': 
                return (np.round(float(i['value'])/20,0))
            else: 
                edd=0
    except:
        return 0
    
def ExtractZoneX(qualif):
    try:
        for i in qualif:
            if i['type']['displayName']=='PassEndX':
                return (np.round(float(i['value'])/20,0))
            else: 
                edd=0
    except:
        return 0

def GetStatsTable(ids,driver):        
    url='http://www.whoscored.com/Matches/'+str(ids)+'/Live'
    try:
        driver.get(url)
    except:
        time.sleep(0.5)
        driver.get(url)
    result = driver.execute_script('return matchCentreData')
    # driver.quit()
    match_stats=pd.DataFrame(index=range(1,95))


    s = pd.Series(result['away']['stats']['ratings'], name='ratings Away')
    s.index=s.index.astype(int)
    match_stats['Ratings_A']=s
    match_stats['Ratings_A']=match_stats['Ratings_A'].fillna(method='ffill')
    t = pd.Series(result['home']['stats']['ratings'], name='ratings Home')
    t.index=t.index.astype(int)
    match_stats['Ratings_H']=t
    match_stats['Ratings_H']=match_stats['Ratings_H'].fillna(method='ffill')

    # Substitutions, Cards counting
    subs=pd.DataFrame(index=range(0,95),columns=['subs_h','subs_a','yellow_h','yellow_a','red_h','red_a'])
    sh=0
    sa=0
    yh=0
    ya=0
    rh=0
    ra=0
    for evt in result['home']['incidentEvents']:
        min_evt=min(94,evt['minute'])
        if evt['type']['displayName']=='SubstitutionOn':
            sh=sh+1
            subs.loc[min_evt]['subs_h']=sh
        else:
            if evt['type']['displayName']=='Card':
                if evt['cardType']['displayName']=='Yellow':
                    yh=yh+1
                    subs.loc[min_evt]['yellow_h']=yh
                else:
                    rh=rh+1
                    subs.loc[min_evt]['red_h']=rh
            else:
                zz=0
        
    for evt in result['away']['incidentEvents']:
        min_evt=min(94,evt['minute'])
        if evt['type']['displayName']=='SubstitutionOn':
            sa=sa+1
            subs.loc[min_evt]['subs_a']=sa
        else:
            if evt['type']['displayName']=='Card':
                if evt['cardType']['displayName']=='Yellow':
                    ya=ya+1
                    subs.loc[min_evt]['yellow_a']=ya
                else:
                    ra=ra+1
                    subs.loc[min_evt]['red_h']=ra
            else:
                zz=0
    subs=subs.fillna(method='ffill').fillna(0)
    # aggregate and transform features
    subs['Sum_subs']=subs['subs_a']+subs['subs_h']
    subs['A-H_subs']=subs['subs_a']-subs['subs_h']
    subs['Sum_yellow']=subs['yellow_a']+subs['yellow_h']
    subs['A-H_yellow']=subs['yellow_a']-subs['yellow_h']
    subs['Sum_red']=subs['red_a']+subs['red_h']
    subs['A-H_red']=subs['red_a']-subs['red_h']
    subs['Subs_10m']=subs['Sum_subs']-subs['Sum_subs'].shift(10)
    subs['A-H_Subs_10m']=subs['A-H_subs']-subs['A-H_subs'].shift(10)
    subs=subs.drop(['subs_h','subs_a','yellow_h','yellow_a','red_h','red_a'],axis=1)
        
    match_stats=match_stats.join(subs)
        
    #Shots Statistics
    try:
        s = pd.Series(result['home']['stats']['shotsTotal'],name='Shots Home')
        s.index=s.index.astype(int)
        match_stats['Shots_H']=s
    except:
        match_stats['Shots_H']=0
    match_stats['Shots_H']=match_stats['Shots_H'].fillna(0).cumsum()
    try:
        s = pd.Series(result['away']['stats']['shotsTotal'],name='Shots Away')
        s.index=s.index.astype(int)
        match_stats['Shots_A']=s
    except:
        match_stats['Shots_A']=0
    match_stats['Shots_A']=match_stats['Shots_A'].fillna(0).cumsum()
    try:
            
        s = pd.Series(result['home']['stats']['shotsOffTarget'],name='Shots Off Home')
        s.index=s.index.astype(int)
        match_stats['Shots_H_off']=s
        match_stats['Shots_H_off']=match_stats['Shots_H_off'].fillna(0).cumsum()
        match_stats['Shots_H_off']=(match_stats['Shots_H_off']/match_stats['Shots_H']).fillna(-10)
    except:
        match_stats['Shots_H_off']=0
        
    try:
        
        s = pd.Series(result['away']['stats']['shotsOffTarget'],name='Shots Off Away')
        s.index=s.index.astype(int)
        match_stats['Shots_A_off']=s
        match_stats['Shots_A_off']=match_stats['Shots_A_off'].fillna(0).cumsum()
        match_stats['Shots_A_off']=(match_stats['Shots_A_off']/match_stats['Shots_A']).fillna(-10)
    except:
        match_stats['Shots_A_off']=0
        # loading the possession of each time through time
    s = pd.Series(result['away']['stats']['possession'], name='possession Away')
    s.index=s.index.astype(int)
    match_stats['possession_A']=s
    t = pd.Series(result['home']['stats']['possession'], name='possession Home')
    t.index=t.index.astype(int)
    match_stats['possession_H']=t.fillna(0)
    s = pd.Series(result['away']['stats']['touches'], name='touches Away')
    s.index=s.index.astype(int)
    match_stats['touches_A']=s.fillna(0)
    t = pd.Series(result['home']['stats']['touches'], name='touches Home')
    t.index=t.index.astype(int)
    match_stats['touches_H']=t.fillna(0)
    match_stats[['touches_A','touches_H']]=match_stats[['touches_A','touches_H']].fillna(0)
    match_stats[['possession_A','possession_H']]=match_stats[['possession_A','possession_H']].fillna(0)

    try:
        s = pd.Series(result['away']['stats']['foulsCommited'], name='foulsCommited Away')
        s.index=s.index.astype(int)
        match_stats['foulsCommited_A']=s.fillna(0)
    except:
        match_stats['foulsCommited_A']=0
    try:
        t = pd.Series(result['home']['stats']['foulsCommited'], name='foulsCommited Home')
        t.index=t.index.astype(int)
        match_stats['foulsCommited_H']=t.fillna(0)
    except:
        match_stats['foulsCommited_H']=0

    try:
        s = pd.Series(result['away']['stats']['interceptions'], name='interceptions Away')
        s.index=s.index.astype(int)
        match_stats['interceptions_A']=s.fillna(0)
    except:
        match_stats['interceptions_A']=0
    try:
        t = pd.Series(result['home']['stats']['interceptions'], name='interceptions Home')
        t.index=t.index.astype(int)
        match_stats['interceptions_H']=t.fillna(0)     
    except:
        match_stats['interceptions_H']=0

    s = pd.Series(result['away']['stats']['passesAccurate'], name='passesAccurate Away')
    s.index=s.index.astype(int)
    match_stats['passesAccurate_A']=s.fillna(0)
    t = pd.Series(result['home']['stats']['passesAccurate'], name='passesAccurate Home')
    t.index=t.index.astype(int)
    match_stats['passesAccurate_H']=t.fillna(0)
    match_stats[['passesAccurate_A','passesAccurate_H']]=match_stats[['passesAccurate_A','passesAccurate_H']].fillna(0)

    try:
        s = pd.Series(result['away']['stats']['clearances'], name='clearances Away')
        s.index=s.index.astype(int)
        match_stats['clearances_A']=s.fillna(0)
    except:
        match_stats['clearances_A']=0
    try:
        t = pd.Series(result['home']['stats']['clearances'], name='clearances Home')
        t.index=t.index.astype(int)
        match_stats['clearances_H']=t.fillna(0)
    except:
         match_stats['clearances_H']=0
    match_stats[['clearances_A','clearances_H']]=match_stats[['clearances_A','clearances_H']].fillna(0)


    s = pd.Series(result['away']['stats']['aerialsWon'], name='aerialsWon Away')
    s.index=s.index.astype(int)
    match_stats['aerialsWon_A']=s.fillna(0)
    t = pd.Series(result['home']['stats']['aerialsWon'], name='aerialsWon Home')
    t.index=t.index.astype(int)
    match_stats['aerialsWon_H']=t.fillna(0)
    match_stats[['aerialsWon_A','aerialsWon_H']]=match_stats[['aerialsWon_A','aerialsWon_H']].fillna(0)


    # creating the formations

    forma=pd.DataFrame(index=range(0,95),columns=['Forma_h','Forma_a'])

    for x in result['home']['formations']:
        minute=x['startMinuteExpanded']
        forma['Forma_h'].loc[minute]=x['formationId']

    for x in result['away']['formations']:
        minute=x['startMinuteExpanded']
        forma['Forma_a'].loc[minute]=x['formationId']

    forma=forma.fillna(method='ffill')

    match_stats=match_stats.join(forma)

    # Other Metrics

        #match_stats['Weather']=result['weatherCode']
    match_stats['Away_age']=float(result['away']['averageAge'])
    match_stats['Home_age']=float(result['home']['averageAge'])

    sco=pd.DataFrame(index=range(0,95),columns=['Home Score'])
    sco.loc[0]=0

    ini_score=0
    home_id=result['home']['teamId']
    away_id=result['away']['teamId']

    for x in result['events']:
        minute=x['minute']
        try:
            if x['isGoal']==True:
                if x['teamId']==home_id:
                    ini_score=ini_score+1
                else:
                    ini_score=ini_score-1
                sco['Home Score'].loc[minute]=ini_score
        except:
            h=1+1

        # Creation of the goal series
    sco=sco.fillna(method='ffill')
    # merge with the result table
    match_stats['Home_id']=home_id
    match_stats['Away_id']=away_id
    match_stats=match_stats.join(sco)

    # Transformations

    match_stats['A-H']=match_stats['Ratings_A']-match_stats['Ratings_H']
    match_stats['A-H 5 minutes']=match_stats['A-H']-match_stats['A-H'].shift(5)
    match_stats['A-H 5 minutes']=match_stats['A-H 5 minutes'].fillna(0)
    match_stats['A-H 10 minutes']=match_stats['A-H']-match_stats['A-H'].shift(10)
    match_stats['A-H 10 minutes']=match_stats['A-H 10 minutes'].fillna(0)
    match_stats['A-H 1 minutes']=match_stats['A-H']-match_stats['A-H'].shift(1)
    match_stats['A-H 1 minutes']=match_stats['A-H 1 minutes'].fillna(0)

    match_stats['Poss A%']=100*(match_stats['possession_A']/(match_stats['possession_A']+match_stats['possession_H']))

    match_stats['Possession A 5 minutes']=100*(match_stats['possession_A'].rolling(window=5).sum()/(match_stats['possession_A'].rolling(window=5).sum()+match_stats['possession_H'].rolling(window=5).sum()))
    match_stats['Possession A 10 minutes']=100*(match_stats['possession_A'].rolling(window=10).sum()/(match_stats['possession_A'].rolling(window=10).sum()+match_stats['possession_H'].rolling(window=10).sum()))
    match_stats['Touch A-H']=match_stats['touches_A']-match_stats['touches_H']
    match_stats['Touch A-H 5 minutes']=match_stats['Touch A-H'].rolling(window=5).mean()
    match_stats['Touch A-H 10 minutes']=match_stats['Touch A-H'].rolling(window=10).mean()
    match_stats['Touch A-H 3 minutes']=match_stats['Touch A-H'].rolling(window=3).mean()
    
    match_stats['Away age diff']=match_stats['Away_age']-match_stats['Home_age']
    match_stats['intercept A-H']=match_stats['interceptions_A']-match_stats['interceptions_H']
    match_stats['intercept A-H 5 minutes']=match_stats['intercept A-H'].rolling(window=5).mean()
    match_stats['intercept A-H 10 minutes']=match_stats['intercept A-H'].rolling(window=10).mean()
    match_stats['intercept A-H 3 minutes']=match_stats['intercept A-H'].rolling(window=3).mean()

    match_stats['passesAccurate_A-H']=(match_stats['passesAccurate_A']-match_stats['passesAccurate_H'])/(match_stats['passesAccurate_A']+match_stats['passesAccurate_H'])
    match_stats['passesAccurate_A-H 5m']=(match_stats['passesAccurate_A'].rolling(window=5).sum()-match_stats['passesAccurate_H'].rolling(window=5).sum())/(match_stats['passesAccurate_A'].rolling(window=5).sum()+match_stats['passesAccurate_H'].rolling(window=5).sum())
    match_stats['passesAccurate_A-H 10m']=(match_stats['passesAccurate_A'].rolling(window=10).sum()-match_stats['passesAccurate_H'].rolling(window=10).sum())/(match_stats['passesAccurate_A'].rolling(window=10).sum()+match_stats['passesAccurate_H'].rolling(window=10).sum())

    match_stats['clearances A-H']=match_stats['clearances_A']-match_stats['clearances_H']
    match_stats['clearances A-H 5 minutes']=match_stats['clearances A-H'].rolling(window=5).mean()
    match_stats['clearances A-H 10 minutes']=match_stats['clearances A-H'].rolling(window=10).mean()
    match_stats['clearances A-H 3 minutes']=match_stats['clearances A-H'].rolling(window=3).mean()

    match_stats['aerialsWon A-H']=match_stats['aerialsWon_A']-match_stats['aerialsWon_H']
    match_stats['AerialsWon A-H 5 minutes']=match_stats['aerialsWon A-H'].rolling(window=5).mean()
    match_stats['AerialsWon A-H 10 minutes']=match_stats['aerialsWon A-H'].rolling(window=10).mean()
    match_stats['AerialsWon A-H 3 minutes']=match_stats['aerialsWon A-H'].rolling(window=3).mean()

    match_stats['Shots A-H']=match_stats['Shots_A']-match_stats['Shots_H']
    match_stats['Shots A-H 5 minutes']=match_stats['Shots A-H']-match_stats['Shots A-H'].shift(5)
    match_stats['Shots A-H 10 minutes']=match_stats['Shots A-H']-match_stats['Shots A-H'].shift(10)
    match_stats['Shots A-H 3 minutes']=match_stats['Shots A-H']-match_stats['Shots A-H'].shift(3)
        
    match_stats['Shots A+H']=match_stats['Shots_A']+match_stats['Shots_H']
    match_stats['Shots A+H 5 minutes']=match_stats['Shots A+H']-match_stats['Shots A+H'].shift(5)
    match_stats['Shots A+H 10 minutes']=match_stats['Shots A+H']-match_stats['Shots A+H'].shift(10)
    match_stats['Shots A+H 3 minutes']=match_stats['Shots A+H']-match_stats['Shots A+H'].shift(3)
        
    match_stats['minutes']=match_stats.index
    match_stats['match_id']=int(ids)
        
    evt=pd.DataFrame(result['events'])[['minute','second','qualifiers']]
    evt['ZoneX']=evt['qualifiers'].apply(ExtractZoneX).fillna(0)
    evt['ZoneY']=evt['qualifiers'].apply(ExtractZoneY).fillna(0)
    evt['Totalsec']=evt['minute']*60+evt['second']
    evt['TimeSpent']=(evt['Totalsec']-evt['Totalsec'].shift(1)).fillna(0).clip(0,100)
    evtx=pd.pivot_table(data=evt,index='minute',columns=['ZoneX'],values=['TimeSpent'],aggfunc='sum').fillna(0)
    #print(evtx)
    evt1=evtx.rolling(window=5).sum()
    evt1.columns=[['X0 5min','X1 5min','X2 5min','X3 5min','X4 5min','X5 5min']]
    evt2=evtx.rolling(window=3).sum()
    evt2.columns=[['X0 3min','X1 3min','X2 3min','X3 3min','X4 3min','X5 3min']]
    evt3=evtx.rolling(window=10).sum()
    evt3.columns=[['X0 10min','X1 10min','X2 10min','X3 10min','X4 10min','X5 10min']]
        
    evty=pd.pivot_table(data=evt,index='minute',columns=['ZoneY'],values=['TimeSpent'],aggfunc='sum').fillna(0)
    evty1=evty.rolling(window=5).sum()
    evty1.columns=[['Y0 5min','Y1 5min','Y2 5min','Y3 5min','Y4 5min','Y5 5min']]
    evty2=evty.rolling(window=3).sum()
    evty2.columns=[['Y0 3min','Y1 3min','Y2 3min','Y3 3min','Y4 3min','Y5 3min']]
    evty3=evty.rolling(window=10).sum()
    evty3.columns=[['Y0 10min','Y1 10min','Y2 10min','Y3 10min','Y4 10min','Y5 10min']]
    match_stats=match_stats.join(evty1).join(evt1).join(evt2).join(evt3).join(evty2).join(evty3)
    #print(match_stats)    
    match_stats=match_stats.fillna(0)
    match_stats.index=match_stats['minutes']
    return match_stats

defensive={2:1,3:0,4:1,5:-1,6:0,7:0,8:0,9:0,10:-1,11:0,12:1,13:0,14:0,15:1,16:1,17:0,18:1,19:0,20:1,21:0,22:-1,23:0,24:-1,25:0}
offensive={2:1,3:1,4:1,5:-1,6:-1,7:0,8:1,9:1,10:-1,11:-1,12:0,13:1,14:-1,15:1,16:1,17:0,18:1,19:1,20:1,21:-1,22:0,23:0,24:1,25:1}
def Defensive(forma):
    return defensive[forma]

def Offensive(forma):
    return offensive[forma]