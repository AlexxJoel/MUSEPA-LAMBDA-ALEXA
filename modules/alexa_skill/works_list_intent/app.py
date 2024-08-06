import json
import math

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

        if int(page) < 0 or int(size) <= 0:
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid fields"})}

        # Find event by name
        cur.execute("SELECT * FROM works OFFSET %s LIMIT %s", (page, size))
        entities = cur.fetchall()

        # Get total elements count
        cur.execute("SELECT COUNT(*) AS total_elements FROM works")
        res = cur.fetchone()
        total_elements = int(res['total_elements'])
        page = int(page)
        size = int(size)

        is_last_page = total_elements <= (page + 1) * size

        total_pages = math.ceil(total_elements / size)
        
        if not entities:
            return {"statusCode": 204, "body": json.dumps({"message": "No works in this range"})}

        return {"statusCode": 200, "body": json.dumps({
            "data": entities,
            "totalElements": total_elements,
            "isLasPage": is_last_page,
            "totalPages": total_pages
        }, default=datetime_serializer)}
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
#         'page': "0",
#         'size': "10"
#     }
# }
# test_context = None
#
# print(lambda_handler(test_event, test_context))
