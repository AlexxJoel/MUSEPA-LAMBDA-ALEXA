import json

from psycopg2.extras import RealDictCursor

from connect_db import get_db_connection
from functions import datetime_serializer


def lambda_handler(event, _context):
    conn = None
    cur = None
    try:
        # Get database connection
        conn = get_db_connection()

        # Create cursor
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get parameters
        query_params = event.get('queryStringParameters', {})

        # Set parameter value
        page = query_params.get('page', None)
        size = query_params.get('size', None)

        if page is None or size is None:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing fields"})}

        if page < 0 or size <= 0:
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid fields"})}

        # Find event by name
        cur.execute("SELECT * FROM works OFFSET %s LIMIT %s", (page, size))
        works = cur.fetchall()

        if not works:
            return {"statusCode": 204, "body": json.dumps({"message": "No works in this range"})}

        return {"statusCode": 200, "body": json.dumps({"data": works}, default=datetime_serializer)}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({"error": str(e)})}
    finally:
        # Close connection and cursor
        if conn is not None:
            conn.close()
        if cur is not None:
            cur.close()


test_event = {
    'queryStringParameters': {
        'page': 0,
        'size': 10
    }
}
test_context = None

print(lambda_handler(test_event, test_context))
