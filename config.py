import pandas as pd
import datetime


def MEB_to_energy_map(meb):

    energy_map_path = 'EnergyMap/EnergyMap.xlsx'

    #Reading tables:
    MEB = pd.read_excel(meb, sheet_name='MEB', index_col=2, skiprows=range(2))
    energy_map_ref = pd.read_excel(energy_map_path, sheet_name='Stream data from MEB')

    #Decide which column from the MEB and the EnergyMap to keep
    columns = ['Description', 'Section', 'Tag (MEB)', 'T [C]', 'P [bara]', 'Flow [kg/h]', 'cp [kJ/kgK]', 'h [kJ/kg]', 'Concentration']
    descr_list = ['TC', 'Ptot', 'massflowtot', 'Cpgas', 'Hspecgas', 'molpercH2Otot']

    #Reducing the energy map into the necessary tags:
    descr = pd.Series(descr_list)
    energy_map_ref = energy_map_ref[columns]
    energy_map_ref = energy_map_ref[energy_map_ref['Description'].notna()]
    tags_series = energy_map_ref['Tag (MEB)']
    tags_list = tags_series.dropna().to_list()

    MEB_condensed = MEB[MEB.index.isin(descr)][tags_list]
    return MEB_condensed.transpose()

def kilnstops_times(kilnstops_excelsheet):
    #Fetching the stops from the excel sheet, returning a dataframe with all start and stop times.
    df = pd.read_excel(kilnstops_excelsheet, sheet_name='Kilnstops 2011-2019') #reading the excel-sheet
    df_kilnstops = df[['date', "Weeks"]] #fetching out only the first date and week

    for i in range(1,9):
        #appending all the columns in the sheet which has a "date" and "week" prefix.
        df_add = df[['date.' + str(i), 'Weeks.'+ str(i)]]
        df_add.columns = ['date', 'Weeks']
        df_kilnstops = pd.concat([df_kilnstops, df_add])

    df_kilnstops.dropna(inplace=True) #Removes all columns with NaN
    df_kilnstops['date'] = pd.to_datetime(df_kilnstops['date'], dayfirst=True) #Because of the formatting of the sheet, some of the dates are in a different format. This solves this problem, but is very susceptible to format changes.

    end_date = [] #Create an empty list
    for index, row in df_kilnstops.iterrows():
        #This iterates through the dataframe to calculate the time difference between start and stop
        start_time = row['date']
        week_difference = row['Weeks']
        end_date.append(start_time + datetime.timedelta(weeks=week_difference))
    df_kilnstops['end_date'] = end_date #appending the list to the dataframe

    #Finding load difference
    df_kilnstops['hours'] = df_kilnstops['Weeks']*7*24 #finding the number of hours stoptime instead of weeks

    #Finding the numbers of non-stoptime, applying a trick to shift the end-date column up one step and calculating difference per row.
    df_kilnstops['end_shift'] = df_kilnstops['end_date'].shift(1)
    df_kilnstops['hours_off'] = df_kilnstops['date'] - df_kilnstops['end_shift']
    df_kilnstops['hours_off_int'] = df_kilnstops['hours_off']/pd.Timedelta(hours=1) #Converting it to hours
    
    #Filling in a zero in the last column first, and then filling in zero time in the columns which has a datetime type
    df_kilnstops['hours_off_int'].fillna(0, inplace=True)
    df_kilnstops.fillna(datetime.timedelta(hours=0), inplace=True)

    return df_kilnstops

def cumulative_storage(df_kilnstops, initial_storage, running_loading, stop_loading):
    storage = []
    timestamp = []
    current_storage = initial_storage


    #This loop will make a new dataframe which consists of all the timestamps and the current loading in the storage at that point in time.
    for index, row in df_kilnstops.iterrows():
        timestamp.append(row['date'])
        #Consider fixing the naming here
        current_storage += running_loading * row['hours_off_int']
        storage.append(current_storage)
        timestamp.append(row['end_date'])
        current_storage += stop_loading * row['hours']
        storage.append(current_storage)
        
    # return storage

    df_storage = pd.DataFrame(list(zip(timestamp, storage)), columns=['timestamp', 'storage']) #Creating a new dataframe with the lists generated
    df_storage.set_index('timestamp', inplace=True) #setting timestamp to be index
    return df_storage

    
