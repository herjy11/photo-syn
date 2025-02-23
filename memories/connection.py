import psycopg2

def get_connection(ip="192.168.0.69"):
    connection = psycopg2.connect(
        host=ip,
        database="synofoto",
        user="postgres",
        port=5432,
    )

    if connection:
        print("Connection to the PostgreSQL established successfully.")
    else:
        raise Exception("Connection to the PostgreSQL encountered and error.")

    return connection