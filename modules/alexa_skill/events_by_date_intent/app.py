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
        event_date = query_params.get('date', None)

        if not event_date:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing fields"})}

        # Find events by date
        cur.execute("SELECT * FROM events WHERE %s >= start_date AND %s <= end_date ORDER BY id ASC",
                    (event_date, event_date))
        entities = cur.fetchall()

        if not entities:
            return {"statusCode": 204, "body": json.dumps({"message": "No events ongoing"})}

        return {"statusCode": 200, "body": json.dumps({"data": entities}, default=datetime_serializer)}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({"error": str(e)})}
    finally:
        # Close connection and cursor
        if conn is not None:
            conn.close()
        if cur is not None:
            cur.close()


# test_event = {
#     'queryStringParameters': {
#         'date': '2024-06-07'
#     }
# }
# test_context = None
#
# print(lambda_handler(test_event, test_context))
