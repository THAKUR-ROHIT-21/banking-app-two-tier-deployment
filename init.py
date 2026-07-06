import os
import boto3
import pymysql
import sys

client = boto3.client("ssm", region_name="ap-south-1")

def get_param(name):
    return client.get_parameter(
        Name=f"/application/banking/{name}",
        WithDecryption=True
    )["Parameter"]["Value"]

conn = None

try:
    DB_HOST = get_param("DB_HOST")
    DB_USER = get_param("DB_USER")
    DB_PASSWORD = get_param("DB_PASSWORD")
    DB_NAME = get_param("DB_NAME")
    DB_PORT = int(get_param("DB_PORT"))

    conn = pymysql.connect(
    host=get_param("DB_HOST"),
    user=get_param("DB_USER"),
    password=get_param("DB_PASSWORD"),
    database=get_param("DB_NAME"),
    port=int(get_param("DB_PORT")),
    connect_timeout=10
    )

    cur = conn.cursor()

    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
    cur.execute(f"USE `{DB_NAME}`")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file = os.path.join(base_dir, "init.sql")

    with open(sql_file, "r", encoding="utf-8") as f:
        sql = f.read()

    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            cur.execute(statement)

    conn.commit()
    print("✅ Database initialized successfully")

except Exception as e:
    print("❌ error:", e)
    sys.exit(1)

finally:
    if conn:
        conn.close()    