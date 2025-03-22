
import pandas.io.sql as sqlio

def get_people(connection):
    data = sqlio.read_sql_query("SELECT * FROM person WHERE NOT name = ''", connection)
    # Now data is a pandas dataframe having the results of above query.

    names = data['name'].values
    return names


def get_users(connection):
    data = sqlio.read_sql_query("SELECT * FROM user_info", connection)
    # Now data is a pandas dataframe having the results of above query.

    names = data['name'].values[1:]
    return names
