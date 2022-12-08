import pandas as pd 
import numpy as np 
import requests
import json  
from bs4 import BeautifulSoup
import re
from typing import List
import pysbr as sbr
from datetime import datetime
import ast
import dateutil.parser as dp


class BettingOdds():
    def __init__(self,api_key):
        self.api_key = api_key
    def list_of_sports(self)->json:
        in_season_sports = requests.get("https://api.the-odds-api.com/v4/sports?apiKey="+self.api_key)
        in_season_sports = ast.literal_eval(str(in_season_sports.text).replace('\n','').replace(':false',':False').replace(':true',':True'))
        return in_season_sports
    
    def get_odds_for_sport(self,sport:str)->json:
        odds = requests.get("https://api.the-odds-api.com/v4/sports/{}/odds/?regions=us&oddsFormat=american&apiKey={}".format(sport,self.api_key))
        return ast.literal_eval(odds.text) 
    def _reform_dict(self,nested_dict:json):
        reformed_dict = {}
        for outerKey, innerDict in nested_dict.items():
            for innerKey, centerDict in innerDict.items():
                for centralKey,values in centerDict.items():
                    reformed_dict[(outerKey,innerKey,centralKey)] = values
        return reformed_dict
        
    def _get_usefull_stats(self,data:json)-> pd.DataFrame:
        id = data['id']
        bookMakers = data['bookmakers']
        date = data['commence_time']
        dict_data = {}
        dict_data[id] = {date:{}}
        company_list = []
        for book in bookMakers:
            company_list.append(book['title'])
            for outcome in book['markets'][0]['outcomes']:
                dict_data[id][date].setdefault(outcome['name'],[]).append(outcome['price'])
        return dict_data,company_list
        
    def _format_all_odds(self,odds:list)->pd.DataFrame:
        odds_storage = []
        for odd in odds:
            odds_dic,company_names = self._get_usefull_stats(odd)
            odds_dic = self._reform_dict(odds_dic)
            temp_df = pd.DataFrame(odds_dic).T 
            temp_df.columns = company_names 
            odds_storage.append(temp_df)
        all_odds = pd.concat(odds_storage)
        all_odds.index = all_odds.index.set_levels([all_odds.index.levels[0],pd.to_datetime(list(map(lambda x: x.strftime('%Y-%m-%d %H:%M'),pd.to_datetime(all_odds.index.levels[1])))),all_odds.index.levels[2]])
        return all_odds

    def convert_to_dec(self,odds:pd.DataFrame):
        odds = odds.applymap(lambda x: round(1+(x/100),2) if x>0 else round((100/abs(x))+1,2) )
        return odds

    def convert_to_prob(self,odds:pd.DataFrame):
        odds = odds = odds.applymap(lambda x: 1+(x/100) if x>0 else (100/abs(x))+1 )
        return round(1/odds*100,2)


    def odds_for_sport(self,sport:str)->pd.DataFrame:
        odds_for_specific_sport = self.get_odds_for_sport(sport)
        all_odds = self._format_all_odds(odds_for_specific_sport)

        dec_odds = self.convert_to_dec(all_odds).fillna(np.nan)
        prob_odds = self.convert_to_prob(all_odds).fillna(np.nan)
        return all_odds,dec_odds,prob_odds

    def find_arbs(self,prob_odds:pd.DataFrame)-> pd.DataFrame:
        indexes = prob_odds.index.levels[0]
        companies = prob_odds.columns.tolist()
        combined_arbs = []
        for ind in indexes:
            ind_level_two = prob_odds.loc[ind].index 
            probabilities = []
            prob_col = []
            prob_dics = []
            for level_two in ind_level_two:
                temp_prob = prob_odds.loc[ind].loc[level_two].min()
                prob_col_ind = prob_odds.loc[ind].loc[level_two].tolist().index(temp_prob)
                probabilities.append(temp_prob)
                d = dict()
                level_two = [i for i in level_two]
                d[(ind,level_two[0],level_two[1])] = [temp_prob]
                prob_dics.append(d)
                prob_col.append(prob_col_ind)
            if sum(probabilities) < 100: 
                prob_dics = [pd.DataFrame(i).T for i in prob_dics]
                for i in range(len(prob_col)):
                    prob_dics[i].columns = [companies[prob_col[i]]] 
                prob_dics = pd.concat(prob_dics)
                combined_arbs.append(prob_dics)
        if not combined_arbs:
            return "No Arbitrages Found"
        combined_arbs = pd.concat(combined_arbs)
        return combined_arbs 
    def calculate_each_leg(self,df:pd.DataFrame)->pd.DataFrame:
        df['bet_size_%']= df.sum(axis = 1)
        df = df.fillna("") 
        arbitrages = df.index.levels[0]
        all_bets = []
        for arb in arbitrages:
            temp_df = df.loc[arb]
            edge = temp_df.sum(axis =1).sum()
            temp_df['bet_size_%'] = temp_df['bet_size_%'].apply(lambda x: round(x/edge,2))
            all_bets.append(temp_df)
        return pd.concat(all_bets)
        
# odds = BettingOdds("Your api key goes here")
# all_ods,dec_odds, prob_odds  = odds.odds_for_sport("soccer_fifa_world_cup")
# arbs = odds.find_arbs(prob_odds)
# arbs.fillna("")
