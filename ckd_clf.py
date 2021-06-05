# -*- coding: utf-8 -*-
"""
Created on Sat Jun  5 16:44:48 2021

@author: Zuzia
"""

import pandas as pd
import numpy as np
from sklearn.impute import IterativeImputer
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.ensemble import GradientBoostingClassifier

pd.set_option('display.max_columns', 25)
pd.set_option('display.max_rows', None)
#loading data 
data = pd.read_csv('chronic_kidney_disease_full.csv')
df = pd.DataFrame(data)
#df1 = df.drop(columns='class')
df.head()

#replacing '?' with NaN
def replace(data):
    data.replace('?', np.nan, inplace=True)
    return data
df = replace(df)

#plotting outliars
def plot_boxplot(df, col):
    data=df[col].dropna().values
    data = data.astype('float64')

    q25= np.percentile(data, 25)
    q50 = np.percentile(data, 50)
    q75 = np.percentile(data, 75)
    iqr = q75 - q25

    cut_off = iqr * 1.5
    lower_limit, upper_limit = q25 - cut_off, q75 + cut_off
    print( np.min(data), lower_limit, q25, q50, q75, upper_limit, np.max(data))
    print( np.mean(data), np.std(data), np.median(data))
    fig, ax = plt.subplots(figsize=(9,6))
    sns.boxplot(ax=ax, x=data)
    
plot_boxplot(df, "sod")
plot_boxplot(df, "pot")

#deleting outliars based on boxplots
indexNamesOut = df[ (df['sod'] == "4.5") | (df['pot'] == "47") | (df['pot'] == "39")].index
df.drop(indexNamesOut , inplace=True)
df = df.reset_index()
df = df.drop(columns='index')




#deleting rows where nan values is greater than 6 
def delete(data):
    dropval = data.isnull().sum(axis=1)
    data = data.drop(data[dropval>6].index)
    data = data.reset_index()
    data = data.drop(columns='index')
    return data
df = delete(df)

#nominal data to numerical
mapping1 = {'normal' : 0, 'abnormal' : 1}
mapping2 = {'notpresent' : 0, 'present' : 1}
mapping3 = {'good' : 0, 'poor': 1}
mapping4 = {'no' : 0, 'yes' : 1}
mapping5 = {'notckd' : 0, 'ckd' : 1}
mapping6 = {'1.005': 1, '1.010' : 2, '1.015' : 3, '1.020' : 4, '1.025' : 5}

def label_decode(df, labels, mapping):
    #Map values using the mapping dictionary
    df_result = df.copy()
    df_result[labels] = df_result[labels].replace(mapping)
    return df_result

df = label_decode(df, 'rbc', mapping1)
df = label_decode(df, 'pc', mapping1)
df = label_decode(df, 'pcc', mapping2)
df = label_decode(df, 'ba', mapping2)
df = label_decode(df, 'htn', mapping4)
df = label_decode(df, 'dm', mapping4)
df = label_decode(df, 'cad', mapping4)
df = label_decode(df, 'appet', mapping3)
df = label_decode(df, 'pe', mapping4)
df = label_decode(df, 'ane', mapping4)
df = label_decode(df, 'class', mapping5)
df = label_decode(df, 'sg', mapping6)

#the imputation process was based on linear regression for predicting continuous variables 
#logistic regression for categorical variables
imputer_one = IterativeImputer(estimator = LogisticRegression(), max_iter=10)
imputer_two = IterativeImputer(estimator = LinearRegression(), max_iter=10)
df_cont = df[['age','bp','bgr','bu','sc','sod','pot','hemo','pcv','wbcc','rbcc']]
df_cat = df[['sg','al','su','rbc','pc','pcc','ba','htn','dm','cad','appet','pe','ane']]
df_class = df[['class']]

cont = pd.DataFrame(imputer_two.fit_transform(df_cont),columns = ['age','bp','bgr','bu','sc','sod','pot','hemo','pcv','wbcc','rbcc'])
cat = pd.DataFrame(imputer_one.fit_transform(df_cat),columns =['sg','al','su','rbc','pc','pcc','ba','htn','dm','cad','appet','pe','ane'])

result = pd.concat([cont, cat, df_class], axis=1)
result.age = result.age.astype(int)
result.bp = result.bp.astype(int)
result.sg = result.sg.astype(int)
result.al = result.al.astype(int)
result.su = result.su.astype(int)
result.rbc = result.rbc.astype(int)
result.pc = result.pc.astype(int)
result.pcc = result.pcc.astype(int)
result.ba = result.ba.astype(int)
result.htn = result.htn.astype(int)
result.dm = result.dm.astype(int)
result.cad = result.cad.astype(int)
result.appet = result.appet.astype(int)
result.pe = result.pe.astype(int)
result.ane = result.ane.astype(int)
result.wbcc = result.wbcc.astype(int)
result.sod = result.sod.astype(int)
result.bgr = result.bgr.astype(int)
result.pcv = result.pcv.astype(int)

#pearson correlation
def correlation(data, col1, col2, xlim1, xlim2):
    corr_one = data[col1].corr(data[col2], method='pearson')
    print(corr_one)
    g=sns.lmplot(x=col1, y=col2, data=data)
    g = (g.set(xlim=(xlim1, xlim2)))
    
ready_df = result.drop(['bgr', 'bp', 'pcv', 'rbcc', 'rbc', 'ane', 'su', 'pc', 'bu'], axis = 1)

ready_df = result.drop(columns='class')
df_class = result[['class']]

#splitting the columns to normalize some of them
df_not_normalize = ready_df[['age','sg','al','pcc','ba','htn','dm','cad','appet','pe']]
df_normalize = ready_df[['sc','sod','pot','hemo','wbcc']]
# create an abs_scaler object
scaler = MinMaxScaler()
# fit and transform the data
df_norm = pd.DataFrame(scaler.fit_transform(df_normalize), columns=df_normalize.columns)

df_res = pd.concat([df_not_normalize, df_norm], axis=1)

