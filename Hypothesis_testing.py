import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.



# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''

    file = open('university_towns.txt','r')
    content = file.read().splitlines()

    university_towns = pd.DataFrame(columns = ['State','RegionName'])

    i = 0
    for item in content:
        if '[edit]' in item:
            state = item.replace('[edit]','') 
        else:
            town = item
            if '(' in town:
                town = town[:town.index(' (')]
            if '[' in town:
                town = town[:town.index('[')]
            university_towns.loc[i] = [state , town]
            i += 1
    return university_towns


def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    
    gdp = pd.read_excel('gdplev.xls', skiprows = 5)
    gdp = gdp[['Unnamed: 4','GDP in billions of chained 2009 dollars.1']].iloc[214:,:]
    gdp = gdp.rename(columns = {'Unnamed: 4':'Quarter'}).set_index('Quarter')


    change = [None]
    for i in range(1,len(gdp)):
        if (float(gdp.iloc[i]) - float(gdp.iloc[i-1])) > 0:
            change.append(1)
        else:
            if change[-1] == 0:
                start = gdp.index[i-1]
                break
            change.append(0)

    return start


def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''


    gdp = pd.read_excel('gdplev.xls', skiprows = 5)
    gdp = gdp[['Unnamed: 4','GDP in billions of chained 2009 dollars.1']].iloc[214:,:]
    gdp = gdp.rename(columns = {'Unnamed: 4':'Quarter'}).set_index('Quarter')


    change = [None]
    for i in range(1,len(gdp)):
        if (float(gdp.iloc[i]) - float(gdp.iloc[i-1])) > 0:
            change.append(1)
        else:
            change.append(0)

    gdp['Change'] = change
    start = get_recession_start()
    new = gdp.loc[start:]

    for i in range(1,len(new)):
        if int(new.iloc[i][1]) == 1 and int(new.iloc[i-1][1]) == 1:
            end = new.index[i]
            break

    return end


def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''


    gdp = pd.read_excel('gdplev.xls', skiprows = 5)
    gdp = gdp[['Unnamed: 4','GDP in billions of chained 2009 dollars.1']].iloc[214:,:]
    gdp = gdp.rename(columns = {'Unnamed: 4':'Quarter'}).set_index('Quarter')


    change = [None]
    for i in range(1,len(gdp)):
        if (float(gdp.iloc[i]) - float(gdp.iloc[i-1])) > 0:
          change.append(1)
        else:
            change.append(0)
    gdp['Change'] = change
    gdp = gdp.loc[get_recession_start():get_recession_end()]
    return gdp['GDP in billions of chained 2009 dollars.1'].idxmin()


def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    
    df = pd.read_csv('City_Zhvi_AllHomes.csv')
    sth = list(df.columns)[6:51]
    df = df.drop(sth, axis = 1)
    df = df.rename(columns = {'State':'StateName'})
    df['State'] = df['StateName'].map(states)
    df = df.drop(['RegionID','Metro','CountyName','SizeRank','StateName'],axis = 1)
    df = df.set_index(['State','RegionName']).sort_index()



    sth = pd.read_excel('gdplev.xls', skiprows = 5)
    sth = sth.iloc[214:,4:5]
    sth = list(sth['Unnamed: 4'])

    i = 0
    for item in sth:
        df[item] = df.iloc[:,i:i+3].mean(axis = 1)
        i += 3
    df['2016q3'] = (df['2016-07'] + df['2016-08']) / 2
    sth = list(df.columns)[0:200]
    df = df.drop(sth,axis = 1)
    return df


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    

    unitowns = get_list_of_university_towns()
    unitowns = unitowns.set_index(['State','RegionName'])

    housing_data = convert_housing_data_to_quarters()
    start = get_recession_start()
    bottom = get_recession_bottom()
    
    x = housing_data.columns[list(housing_data.columns).index(start)-1] #Year Before Recession Start
    y = bottom #Year with lowest GDP during Recession

    housing_data['PriceRatio'] = housing_data[x] / housing_data[y]
    housing_data = pd.DataFrame(housing_data['PriceRatio'])

    U_towns = pd.merge(unitowns, housing_data, how = 'inner', left_index = True, right_index = True)
    NU_towns = housing_data.drop(U_towns.index)

    if NU_towns['PriceRatio'].mean() < U_towns['PriceRatio'].mean():
        better = 'non-university town'
    else:
        better = 'university town'

    res = ttest_ind(U_towns['PriceRatio'].dropna(),NU_towns['PriceRatio'].dropna())
    if res[1] < 0.01:
        ans = (True,res[1],better)
    else:
        ans = (False,res[1],better)

    return ans


print(run_ttest())