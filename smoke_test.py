import boto3
import os
import sys
import pymysql

# Get SSM Parameters
client = boto3.client("ssm", region_name="ap-south-1")

parameters = {
    os.path.basename(p["Name"]): p["Value"]
    for p in client.get_parameters_by_path(
        Path="/application/banking",
        WithDecryption=True
    )["Parameters"]
}

# Required Parameters
required = [
    "DB_HOST",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_PORT"
]

missing = [k for k in required if k not in parameters]

print("===== SSM Parameters Check =====")
for k in required:
    print(f"{k}: {'✅' if k in parameters else '❌'}")

if missing:
    print(f"\n❌ Failed: Missing Parameters -> {', '.join(missing)}")
    sys.exit(1)

print("\n✅ All required parameters found.\n")

# ============================
# Connect to MySQL
# ============================

try:
    connection = pymysql.connect(
        host=parameters["DB_HOST"],
        user=parameters["DB_USER"],
        password=parameters["DB_PASSWORD"],
        database=parameters["DB_NAME"],
        port=int(parameters["DB_PORT"]),
        connect_timeout=10
    )

    cursor = connection.cursor()

    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]

    print(f"📦 Database : {parameters['DB_NAME']}")

    if tables:
        print("\n📋 Tables:")
        for table in tables:
            print(f"   ✅ {table}")
    else:
        print("\n⚠️ No tables found.")

    cursor.close()
    connection.close()

except Exception as e:
    print(f"\n❌ DB_ERROR: {e}")
    sys.exit(1)

print("\n✅ Smoke Test Completed Successfully")