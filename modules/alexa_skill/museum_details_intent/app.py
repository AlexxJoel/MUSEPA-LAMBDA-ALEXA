import json

from psycopg2.extras import RealDictCursor

from connect_db import get_db_connection
from functions import datetime_serializer


def lambda_handler(_event, _context):
    conn = None
    cur = None
    try:
        # Get database connection
        conn = get_db_connection()

        # Create cursor
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Find event by name
        cur.execute("SELECT * FROM museums ORDER BY id ASC LIMIT 1")
        museum = cur.fetchone()

        if not museum:
            return {"statusCode": 204, "body": json.dumps({"message": "Museum not found"})}

        return {"statusCode": 200, "body": json.dumps({"data": museum}, default=datetime_serializer)}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({"error": str(e)})}
    finally:
        # Close connection and cursor
        if conn is not None:
            conn.close()
        if cur is not None:
            cur.close()


# test_event = None
# test_context = None
#
# print(lambda_handler(test_event, test_context))
