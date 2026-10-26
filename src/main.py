
# Import the function that connects to Oracle
from oracle_connection import get_connection

# Import the function that reads and transforms the CSV
from dataframe import dataframe

# Import Pandas for handling DataFrame data types and missing values
import pandas as pd


def main():

    # STEP 1: EXTRACT AND TRANSFORM
    # Call dataframe() to read the CSV, clean column names,
    # calculate discount, sale_price, profit, and convert dates.
    # The processed DataFrame is stored in df.
    df = dataframe()

    # Print a message to confirm that the DataFrame is ready.
    print("DataFrame Loaded Successfully . . .")

    # Display the first five rows to check the processed data.
    print(df.head())

    # Display the total number of rows that will be inserted.
    print("Total DataFrame rows:", len(df))

    # Initialize the connection variable.
    # None allows us to check later whether a connection was opened.
    connection = None

    try:
        # STEP 2: CONNECT TO ORACLE
        # Open a connection using the credentials and configuration
        # defined inside oracle_connection.py.
        connection = get_connection()

        # Create a cursor to execute SQL statements.
        # The with statement automatically closes the cursor afterward.
        with connection.cursor() as cursor:

            # STEP 3: CHECK WHETHER THE TABLE EXISTS
            # USER_TABLES contains tables owned by the connected Oracle user.
            # Oracle stores ordinary unquoted table names in uppercase,
            # so we search for ORDERS.
            cursor.execute("""
                SELECT COUNT(*)
                FROM USER_TABLES
                WHERE TABLE_NAME = 'ORDERS'
            """)

            # fetchone() retrieves the query result.
            # If the count is greater than zero, the table exists.
            table_exists = cursor.fetchone()[0] > 0

            # STEP 4: DROP THE EXISTING TABLE
            # If ORDERS exists, drop it before creating a fresh table.
            # This removes the existing table and its data.
            if table_exists:
                cursor.execute("DROP TABLE ORDERS")
                print("Existing ORDERS table dropped successfully.")
            else:
                # If the table does not exist, there is nothing to drop.
                print("ORDERS table does not exist.")

            # STEP 5: PREPARE THE TABLE COLUMN DEFINITIONS
            # Create an empty list to store each column name and
            # its corresponding Oracle data type.
            column_definitions = []

            # Loop through every DataFrame column and its Pandas data type.
            for column, dtype in df.dtypes.items():

                # DATE stores date and time to the nearest second in Oracle.
                # Pandas timestamps are converted before insertion below.
                if pd.api.types.is_datetime64_any_dtype(dtype):
                    oracle_type = "DATE"

                # Use NUMBER(19) for integer columns.
                elif pd.api.types.is_integer_dtype(dtype):
                    oracle_type = "NUMBER(19)"

                # Use NUMBER(18,4) for floating-point numeric columns.
                # This allows up to four digits after the decimal point.
                elif pd.api.types.is_float_dtype(dtype):
                    oracle_type = "NUMBER(18,4)"

                # Store Boolean values as numeric values.
                elif pd.api.types.is_bool_dtype(dtype):
                    oracle_type = "NUMBER(1)"

                # Use VARCHAR2 for text and other unrecognized types.
                else:
                    oracle_type = "VARCHAR2(4000)"

                # Append the column definition to the list.
                # Example: "ORDER_ID" VARCHAR2(4000)
                column_definitions.append(
                    f'"{column.upper()}" {oracle_type}'
                )

            # STEP 6: GENERATE THE CREATE TABLE STATEMENT
            # Join the column definitions with commas.
            # This automatically creates a table matching the DataFrame columns.
            create_sql = f"""
                CREATE TABLE ORDERS (
                    {", ".join(column_definitions)}
                )
            """

            # Execute the CREATE TABLE statement in Oracle.
            cursor.execute(create_sql)

            print("ORDERS table created successfully.")

            # STEP 7: PREPARE THE INSERT STATEMENT
            # Get all DataFrame column names in their original order.
            columns = list(df.columns)

            # Convert column names to uppercase and join them with commas.
            # Example: "ORDER_ID", "CITY", "PROFIT"
            column_names = ", ".join(
                f'"{col.upper()}"' for col in columns
            )

            # Generate one bind placeholder for each column.
            # Example: :1, :2, :3
            # Bind variables safely pass data separately from SQL.
            placeholders = ", ".join(
                f":{i + 1}" for i in range(len(columns))
            )

            # Build the INSERT statement dynamically.
            # The column order and placeholder order must match the row data.
            insert_sql = f"""
                INSERT INTO ORDERS ({column_names})
                VALUES ({placeholders})
            """

            # STEP 8: CONVERT DATAFRAME ROWS
            # Oracle needs Python-compatible values.
            # Build a list of tuples, with one tuple for each DataFrame row.
            rows = []

            # itertuples() reads rows efficiently without including the index.
            for row in df.itertuples(index=False, name=None):

                converted_row = []

                for value in row:

                    # Convert NaN, NaT, and other Pandas missing values
                    # to Python None, which Oracle inserts as SQL NULL.
                    if pd.isna(value):
                        converted_row.append(None)

                    # Convert Pandas Timestamp to Python datetime,
                    # which the Oracle driver can bind to a DATE column.
                    elif isinstance(value, pd.Timestamp):
                        converted_row.append(
                            value.to_pydatetime()
                        )

                    # Keep other values unchanged.
                    else:
                        converted_row.append(value)

                # Store the converted row as a tuple.
                # Tuples work well as parameter sequences for executemany().
                rows.append(tuple(converted_row))

            # STEP 9: BULK INSERT THE DATA
            # executemany() inserts multiple rows using one prepared
            # SQL statement, reducing the overhead of repeated executions.
            if rows:
                cursor.executemany(insert_sql, rows)

            # STEP 10: COMMIT THE INSERTED DATA
            # Commit saves the inserted rows in the database.
            connection.commit()

            print(f"{len(rows)} records inserted successfully.")

            # STEP 11: VERIFY THE INSERTED ROW COUNT
            # Query Oracle to confirm how many rows are in the table.
            cursor.execute("""
                SELECT COUNT(*)
                FROM ORDERS
            """)

            # Read the count returned by Oracle.
            total_rows = cursor.fetchone()[0]

            print("Total records in Oracle ORDERS:", total_rows)

    # STEP 12: HANDLE ERRORS
    # Catch connection, SQL, data-conversion, and insertion errors.
    except Exception as error:

        # Roll back uncommitted transactional changes if possible.
        # Note: Oracle DDL statements such as DROP and CREATE TABLE
        # commit implicitly and cannot be undone by this rollback.
        if connection is not None:
            connection.rollback()

        print("ETL process failed:", error)

    # STEP 13: CLOSE THE CONNECTION
    # This runs whether the ETL succeeds or fails.
    # It releases the Oracle database connection.
    finally:

        if connection is not None:
            connection.close()
            print("Oracle connection closed.")


# Run main() only when this file is executed directly.
# Importing this file from another Python module will not run main().
if __name__ == "__main__":
    main()
