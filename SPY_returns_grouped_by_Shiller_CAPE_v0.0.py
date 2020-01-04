import pandas as pd
import numpy as np
from scipy.stats import skew 
from datetime import datetime

shiller = pd.DataFrame(pd.read_csv('/home/david/Desktop/Market_research/CAPE_7_2019.csv', header = 7))
#shiller.to_csv('/home/david/Desktop/Market_research/shiller_CLEAN.csv')

shiller['Date'] = pd.to_datetime(shiller['Date']*100, format='%Y%m')

shiller['Date'] = shiller['Date'].dt.strftime('%Y-%m')

#drop last col
shiller.drop(columns = 'Unnamed: 14', inplace = True, axis = 1)

shiller = shiller[~np.isnan(shiller['CAPE.1']) ]

shiller['P'] = shiller['P'].astype(float)
shiller['CAPE.1'] = shiller['CAPE.1'].astype(float)

max = 0
ath_list = []
for point in shiller.index:
    if shiller['P'][point] > max:
        max = shiller['P'][point]
        ath_list.append(shiller['Date'][point])

# Now calculate returns after N days
N_day_array = np.arange(1, 25, 1)
CAPE_array = np.arange(29, 42, 1)


def ret_calc(df, prior_date, later_date):
    prior_price = df.loc[df['Date'] == prior_date]['P']
    later_price = df.loc[df['Date'] == later_date]['P']
    return( ( np.array(later_price) / np.array(prior_price)  )[0] - 1) 

return_df = pd.DataFrame()
    
for date in shiller['Date']:
    # We start going through CAPE values
    return_array = {'Date' : date}
    
    for number in CAPE_array:
        
        if np.array(shiller.loc[shiller['Date'] == date]['CAPE.1'])[0] >= number:
        
            # We starting going through month values
            for val in N_day_array:
                index_val_days_later = np.array(shiller.loc[shiller['Date'] == date].index)[0] + val
                
                new_item_name = 'CAPE='+ str(number) + '_' + str(val) + '_month_return'
                
                try:
                    date_val_days_later = shiller['Date'].iloc[index_val_days_later]
                    return_array.update({ new_item_name : ret_calc(shiller, date, date_val_days_later)}) 
                    
                except:
                    return_array.update({ new_item_name : np.NaN}) 
                
    return_df = return_df.append(return_array, ignore_index = True)
        
return_df = round(return_df, 4)
return_df.set_index('Date',inplace=True)

col_names = []
for number in CAPE_array:
    for val in N_day_array:
        col_names.append('CAPE='+ str(number) + '_' + str(val) + '_month_return')
return_df.columns = col_names

# now get means and variances
for col in return_df:
    mu = str(round(np.mean(return_df[col]),3))  
    sd = str(round(np.std(return_df[col]),3))  
    med = str(round(np.median(return_df[col].dropna()),3)) 
    left = str(round(np.mean(return_df[col]) - np.std(return_df[col]), 3))
    right = str(round(np.mean(return_df[col]) + np.std(return_df[col]),3))
    print(col + " has mean of " + mu + "; CI = (" + left + "," + right + "):" + "med = " + med)
    
desc = return_df.describe()

return_df.to_csv('/home/david/Desktop/Market_research/return_df.csv')

# Let's broaden the dataframe so we get returns for months = 1, 2,...24
ld = np.log(shiller['P']).diff()

for month in range(1,25):
    colname = str(month) + '_month_ret'
    null = []
    for i in range(0, month - 1):
        null.append(np.nan)
    null = pd.Series(null)
    add = ld[:-month]
    shiller[colname] = null.append(add, ignore_index = True)
 