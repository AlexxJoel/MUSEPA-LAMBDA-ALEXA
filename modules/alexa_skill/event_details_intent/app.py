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
        event_name = query_params.get('event_name', None)

        if not event_name:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing fields"})}

        # Find event by name
        cur.execute("SELECT * FROM events WHERE name ILIKE %s", (f"%{event_name}%",))
        events = cur.fetchall()

        if not events:
            return {"statusCode": 204, "body": json.dumps({"message": "No matching events"})}

        return {"statusCode": 200, "body": json.dumps({"data": events}, default=datetime_serializer)}
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
        'event_name': 'esculturas'
    }
}
test_context = None

print(lambda_handler(test_event, test_context))
