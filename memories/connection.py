import psycopg2

def get_connection(ip, port):
    connection = psycopg2.connect(
        host=ip,
        database="synofoto",
        user="postgres",
        port=port,
    )

    if connection:
        print("Connection to the PostgreSQL established successfully.")
    else:
        raise Exception("Connection to the PostgreSQL encountered and error.")

    return connection