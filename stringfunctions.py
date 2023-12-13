

import psycopg2
import re
import sqlparse
import json
import traceback


def sanitize_string(value):
        sanitized_value = re.sub(r"'", "''", value)
        return sanitized_value.strip().lower()

