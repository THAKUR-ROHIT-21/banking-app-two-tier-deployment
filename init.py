import os
import boto3
import sys
import pymysql

client = boto3.client("ssm", region_name="ap-south-1")

def get_param(name):
    return client.get_parameter(
        Name=f"/application/banking/{name}",
        WithDecryption=True

    )["Parameter"]["Value"]

try:
    conn=pymysql.connect(
        host=get_param["DB_HOST"],
        user=get_param["DB_USER"],
        password=get_param["DB_PASSWORD"],
        database=get_param["DB_NAME"],
        port=int(get_param["DB_PORT"]),
        connect_timeout=10
    )

    cur=conn.cursor()
    base_dir=os.path.dirname(os.path.abspath(__file__))
    sql_file=os.path.join(base_dir,"init.sql")
    
    with open(sql_file,"r",encoding="utf-8") as f:
        sql=f.read()
    
    for statement in sql.split(";"):
        statement=statement.strip()
        if statement:
            cur.execute(statement)
    
    conn.commit()
    print("✅ Database connect successfully")

except Exception as e:
    print("❌ error :",e)

finally:
    conn.close()
