import csv
import decimal
import math
from datetime import datetime

def analyse(path_to_file):
    ''' This function analyse the csv file containing the world vaccination 
    data.
    Reference: https://stackoverflow.com/questions/4174941/how-to-sort-a-list
    -of-lists-by-a-specific-index-of-the-inner-list. To sort table by column
    value.
    
    :param path_to_file: string of path to csv file.
    '''
    # Open and read csv file.
    with open(path_to_file) as csvfile:
        reader = csv.reader(csvfile)
        # Skip header.
        next(reader)
        data = [row for row in reader]
    # Data cleaning. Sort data by date then location name.
    data = sorted(data, key = lambda x : datetime.strptime(x[2], "%Y-%m-%d"))
    data = sorted(data, key = lambda x : x[0])
    
    print("Analysing data file ./vaccinations.csv \n\n"
          "Question 1: ")
    count_unique_loc(data)
    unique_countries = count_unique_country(data)
    count_vacc_doses(data, unique_countries)
    count_vacc_popluation(data, unique_countries)
    
    print("\nQuestion 2: ")
    top_vacc_countries = find_top_vacc_countries(data, unique_countries)
    find_partly_vacc_rate(data, top_vacc_countries)
    
    print("\nQuestion 3: ")
    earliest_vacc_countries = find_earliest_vacc_countries(
        data, unique_countries)
    find_peak_date(data, earliest_vacc_countries)
    
    print("\nQuestion 4: ")
    lowest_fully_vacc_countries = find_lowest_fully_vacc_countries(
        data, unique_countries)
    predict_days_to_80(data, lowest_fully_vacc_countries)
    
def count_unique_loc(data):
    ''' QUESTION 1a: Count the number of unique locations in the data file 
    and print the result to the screen. 
    
    :param data: world vaccination data
    '''
    # Find locations in the first column in data.
    locations = [row[0] for row in data]
    # Put list into a set to eliminate duplicates and then count number 
    # of elements in it.
    num_unique_loc = len(set(locations))
    
    print("Number of unique locations: ", num_unique_loc)
    
def count_unique_country(data):
    ''' QUESTION 1b: Count the number of unique countries in the data file 
    and print the result to the screen.
    
    :param data: world vaccination data
    '''
    # Find the location and iso_code column in data.
    countries_table = [[row[0],row[1]] for row in data]
    # Remove rows with other aggregate or sub-countries data.
    no_subcountries = [row for row in countries_table if 
                       row[1].find("OWID_") == -1]
    loc_no_isocode = [row[0] for row in no_subcountries]
    # Put list into a set to eliminate duplicates.
    unique_country = set(loc_no_isocode)
    num_countries = len(unique_country)
    
    print("Number of unique countries: ", num_countries)      
    return set(unique_country)
    
def count_vacc_doses(data, unique_countries):
    ''' QUESTION 1c: Count the total number of vaccine doses that have been 
    globally administered in all countries. As countries report data at
    differet dates, so we assume that the latest total vaccination for 
    each country is the one on their latest available data.

    :param data: world vaccination data
    :param unique_countries: a list of unique country in data
    '''
    # Find locations and total vaccinations columns for all countries.
    total_vacc = [[row[0],row[3]] for row in data if row[0] in 
                  unique_countries]
    # Remove rows with no total vaccination data.
    total_vacc = remove_empty_row(total_vacc, [1])
    # Find the latest data for each country.
    total_vacc = find_latest_data(total_vacc)
    # Convert all total vaccination data into decimal and add to a list.
    total_vacc_data = [int(row[1]) for row in total_vacc]
    global_dose = sum(total_vacc_data)

    print("Global vaccine doses: ", global_dose)
    
def count_vacc_popluation(data, unique_countries):
    ''' QUESTION 1d: The global number of people who have received at least 
    one dose over all countries in the world and also those who are fully 
    vaccinated. 
    Assumption: The total people_vaccinated and total people_fully_vaccinated
    of a country is the latest data.

    :param data: world vaccination data
    :param unique_country_list: a list of unique country in data
    '''
    # Find the column for location, people_vaccinated and 
    # people_fully_vaccinated.
    vacc_table = [[row[0], row[4], row[5]] for row in data if 
                    row[0] in unique_countries]
    # Remove rows with empty vaccination cell.
    vacc_no_empty = remove_empty_row(vacc_table,[1])
    fvacc_no_empty = remove_empty_row(vacc_table,[2])
    
    vacc_data = [vacc_no_empty, fvacc_no_empty]
    result = "Global population vaccinated: "
    for i in range(len(vacc_data)):
        # Find the latest data for each country.
        latest_data = find_latest_data(vacc_data[i])
        if i == 0:
            # Creates a list with the entries in people_vaccinated column.
            vacc = [int(row[1]) for row in latest_data]
            num = sum(vacc)
        else:
            # Creates a list with the entries in 
            # people_fully_vaccinated column.
            fvacc = [int(row[2]) for row in latest_data]
            num = sum(fvacc)
            result += "\nGlobal population fully vaccinated: "
            
        result += str(num)
        
    print(result)

def find_top_vacc_countries(data, unique_countries):
    ''' QUESTION 2a: Find the top 10 countries with a population of at least 
    1 million having the highest percentage of their population being 
    vaccinated with at least one dose.
    Assumption: The population of all countries are the population calculated 
    by the latest data without rows with 0 and empty cells. 
    The countries that contain no data or only contain 0 in
    people_vaccinated_per_hundred will not be included.

    :param data: world vaccination data
    :param unique_countries: a list of unique country in data
    '''
    # Find the columns for locations, people_vaccinated,
    # people_vaccinated_per_hundred and people_fully_vaccinated if location 
    # is a country.
    vacc_data = [[row[0], row[4], row[10], row[11]] for row in data 
                 if row[0] in unique_countries]
    # Remove rows with empty vaccination cell.
    vacc_data = remove_empty_row(vacc_data, [1, 2])
    # Remove rows with 0.
    vacc_data = [row for row in vacc_data if float(row[2]) != 0]
    # Find latest data for each country.
    latest_vacc_data = find_latest_data(vacc_data)
    
    countries_over_million = []
    for i in range(len(latest_vacc_data)):
        # Find the countries with population of at least 1 million.
        # Calculate the population of a country.
        country_popn = (float(latest_vacc_data[i][1]) / 
                        (float(latest_vacc_data[i][2]) / 100))
        if country_popn >= 1000000:
            # Append people vaccinated percentage, country name, 
            # people_fully_vaccinated.
            countries_over_million.append([float(latest_vacc_data[i][2]),
                                            latest_vacc_data[i][0], 
                                            latest_vacc_data[i][3]])      
    # Sorted the percentage of population vaccinated in descending order.
    sorted_countries = sorted(countries_over_million, reverse = True)
    # Select the top 10 countries.
    top_vacc_countries = sorted_countries[:10]
    
    return top_vacc_countries

def find_partly_vacc_rate(data, top_vacc_countries):
    ''' QUESTION 2b: For the top-10 countries found in 
    count_popluation_vaccined(), report the percentage of population 
    being partly vaccinated. A person is called partly vaccinated if 
    they already received one dose of vaccine but are not fully vaccinated.
    If there are no fully vaccinated percentage on the same date, we display
    NaN for that country.
    Assumptions: Top_vacc_countries only contains country, no locations.
    
    :param data: world vaccination data
    :param top_vacc_countries: a table of countries that have the highest 
    vaccination percentage, where the first column is vaccination percentage 
    and second column is their names
    '''
    for i in range(len(top_vacc_countries)):
        # Check if fully_vaccinated_per_hundred is empty.
        if (top_vacc_countries[i][2] == '') :
            # Empty and we cannot calculate the partly vaccinated rate, 
            # so we append NaN.
            top_vacc_countries[i].append('NaN')
        else:
            # Calulate the difference between fully vaccinated percentage
            # and vaccinated percentage, to get percentage for partly
            # vaccinated people. Round the result into 2 decimal place.
            diff = str(round(decimal.Decimal(top_vacc_countries[i][0]) 
                        - decimal.Decimal(top_vacc_countries[i][2]), 2))
            # Add the difference to corresponding country.
            top_vacc_countries[i].append(diff)
    
    # Print percentage vaccinated and partly vaccinated.
    for j in range(len(top_vacc_countries)):
        info = (top_vacc_countries[j][1] + ": "
                + str(top_vacc_countries[j][0]) 
                + "% population vaccinated, "
                + top_vacc_countries[j][3] + "% partly vaccinated")
        print (info)

def find_earliest_vacc_countries(data, unique_countries):
    ''' QUESTION 3a: Find the earliest 10 countries in which are the 
    earliest getting their people vaccinated. 
    Assumption: People vaccinated account for people received first dose only.
    Locations of data are sorted by alphabetical order and all rows of one 
    location is sorted by date.
    
    :param data: world vaccination data
    :param unique_countries: a list of unique country in data
    '''
    # Find the columns for locations, date, and people_vaccinated from data. 
    people_vacc = [[row[0], row[2], row[4]] for row in data 
                   if row[0] in unique_countries]
    # Remove row if vaccinated data is empty.
    people_vacc = remove_empty_row(people_vacc, [2])
    # Remove row with 0 in daily_vaccinations column and the location 
    # is a country.
    people_vacc = [row for row in people_vacc if float(row[2]) != 0]
    # Find the earliest data in each country.
    table_earliest = [people_vacc[0]]
    for i in range(len(people_vacc) - 1):
        if people_vacc[i][0] != people_vacc[i + 1][0]:
            table_earliest.append(people_vacc[i + 1])
    # Sort countries using date.
    table_earliest = [[datetime.strptime(row[1], "%Y-%m-%d").date(),
                       row[0]] for row in table_earliest]
    # Slice the table_earliest to get the earliest 10 countries.
    earliest_contries = (sorted(table_earliest))[:10]
    return earliest_contries

def find_peak_date(data, earliest_vacc_countries):
    ''' Question 3b: For the earliest 10 countries found in 
    find_earliest_vacc_countries_date(), find the highest vaccinations
    across all days in that country by looking at the field daily_vaccinations.
    Assumtion: There are only countries in earliest_vacc_countries list.
    
    :param data: world vaccination data
    :param earliest_vacc_countries: a table of countries that have the 
    earliest vaccination date, where the first column is vaccination date 
    and second column is the countries
    '''
    # List the earliest 10 countries from find_earliest_vacc_countries_date().
    country_names = [row[1] for row in earliest_vacc_countries]
    # Find the columns for locations, date, and daily_vaccinations from data 
    # for all interested countries.
    daily_vacc = [[row[0], row[2], row[8]] for row in data if 
                   row[0] in country_names]
    # Remove row if vaccinated data is empty.
    daily_vacc = remove_empty_row(daily_vacc,[2])
    # Find the highest vaccinations in each countries.
    for i in range(len(country_names)):
        country_data = [row for row in daily_vacc 
                        if row[0] == country_names[i]]
        # Change the daily_vaccinations data to the first column.
        country_data = [[int(row[2]),row[1],row[0]] for row in country_data]
        # Sorted the data in descending order and choose the largest
        # number of daily_vaccinations in that country.
        highest_vacc = (sorted(country_data, reverse = True))[0]
        # Add the result to corresponding country in earliest_vacc_countries.
        # Daily vaccination.
        earliest_vacc_countries[i].append(highest_vacc[0])
        # Date.
        earliest_vacc_countries[i].append(highest_vacc[1])
    
    # Print the information in countries_highest_vacc 
    # and earliest_vacc_countries.
    for j in range(len(earliest_vacc_countries)):
        info = (earliest_vacc_countries[j][1]
                + ": first vaccinated on " 
                + str(earliest_vacc_countries[j][0]) + " , "
                + str(earliest_vacc_countries[j][2]) 
                + " people vaccinated on "
                + earliest_vacc_countries[j][3])
        print (info)

def find_lowest_fully_vacc_countries(data, unique_countries):
    ''' QUESTION 4a: Find the top 10 countries with the lowest percentage 
    of fully vaccinated people, where these percentages are greater 50%. 
    Assumption: The latest available data is the newest data for every country.
    
    :param data: world vaccination data
    :param unique_countries: a list of unique country in data
    '''
    # Get country and people_fully_vaccinated_per_hundred columns from table.
    fvacc  = [(row[0], row[11]) for row in data if row[0] in unique_countries]
    # Remove row if vaccinated data is empty. 
    fvacc = remove_empty_row(fvacc, [1])
    # Find latest data for each country.
    fvacc = find_latest_data(fvacc)
    # Filter the list by 50%.
    fvacc_over_50 = [row for row in fvacc if decimal.Decimal(row[1]) > 50]
    # Sort list by vaccination rate in ascending order.
    fvacc_over_50_sorted = sorted(fvacc_over_50, 
                                  key = lambda x : decimal.Decimal(x[1]))
    # Slice the list to get the first 10 countries.
    lowest_fvacc_countries = fvacc_over_50_sorted[:10]
    return lowest_fvacc_countries

def predict_days_to_80(data, lowest_fvacc_countries):
    ''' QUESTION 4b: For the countries with lowest fully vaccination rate, 
    predict how many days they would take to get to 80% population fully 
    vaccinated. We assume lowest_fvacc_countries list only contains countries, 
    no locations are included. The days to 80 is the day from the latest data
    reported day for each country.
    
    The forecast will use linear regression with least square method, as from 
    observation that two variables date and fully vaccination rate follows a 
    linear relationship.
    
    Earliest vaccination date: we will consider the earliest vaccincation date
    as it can be different for every country and it may due to the availability
    of vaccination in that country. This could effect our forecast, hence the 
    data before the earliest vaccination date will not be used for the analysis
    
    Missing data (Missing completely at random): we will ignore this type of
    missing data, assuming that it will not has a significant influence on our
    model. However, if the dataset is relatively small, we will imputate
    estimated data.
    
    Outliers: we will not drop any true outliers in the dataset, because there
    are situations that can lead to an sudden increase on vaccination such as
    enforeced restrictions. However, we will try detect any outliers that may 
    come from things like human error by checking the continuous increasing of
    value.
    
    References: 
    - How to handle missing data:
    https://www.scribbr.com/statistics/missing-data/
    - How to find outliers: https://www.scribbr.com/statistics/outliers/
    - Calculate of linear regreesion model:
    https://www.mathsisfun.com/data/least-squares-regression.html
    - Compare date: https://www.w3schools.com/python/python_datetime.asp
    - Remove a list from a list of list:
    https://stackoverflow.com/questions/58069060/
    removing-a-list-from-a-list-of-lists-python
    - Round number to ceiling:
    https://stackoverflow.com/questions/2356501/how-do-you-round-up-a-number

    :param data: world vaccination data
    :param lowest_fvacc_countries: a list of list containing countries with 
    lowest fully vaccination rate and its fully vaccination percentage
    '''
    # List all countries that we want to predict.
    country_names = [row[0] for row in lowest_fvacc_countries]
    # Get earliest vacc date for all lowest fully vacc countries.
    earliest_dates = find_earliest_vacc_countries(data, country_names)
    
    # Get location, date and fully vaccination percentage columns from table
    # for all interested countries.
    fully_vacc = [[row[0], row[2], row[11]] for row in data 
                  if row[0] in country_names]
    diff = []
    for country in country_names:
        # Obtain data for each country.
        country_data = [row for row in fully_vacc if row[0] == country]
        # Remove rows where the date is before the earliest vacincation date
        # for each country.
        for data in earliest_dates:
            # Find country.
            if data[1] == country:
                # Get date and convert it to datetime format.
                earliest_date = data[0]
                country_data = [row for row in country_data if 
                                datetime.strptime(row[1], "%Y-%m-%d").date() 
                                >= earliest_date]
        
        # Add time dummy to table.
        for i in range(len(country_data)):
            country_data[i].append(i)
        # Check actual number of data each country has by removing rows
        # with no fully vaccination date.
        if len(remove_empty_row(country_data, [2])) > 100:
            # Remove rows if the dataset is larger than 100.
            country_data = remove_empty_row(country_data, [2])
        else:
            # Else impute missing values.
            country_data = impute_missing_values(country_data)
        
        # Look for outliers.
        country_data = find_outliers(country_data)
        
        # Get list of x, time dummys.
        x = [row[3] for row in country_data]
        # Get list of y, fully vaccination percentage.
        y = [decimal.Decimal(row[2]) for row in country_data]
        # Calculations for least square linear regression.
        x_square = [x**2 for x in x]
        x_y = []
        for k in range(len(x)):
            x_y.append(x[k] * y[k])
        sum_x = sum(x)
        sum_y = sum(y)
        sum_x_square = sum(x_square)
        sum_x_y = sum(x_y)
        n = len(x)
        
        # Get slope m and intercept b.
        slope = ((n * sum_x_y - (sum_x * sum_y)) / 
                 (n * sum_x_square - sum_x ** 2))
        intercept = (sum_y - slope * sum_x) / n

        # Calulate x when y is equal to 80.
        x = (80 - intercept) / slope
        # Get the index of the last day.
        last_x = country_data[len(country_data) - 1][3]
        # Add the difference of days to diff list.
        # Use math.ceil to round days up to nearest integer.
        diff.append(math.ceil(x - last_x))

    # Print percentage and prediction.
    for j in range(len(lowest_fvacc_countries)):
        info = (lowest_fvacc_countries[j][0] + ": "
                + lowest_fvacc_countries[j][1]
                + "% population fully vaccinated, "
                + str(diff[j]) + " days to 80%")
        print (info)


def remove_empty_row(table, columns_to_check):
    ''' Helper Function. This function takes in a table and a list of columns
    to be check. It removes the row if the value in these corresponding columns 
    is empty. Assumption: the table contains at least one row.
    
    :param table: a list of list
    :param columns_to_remove: a list of columns to be checked
    '''
    for j in range(len(columns_to_check)):
        table = [row for row in table if row[columns_to_check[j]] != '']
    return table

def find_latest_data(table):
    ''' Helper Function. This function takes in a table, find the last row 
    with latest data for each country and return a new table with all rows
    with latest data. 
    Assumption: The last row for each country in the input table does not 
    contain empty cell. The first column contains location names, locations
    are sorted by alphabetical order and all rows of one location is sorted
    by date. The table has at least 1 rows.
    
    :param table: a table which has location names as its first column.
    '''
    table_latest = []
    for i in range(len(table)):
        if i == len(table) - 1:
            # Append last row of the table.
            table_latest.append(table[len(table) - 1])
        elif table[i][0] != table[i + 1][0]:
            # Append rows where location name changes.
            table_latest.append(table[i])
    return table_latest

def impute_missing_values(table):
    ''' This helper function impute missing values by estimating values
    between existing data points and return a filled table. 
    Assumption: The starting point is 0.
    
    :param table: a list of list containing vaccination data of countries.
    '''
    # Find all empty cells that we would like to impute.
    start = -1
    end = -1
    index = start
    start_list = []
    end_list = []
    for row in table:
        # Check for empty cells.
        # Use index as a indicator to find expected start and end.
        if not row[2] and index == start:
            # When empty cell is found and index is equal to start.
            # Change start to index of the current row.
            start = row[3]
            start_list.append(start)
        elif row[2] and index != start:
            # When non-empty cell is found and index is not equal to start.
            # Change end to index of the current row.
            end = row[3]
            # Set index to start, enable us to search for start now.
            index = start
            end_list.append(end)
    
    # Calculate and fill in cells.
    for j in range(len(start_list)):
        # Find each start and end.
        start = start_list[j]
        end = end_list[j]
        length = end - start + 1
        
        index = 1
        # Loop through each start and end.
        for i in range(start, end):
            if i == 0:
                # Start of vaccincation data.
                # Insert 0.
                table[i][2] = str(0)
            else:
                # Handle the start of vaccincation data, assuming 0.
                if start != 0:
                    # Otherwise start value is the previous non-empty value.
                    start_val = decimal.Decimal(table[start - 1][2])
                else:
                    start_val = 0
                end_val = decimal.Decimal(table[end][2])
                # Estimate value in between, which every adjacent values have 
                # the same differences.
                est = ((end_val - start_val) / (decimal.Decimal(length)) 
                       * (index) + start_val)
                # Insert value to table.
                table[i][2]  =str(round(est, 2))
                index += 1

    return table

def find_outliers(table):
    ''' A helper function to detect any potential outliers in the table,
    by checking the continuous increasing feature of the data, to check
    again human error etc. Remove outliers if found.

    :param table: a list of list containing the data we want to test in
    the third column
    '''
    # Get a list of values from the desired column, fully vaccination rate.
    data = [row[2] for row in table]
    for i in range(len(data) - 1):
        # The current value must not larger than the next value.
        if (decimal.Decimal(data[i]) > decimal.Decimal(data[i + 1])):
            # Remove if there are any.
            table.pop(i)
    return table

# The section below will be executed when you run this file.
# Use it to run tests of your analysis function on the data
# files provided.

if __name__ == '__main__':
    # test on a CSV file
    analyse('./vaccinations_shuffled.csv')
