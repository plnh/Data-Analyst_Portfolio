import pandas as pd
import matplotlib.pyplot as plt
import os
import openpyxl 
import numpy as np
from datetime import datetime, timedelta
import sys
import importlib
from utils.connection import get_conn,tryConnect
from utils.configurations import loadConfig
importlib.invalidate_caches()
import re

#----------Functions--------------
#Read/Clean Gross/Net Revenue
def clean_Rev(path, type):
    
    #Create dataframe to store the files
    combined_df = pd.DataFrame()
    
    #Rergular expression to get all folders with 2023 and above
    pattern = r'\b(202[3-9]|20[3-9]\d|2[1-9]\d{2}|[3-9]\d{3})\b'
    
    #Loop through the folders and get the folders with 2023 and above
    for folder in os.listdir(path):
        if re.search(pattern, folder):
            folder_path = os.path.join(path, folder)
            if os.path.isdir(folder_path):  
                for filename in os.listdir(folder_path):
                    if filename.endswith('xlsx'):
                        file_path = os.path.join(folder_path, filename)
                        excel_file = pd.ExcelFile(file_path)
                        for sheet_name in excel_file.sheet_names:
                            #Read every sheet in the excel
                            df = pd.read_excel(file_path, sheet_name=sheet_name).astype(str)
                            
                            if type == 'G':
                                    
                                if len(df.columns) < 12:
                                    
                                    df.columns = ["Empty","Entity","Period","Account","PC","Entity Name","Sales Type",'Products','Currency','Plan','ACT']
                                    #Unpivot the tables
                                    df = pd.melt(df, id_vars=["Empty","Entity","Period","Account","PC","Entity Name","Sales Type",'Products','Currency'], var_name='Version', value_name='Amount')
                                    
                                else:
                                    
                                    df.columns = ["Empty","Entity","Period","Account","PC","Entity Name","Sales Type",'Products','Currency','Plan','FCST','ACT']
                                    
                                    #Unpivot the tables
                                    df = pd.melt(df, id_vars=["Empty","Entity","Period","Account","PC","Entity Name","Sales Type",'Products','Currency'], var_name='Version', value_name='Amount')

                                
                                #Add 'Period' Column
                                df['Period'] = filename[8:12] + "20" + filename[12:14]
                            
            
                                # Drop rows based on specific criteria
                                df = df.drop(df[(df['Products'] == "AMA Kits") | (df['Entity'] == "E.4000") | (df['Entity'] == "ENTITY")
                                                | (df['Entity'] == "E.4016") | (df['Entity'] == "nan") | (df['Amount'] == "nan")].index)
                                
                                
                                # Modify the "Entity" column to get Netherlands international sales
                                df["Entity"] = np.where((df["Entity"] == "E.4004") & (df["Sales Type"] == "Sales Revenue - International"),'E.4099',df["Entity"])
                                
                
                                # Drop unnecessary columns
                                df = df.drop(['Empty','Entity Name',"Sales Type","Products",'Account','PC','Currency'], axis=1)
                                
                                df['Period'] = pd.to_datetime(df['Period'])
                                
                                df['Amount'] = df['Amount'].astype(float).fillna(0)
                                
                                df['Version'].replace({'Plan':'PLN'},inplace=True)
                                
                                # Append the cleaned DataFrame to the combined DataFrame
                                combined_df = pd.concat([combined_df, df], ignore_index=True)
                                
                            else:
                                #Unpivot the tables
                                df = pd.melt(df, id_vars=["Unnamed: 0"], var_name='Entity', value_name='Amount', col_level=0)
                            
                                # Drop rows based on specific criteria
                                df = df.drop(df[(df['Entity'] == "E.4000") | (df['Entity'] == "E.4016") | (df['Unnamed: 0'] == "nan")].index)
                                
                                #Rename columns
                                df.columns = ['Account', 'Entity', 'Amount']
                                
                                #change 'Amount' Column type to float
                                df['Amount'] = df['Amount'].astype(float).fillna(0)
                                
                                #Add 'Period' Column
                                df['Period'] = filename[12:16] + "20" + filename[16:18]
                                
                                #Change the type of 'Period' to date
                                df['Period'] = pd.to_datetime(df['Period'])
                                
                                #Drop 'Account' Column
                                df.drop(['Account'], axis=1, inplace=True)
                                
                                # Append the cleaned DataFrame to the combined DataFrame
                                combined_df = pd.concat([combined_df, df], ignore_index=True)

    return combined_df

#Read/Clean Gross OPEX
def clean_opex(path, type, pattern):
    combined_df = pd.DataFrame()
    for filename in os.listdir(path):
        if filename.endswith('xlsx') and re.search(pattern, filename):
            file_path = os.path.join(path, filename)
            excel_file = pd.ExcelFile(file_path)
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name).astype(str)
                
                if type == 'ACT':

                    # Filter out rows where the first column contains "ENTITY"
                    df = df[df.iloc[:, 0].str.contains("ENTITY") == False]

                    # Rename columns
                    df.columns = ["Period","Entity","Cost_center_code","Account_code","Entity Name","Func Area", 
                                "Cost Center Name","Account Name","Amount"]
                    
                    # Drop rows based on specific criteria
                    df = df.drop(df[(df['Account_code'].str.contains("A.690090")) | (df['Account_code'].str.contains("A.690045"))
                                    | (df['Account_code'].str.contains("A.610010")) | (df['Account_code'].str.contains("A.690901")) | (df['Account_code'].str.contains("A.660120"))
                                    | (df['Account_code'].str.contains("A.690900")) | (df['Account_code'].str.contains("A.630105"))
                                    | (df['Account_code'].str.contains("A.650020")) | (df['Account_code'].str.contains("A.680013"))
                                    | (df['Cost Center Name'].str.contains("Interns")) | (df['Entity'] == "E.4016") | (df['Entity'] == "E.4100")].index)

                    # Drop unnecessary columns
                    df = df.drop(["Entity Name","Func Area",'Cost Center Name','Account Name'], axis=1)

                    # Append the cleaned DataFrame to the combined DataFrame
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
                    
                    #Change the type of 'Period' to date
                    combined_df['Period'] = pd.to_datetime(combined_df['Period'])
                    
                elif type == 'FCST':
                    
                    #Unpivot the table
                    df = pd.melt(df, id_vars=["Scenario","ENTITY","COSTCENTER","ACCOUNT","ENTITY.1","Func. Area","ACCOUNT.1"], var_name='Period', value_name='Amount')

                    #Rename Columns 
                    df.columns = ['Version','Entity','Cost_center_code','Account_code','Entity Name', 'Func. Area','Account_Name','Period','Amount']

                    #Drop unneeded columns
                    df = df.drop(['Entity Name', 'Func. Area','Account_Name'], axis=1)

                    #Drop Unneeded entities
                    df = df.drop(df[(df['Account_code'].str.contains("A.690090")) | (df['Account_code'].str.contains("A.690045"))
                                                        | (df['Account_code'].str.contains("A.610010")) | (df['Account_code'].str.contains("A.690901")) 
                                                        | (df['Account_code'].str.contains("A.660120")) | (df['Account_code'].str.contains("A.690900")) 
                                                        | (df['Account_code'].str.contains("A.630105")) | (df['Account_code'].str.contains("A.650020")) 
                                                        | (df['Account_code'].str.contains("A.680013")) | (df['Entity'] == "E.4016") 
                                                        | (df['Entity'] == "E.4100") | (df['Entity'] == "E.9997")].index)
                    
                    # Append the cleaned DataFrame to the combined DataFrame
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
                    
                    #Change the type of 'Period' to date
                    combined_df['Period'] = pd.to_datetime(combined_df['Period'])
                    
                else:
                    
                    # Filter out rows where the first column contains "ENTITY"
                    df = df[df.iloc[:, 0].str.contains("Entity") == False]

                    # Rename columns
                    df.columns = ["Period","Entity","Cost_center_code","Account_code","Entity Name","Func Area", 
                                "Cost Center Name","Account Name","Amount","Currency"]
                    
                    # Drop rows based on specific criteria
                    df = df.drop(df[(df['Account_code'].str.contains("A.690090")) | (df['Account_code'].str.contains("A.690045"))
                                    | (df['Account_code'].str.contains("A.610010")) | (df['Account_code'].str.contains("A.690901")) | (df['Account_code'].str.contains("A.660120"))
                                    | (df['Account_code'].str.contains("A.690900")) | (df['Account_code'].str.contains("A.630105"))
                                    | (df['Account_code'].str.contains("A.650020")) | (df['Account_code'].str.contains("A.680013"))
                                    | (df['Cost Center Name'].str.contains("Interns")) | (df['Entity'] == "E.4016") | (df['Entity'] == "E.4100")].index)

                    # Drop unnecessary columns
                    df = df.drop(["Entity Name","Func Area",'Cost Center Name','Account Name',"Currency"], axis=1)

                    # Append the cleaned DataFrame to the combined DataFrame
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
                    
                    #Change the type of 'Period' to date
                    combined_df['Period'] = pd.to_datetime(combined_df['Period'])
            

    return combined_df

#Loads .SQL file from path and returns the query as a string
def readQueryInSQLFile(path) -> str:
    file = open(path, "r")
    query = file.read()
    file.close()
    return query

##Establish a connection to SQL1
def execute_query_sql(query):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        query = readQueryInSQLFile(query)
        cursor.execute(query)
        
        # Get the data from SQL
        sql_data = cursor.fetchall()
        
        #Define the column names
        keys =['Version', 'Entity','Period','Amount']
        
        #Convert the sql result into dictionary  
        dict_data = [dict(zip(keys, tup)) for tup in sql_data]
        
        #Put the data into a dataframe
        data = pd.DataFrame(dict_data)
        
        return data
    except Exception as e:
        print(e)

##Establish a connection to SQL3
def execute_query_sql3():
    try:
        azuresqlconfig = loadConfig()['sql3']
        conn = tryConnect(azuresqlconfig)
        query = readQueryInSQLFile("SQL\COGS.sql")

        # Get the data from SQL
        data = pd.read_sql_query(query, con=conn)
        
        data['Period'] = pd.to_datetime(data['Period'])
        
        return data
    except Exception as e:
        print(e)


#Function to get the version column 
def Version(data, text1, text2):
    
    #check if version column exists
    if "Version" in data.columns:
        
        # Extract year from 'Date' column
        data['Year'] = data['Period'].dt.year.fillna(0).astype(int)

        #Add Year to the Version Column
        if text1 == "ACT":
            data['Version'] = data.apply(lambda row: f"{text1} {row['Year']}", axis=1)
        else:
            data['Version'] = data.apply(lambda row: f"{text1} {row['Year']}" if text2 in row['Version'] else row['Version'], axis=1)

        # Drop the 'Year' column
        data = data.drop(columns=['Year'])
    
    
    else:
        data['Version'] = "NaN"
        # Extract year from 'Date' column
        data['Year'] = data['Period'].dt.year.fillna(0).astype(int)

        #Add Year to the Version Text
        data['Version'] = data.apply(lambda row: f"{text1} {row['Year']}", axis=1)

        # Drop the 'Year' column if not needed
        data = data.drop(columns=['Year'])
        
        
    return data


# Get the mapping between the OPEX and revised functional area and the cost category
def opex_config(data, text):
    
    if text == 'Account_code':
        
        #Merge the data and get the mapping for cost category based on account code
        configured_df = data.merge(Cost_categoy_mapping, how='left',on = [text])

    else:

        #Merge the data and get the mapping for revised functional area based on Cost Center Code
        configured_df = data.merge(func_area_mapping, how = 'left', on = [text])

    return configured_df

#Function to filter all data based on different criteria 
def filter(data, tuple):
    
    gross_revenue_pln_fcst = data[tuple]
    
    return gross_revenue_pln_fcst


#Function to merge the data and perform differen operations 
def merger(df1,df2,list,indicator):
    
    #Merge data based on the indicated list
    merged_df = df2.merge(df1, how = 'left', on = list)
    
    #Get the difference between amount_x and amount_y (to get the profit margin and variance VS PLN)
    if indicator == 'Y':
        
        merged_df['Amount'] = merged_df['Amount_x']-merged_df['Amount_y']
        
        #Drop unnessecary columns 
        merged_df.drop(['Amount_x','Amount_y','Version_y'], axis=1, inplace=True)
        
    #Get the %s of profit margin from the actuals 
    elif indicator == 'P':
        
        #Calculate the %s
        merged_df['Amount'] = merged_df['Amount_x']/merged_df['Amount_y']
        
        #Drop unnessecary columns 
        merged_df.drop(['Amount_x','Amount_y'], axis=1, inplace=True)
        
    #Get the difference between amount_x and amount_y (to get the profit margin amounts)
    elif indicator == 'M':
        
        merged_df['Amount'] = -merged_df['Amount_x'].fillna(0)+merged_df['Amount_y'].fillna(0)
        
        #Drop unnessecary columns 
        merged_df.drop(['Amount_x','Amount_y','Attribute_x','Attribute_y'], axis=1, inplace=True)
    
    ##Get the difference between amount_x and amount_y when one amount is negative (to get the sales discounts and net revenue)
    else:
        merged_df['Amount'] = merged_df['Amount_x'].fillna(0)+merged_df['Amount_y'].fillna(0)
        
        #Drop unnessecary columns 
        merged_df.drop(['Amount_x','Amount_y','Attribute_x','Attribute_y'], axis=1, inplace=True)
        
    return merged_df


# Get variance from plan for different data
def get_the_variance_from_plan(data, text, cond):
    
    if cond == 'OPEX':
        
        #Filter the data to ACT & FCST
        var1 = filter(data,(data['Version'].str.contains('FCST'))  | (data['Version'].str.contains('ACT')))
        
        #Filter the data to PLN
        var2 = filter(data,(data['Version'].str.contains('PLN')))
        
        # Apply the merge and operation Y
        variance = merger(var2,var1,['Period','Cost_center_code','Account_code','Attribute','Entity'],'Y')
        
        #Write the attribute that we want to indicate
        variance['Attribute'] = text
    
    else:

        #Filter the data to ACT & FCST
        var1 = filter(data,(data['Version'].str.contains('FCST'))  | (data['Version'].str.contains('ACT')))
        
        #Filter the data to PLN
        var2 = filter(data,(data['Version'].str.contains('PLN')))
        
        # Apply the merge and operation Y
        variance = merger(var2,var1,['Period','Attribute','Entity'],'Y')
        
        #Write the attribute that we want to indicate
        variance['Attribute'] = text
        
        #Rename the columns after the merge
        variance.columns = ["Period","Version",'Entity',"Attribute","Amount"]
    
    return variance

#To Calculate the COGS Forecast and Plan
def COGS_PF(data, percentage, cond):
    
    #Define an empty list
    list = []
    
    #Define a range to get the data into a dictonary based on the forecas/plan range
    for x in range(len(data['Period'][data['Version'].str.contains(cond)])):
        
        #If forecast, get the last percentage from the actuals
        if cond == 'FCST':
            amount = np.array([y * (1-percentage['Amount'][-1:]) for y in data['Amount'][data['Version'].str.contains(cond)]], dtype=float)[x][0]
            
        #If plan, get the assumed percentages_opex 
        else: 
            amount = np.array([y * percentage.iloc[x] for y in data['Amount'][data['Version'].str.contains(cond)]], dtype=float)[x]
            
        #Get the corresponding period, version, and amount in dictonary
        dict = {'Period':data['Period'][data['Version'].str.contains(cond)][0:].iloc[x],
                        'Version':data['Version'][data['Version'].str.contains(cond)][0:].iloc[x],
                        'Entity':data['Entity'][data['Version'].str.contains(cond)][0:].iloc[x],
                        'Amount':amount}
        
        #Append to the list
        list.append(dict)
        
    return list

#Mapping Dictionaries
#Currency-Entity
entity_currency_dict = {'E.4000': 'EUR','E.4001': 'EUR','E.4002': 'EUR','E.4003': 'GBP','E.4004': 'EUR','E.4005': 'EUR','E.4006': 'EUR','E.4007': 'EUR','E.4008': 'CHF','E.4009': 'EUR',
                        'E.4010': 'NOK','E.4011': 'EUR','E.4012': 'SEK','E.4013': 'DKK','E.4014': 'EUR','E.4015': 'EUR','E.4017': 'PLN','E.4404': 'EUR','E.4405': 'EUR','E.4406': 'EUR',
                        'E.4407': 'EUR','E.4408': 'CHF','E.4409': 'EUR','E.4410': 'NOK','E.4411': 'EUR','E.4412': 'SEK','E.4413': 'DKK','E.4414': 'EUR','E.4415': 'EUR','E.4417': 'PLN',
                        'E.4099': 'EUR','E.4409':'EUR'}

#Countries-Entity
entity_country_dict ={'EUROPE': 'E.4199', 'FRANCE': 'E.4001', 'GERMANY': 'E.4002', 'UNITED KINGDOM': 'E.4003', 'NETHERLANDS': 'E.4004', 'BELGIUM': 'E.4005', 'AUSTRIA': 'E.4006',
                    'SPAIN': 'E.4007', 'SWITZERLAND': 'E.4008', 'ITALY': 'E.4009', 'NORWAY': 'E.4010', 'IRELAND': 'E.4011', 'SWEDEN': 'E.4012', 'DENMARK': 'E.4013',
                    'FINLAND': 'E.4014', 'PORTUGAL': 'E.4015', 'Distributors': 'E.4099', 'POLAND': 'E.4417','Italy Warehouse': 'E.4409',  'AUSTRIA':'E.4406',  'SPAIN':'E.4407'}

#Sales discount %
percentage = {'FCST 2023':-0.012 ,'PLN 2023': -0.012, 'FCST 2024': -0.015, 'PLN 2024': -0.015}

#Assumed COGS % for PLAN
COGS_per = {'2023-01-01':0.5926319107,'2023-02-01':0.5926319107,'2023-03-01':0.5926319107,'2023-04-01':0.599408343,'2023-05-01':0.599408343,'2023-06-01':0.599408343,
            '2023-07-01':0.601413939,'2023-08-01':0.601413939,'2023-09-01':0.601413939,'2023-10-01':0.603894552,'2023-11-01':0.603894552,'2023-12-01':0.603894552,
            '2024-01-01':0.5926319107,'2024-02-01':0.5926319107,'2024-03-01':0.5926319107,'2024-04-01':0.599408343,'2024-05-01':0.599408343,'2024-06-01':0.599408343,
            '2024-07-01':0.601413939,'2024-08-01':0.601413939,'2024-09-01':0.601413939,'2024-10-01':0.603894552,'2024-11-01':0.603894552,'2024-12-01':0.603894552}

#Func.Area mapping
func_area_mapping = pd.read_excel('N:\Business Analysis\Report & Data directory\P&L and OPEX reports\Raw BPC Data\Func_area&Cost_Category Mapping.xlsx', sheet_name='Functional Area')
func_area_mapping = func_area_mapping[['Cost_center_code', 'Revised Func.Area']]

#Cost Category mapping
Cost_categoy_mapping = pd.read_excel('N:\Business Analysis\Report & Data directory\P&L and OPEX reports\Raw BPC Data\Func_area&Cost_Category Mapping.xlsx', sheet_name='Cost Category')


#*********Gross Revenue**********
# Get Gross Revenue Data from Raw BPC 
path_gross_rev = 'N:\\Business Analysis\\Report & Data directory\\P&L and OPEX reports\\Raw BPC Data\\Gross Revenue'

#clean the data
df_gross_rev = clean_Rev(path_gross_rev,'G')

#get forecast/plan for gross revenue
df_gross_rev_pf = execute_query_sql('SQL\Revenue Plan.sql')

#map country to entity
df_gross_rev_pf['Entity'] = df_gross_rev_pf['Entity'].map(entity_country_dict)

#Convert 'Date' column to datetime
df_gross_rev_pf['Period'] =pd.to_datetime(df_gross_rev_pf['Period'])

# Update 'Version' column
df_gross_rev['Year'] = df_gross_rev['Period'].dt.year.fillna(0).astype(int)

df_gross_rev['Version'] = df_gross_rev.apply(lambda row: f"{row['Version']} {row['Year']}", axis=1)
df_gross_rev_pf = Version(df_gross_rev_pf, 'PLN', 'plan')
df_gross_rev_pf = Version(df_gross_rev_pf, 'FCST', 'Fcst')

df_gross_rev = df_gross_rev.drop(["Year"], axis=1)

df_gross_rev_pf = df_gross_rev_pf[~df_gross_rev_pf['Period'].isin(df_gross_rev['Period'])]

#Append both dataframes to get all gross revenue row
df_gross = pd.concat([df_gross_rev, df_gross_rev_pf], ignore_index=True)

#Group by to get the totals per month
df_gross = df_gross.groupby(['Period', 'Version','Entity'],as_index=False).sum()

#Get the international reveneue
df_gross_international = df_gross[df_gross["Entity"] == 'E.4099'] 

#Add categories/attributes 
df_gross_international['Attribute'] = 'Gross Revenue-International'

#Get the domestic reveneue
df_gross_domestic = df_gross[df_gross["Entity"] != 'E.4099'] 

#Add categories/attributes 
df_gross_domestic['Attribute'] = 'Gross Revenue-Domestic'

#Combine both
df_gross = pd.concat([df_gross_domestic, df_gross_international], ignore_index=True)

#Get the column totals
total_per_column_gross = df_gross.groupby([df_gross['Period'],df_gross['Version'],df_gross['Entity']]).agg({'Amount': 'sum'}).reset_index()

#Add categories/attributes
total_per_column_gross['Attribute'] = 'Gross Revenue'

#*********Sales Discount**********
# Get Net Revenue Data from Raw BPC 
dir_path_sales_discount_act = r"input\Accounting amounts (Net Revenue)"

#clean the data
act_sales_discount  = clean_Rev(dir_path_sales_discount_act,'N')

# Update 'Version' column
act_sales_discount  = Version(act_sales_discount ,"ACT","ACT")

#Get the gross revenue for forecast and plan
gross_revenue_pln_fcst = filter(df_gross,(df_gross['Version'].str.contains('FCST'))  | (df_gross['Version'].str.contains('PLN')))

#Multiply the gross revenue with the % for sales forecast & plan
sales_discount_pf = (gross_revenue_pln_fcst.groupby([pd.to_datetime(gross_revenue_pln_fcst['Period']), gross_revenue_pln_fcst['Version'], gross_revenue_pln_fcst['Entity']]).agg({'Amount': 'sum'})).reset_index()

#Map %s to get sales discount for FCST & PLAN
sales_discount_pf['Amount'] = sales_discount_pf.apply(lambda row: row['Amount'] * percentage.get(row['Version'], 1),axis=1)

#Append both dataframes to get all sales discount
sales_discount = pd.concat([sales_discount_pf,act_sales_discount], ignore_index=True)

#Add categories/attributes 
sales_discount['Attribute'] = 'Sales discounts, GPO fees and chargebacks'

#Group by to get the totals per month
sales_discount = sales_discount.groupby(['Period', 'Version','Attribute','Entity'],as_index=False).sum()

#*********Net Revenue**********
#Merge sales discount & Gross revenue to get net revenue per quarter
net_rev = merger(sales_discount ,df_gross,['Period','Version','Entity'],'N')

#Add categories/attributes 
net_rev['Attribute'] = 'Net Revenue'

#get the variance from Plan
variance_net_revenue= get_the_variance_from_plan(net_rev,'Variance vs. PLN','N')

#*************COGS***************
# Get COGS Data 
COGS_act = execute_query_sql3()

# Update 'Version' column
COGS_act = Version(COGS_act,"ACT","ACT")

#Add categories/attributes 
COGS_act['Attribute'] = 'COGS'

#Group by to get the totals per month
COGS_act = COGS_act.groupby(['Period', 'Version','Attribute','Entity'],as_index=False).sum()

#Merge COGS & Net Revenue to get profit margin Actual
profit_margin_act = merger(net_rev,COGS_act,['Period','Entity','Version'],'M')

#Add categories/attributes
profit_margin_act['Attribute'] = 'Gross Profit/Margin'


#Get the net revenue for plan
net_revenue_pln = filter(net_rev,(net_rev['Version'].str.contains('PLN')) )

#Get the %s to calculate the COGS Plan
COGS_pr = 1 - net_revenue_pln['Period'].astype(str).map(COGS_per)

#Calculate COGS Plan
COGS_p = pd.DataFrame(COGS_PF(net_rev,COGS_pr,'PLN'), columns=['Period','Version','Amount','Entity'])

#Append both dataframes to get all COGS row
df_COGS = pd.concat([COGS_act,COGS_p], ignore_index=True)

#Add categories/attributes
df_COGS['Attribute'] = 'COGS'

#Calculate the profit margin
profit_margin = merger(df_COGS,net_rev,['Period','Version','Entity'],'M')

#Add categories/attributes
profit_margin['Attribute'] = 'Gross Profit/Margin'

#Convert amount to +
profit_margin['Amount'] = -1 * profit_margin['Amount'] 

#Get the variance vs plan for profit margin
variance_profit_margin = get_the_variance_from_plan(profit_margin,'Variance vs. PLN *','N')

#*********OPEX**********
#Get OPEX from the RAW BPC 
dir_opex_act = 'input\Raw BPC Data\OPEX\OPEX ACT'

#Get OPEX from the FCST Overview for 2024
dir_opex_fcst = 'input\OPEX\OPEX FCST\OPEX FCST'

#Get OPEX from the Plan
dir_opex_pln = "input\Raw BPC Data\OPEX\OPEX PLN"

#clean the data
df_opex_act = clean_opex(dir_opex_act,"ACT", r'\b(2[3-9]|[3-9][0-9]|\d{3,})\b')

#clean the data
df_opex_fcst = clean_opex(dir_opex_fcst,"FCST",r'\b(202[3-9]|20[3-9]\d|2[1-9]\d{2}|[3-9]\d{3})\b')

#clean the data
df_opex_pln = clean_opex(dir_opex_pln,"PLN",r'\b(202[3-9]|20[3-9]\d|2[1-9]\d{2}|[3-9]\d{3})\b')

# Update 'Version' column
df_opex_act['Cost_center_code'] = df_opex_act['Cost_center_code'].str.strip()
df_opex_fcst['Cost_center_code'] = df_opex_fcst['Cost_center_code'].str.strip()
df_opex_pln['Cost_center_code'] = df_opex_pln['Cost_center_code'].str.strip()

# Update 'Version' column
df_opex_act = Version(df_opex_act,"ACT"," ")
df_opex_fcst = Version(df_opex_fcst,"FCST","FCST")
df_opex_pln = Version(df_opex_pln,"PLN","PLN")


#----Cost Category & Functional Area----
#Get the cost category
cost_category_act = opex_config(df_opex_act,'Account_code')
cost_category_fcst= opex_config(df_opex_fcst,'Account_code')
cost_category_pln= opex_config(df_opex_pln,'Account_code')

# get the func area
fun_area_act = opex_config(df_opex_act,'Cost_center_code')
fun_area_fcst = opex_config(df_opex_fcst,'Cost_center_code')
fun_area_pln = opex_config(df_opex_pln,'Cost_center_code')

# #Rename Columns
cost_category_act.columns = ['Period',"Entity",'Cost_center_code','Account_code',"Amount","Version", "Attribute"]
cost_category_fcst.columns = ["Version","Entity",'Cost_center_code','Account_code','Period',"Amount", "Attribute"]
cost_category_pln.columns = ['Period',"Entity",'Cost_center_code','Account_code',"Amount","Version", "Attribute"]
fun_area_act.columns = ['Period',"Entity",'Cost_center_code','Account_code',"Amount","Version", "Attribute"]
fun_area_fcst.columns = ["Version","Entity",'Cost_center_code','Account_code','Period',"Amount", "Attribute"]
fun_area_pln.columns = ['Period',"Entity",'Cost_center_code','Account_code',"Amount","Version", "Attribute"]

#Group the data to get ACT & FCST/Plan
cost_category = pd.concat([cost_category_pln,cost_category_act,cost_category_fcst],ignore_index=True)
func_area = pd.concat([fun_area_pln,fun_area_act,fun_area_fcst], ignore_index=True)

# Drop rows based on specific criteria
func_area = func_area.drop(func_area[(func_area['Period'].fillna('na') == 'na')].index)
cost_category = cost_category.drop(cost_category[(cost_category['Period'].fillna('na') == 'na')].index)

#Convert amount into float
func_area["Amount"] = func_area["Amount"].astype(float)
cost_category["Amount"] = cost_category["Amount"].astype(float)

#Distinguish between OPEX Func area and Cost Category func area
func_area["Attribute"] = func_area["Attribute"].fillna("na").apply(lambda row: "OPEX " + row)

# ----GET THE COSTS----
#Filter attribute to get the COSTS
costs_opex = func_area[func_area["Attribute"] == 'OPEX COSTS'] 

#Add categories/attributes
costs_opex['Attribute'] = 'COSTS (from OPEX)'

# ----GET All OPEX not costs----
#Filter attribute to get everything but costs
other_func_area_opex = func_area[func_area["Attribute"] != 'OPEX COSTS'] 

#Group by and get the sum per month
other_func_area_opex = other_func_area_opex.groupby([other_func_area_opex['Period'],other_func_area_opex['Cost_center_code'],other_func_area_opex['Account_code'],other_func_area_opex['Version'],other_func_area_opex['Attribute'],other_func_area_opex['Entity']]).agg({'Amount': 'sum'}).reset_index()

#Get the column totals
total_per_column_opex = other_func_area_opex.groupby([other_func_area_opex['Period'],other_func_area_opex['Version'],other_func_area_opex['Entity']]).agg({'Amount': 'sum'}).reset_index()

#Add categories/attributes
total_per_column_opex['Attribute'] = 'Total OPEX'

#Get the variance vs plan for opex
variance_opex = get_the_variance_from_plan(other_func_area_opex,'Variance vs. PLN ***', 'OPEX')

variance_opex.columns = ["Period",'Cost_center_code', 'Account_code',"Version","Attribute","Entity","Amount"]

#-----Get the OPEX from Cost Categories----
#Group by and get the sum per month
cost_category= cost_category.groupby([cost_category['Period'],cost_category['Cost_center_code'],cost_category['Account_code'],cost_category['Version'],cost_category['Attribute'],cost_category['Entity']]).agg({'Amount': 'sum'}).reset_index()

#Get the column totals
total_per_column_cost_category = cost_category.groupby([cost_category['Period'],cost_category['Version'],cost_category['Entity']]).agg({'Amount': 'sum'}).reset_index()

#Add categories/attributes
total_per_column_cost_category['Attribute'] = 'Total OPEX'

#Get the variance vs plan for opex
variance_cost_category = get_the_variance_from_plan(cost_category,'Variance vs. PLN ***', 'OPEX')

variance_cost_category.columns = ["Period",'Cost_center_code', 'Account_code',"Version","Attribute","Entity","Amount"]

#------EBIT FUNC AREA-----
# Merge data based on the indicated list
EBIT = profit_margin.merge(total_per_column_opex, how = 'outer', on = ['Period','Version','Entity'])

EBIT['Amount'] = +EBIT['Amount_x'].fillna(0)-EBIT['Amount_y'].fillna(0)

EBIT.drop(['Amount_x','Amount_y','Attribute_x','Attribute_y'], axis=1, inplace=True)

#Add categories/attributes
EBIT['Attribute'] = 'EBIT before royalty and mngt fee'
#Get the variance vs plan for EBIT
variance_EBIT = get_the_variance_from_plan(EBIT,'Variance vs. PLN ****','N')

#------EBIT Cost Category-----
# Merge data based on the indicated list
EBIT_cost = profit_margin.merge(total_per_column_cost_category, how = 'outer', on = ['Period','Version','Entity'])

EBIT_cost['Amount'] = +EBIT_cost['Amount_x'].fillna(0)-EBIT_cost['Amount_y'].fillna(0)

EBIT_cost.drop(['Amount_x','Amount_y','Attribute_x','Attribute_y'], axis=1, inplace=True)

#Add categories/attributes
EBIT_cost['Attribute'] = 'EBIT before royalty and mngt fee'
#Get the variance vs plan for EBIT
variance_EBIT_cost = get_the_variance_from_plan(EBIT_cost,'Variance vs. PLN ****', 'N')


#Combine all data together (rev, func area,EBIT)
final_data_func_area = pd.concat([df_gross,total_per_column_gross,sales_discount,net_rev,variance_net_revenue,df_COGS,profit_margin,variance_profit_margin,costs_opex,other_func_area_opex,
                          total_per_column_opex,variance_opex,EBIT,variance_EBIT], ignore_index=True)

#Combine all data together (rev, cost category,EBIT)
final_data_cost_category = pd.concat([cost_category,total_per_column_cost_category,variance_cost_category], ignore_index=True)

#______DO NOT UNCOMMENT THIS WITHOUT BEING SURE THAT YOU HAVE THE CORRECT DATA UNDER THE SAME FORMAT______
# final_data_func_area.to_excel('output\CompanyP&L.xlsx')
# final_data_cost_category.to_excel('output\CompanyP&L_cost_category.xlsx')