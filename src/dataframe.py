import pandas as pd



def dataframe():

    dataframe = pd.read_csv(
        'C:/Users/mural/OneDrive/Desktop/Icons/Python_Projects/01_project/raw_data/orders.csv',
        na_values=['Not Available','unknown']
    )

    # print(dataframe.iloc[0]) # Print the first row
    # print(dataframe.head())  # only shows few Cloumns
    # print(dataframe.head(20))# Shows All cloumns


    # Step 1 :
    # Identify the how many unique values is there in shipments 
    # we make invalid column data as na_values  = ['Not Available','unknown']


    unq = dataframe['Ship Mode'].unique()
    # print(unq)



    # Step 2 :
    # Rename the columns
    # There are 2 Methods :

    # Method - 1 :
    '''
    dataframe = dataframe.rename(columns=
                    {'Order Id':'order_id',
                    'Ship Mode':'ship_mode',
                    'City':'city'}
                    )
    '''

    # print(dataframe.head(20)) # Wrong Pratice Because we have give all columns

    # Method - 2 :

    dataframe.columns = (
        dataframe.columns
        .str.lower()
        .str.replace(' ','_')
    )

    # print(dataframe.head(20)) #Best Pratice

    # Step 3 :
    # Calculate the Discount 
    dataframe['discount'] = dataframe['list_price'] * (dataframe['discount_percent']/100)

    # Calculate sale price list_price - discount
    dataframe['sale_price'] = dataframe['list_price'] - dataframe['discount']

    # Calculate the profit sale - cost
    dataframe['profit'] = dataframe['sale_price'] - dataframe['cost_price']


    # step - 4 :
    # Convert Date(Str) type to DATE type

    dataframe['order_date'] = pd.to_datetime(
        dataframe['order_date'],format="%Y-%m-%d"
    )

    # Drop Cost_price, List_price and discount_percent columns
    dataframe.drop(columns=['cost_price','list_price','discount_percent'],inplace=True)



    # print(dataframe.dtypes)

    # print(dataframe.head(20))

    # Return the processed DataFrame
    return dataframe

