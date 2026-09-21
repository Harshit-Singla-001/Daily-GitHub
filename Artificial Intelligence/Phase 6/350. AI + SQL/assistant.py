from sql_generator import generate_sql
from sql_validator import validate_sql
from database import execute_query

def process_question(question):
    if not question or not question.strip():
        return {
            "success": False,
            "message": "Please enter a question."
        }

    try:
        sql = generate_sql(question)

        valid, validation_message = validate_sql(sql)

        if not valid:
            return {
                "success": False,
                "message": validation_message,
                "sql": sql
            }

        result = execute_query(sql)

        return {
            "success": True,
            "question": question,
            "sql": sql,
            "columns": result["columns"],
            "rows": result["rows"],
            "row_count": len(result["rows"])
        }

    except Exception as error:
        return {
            "success": False,
            "message": str(error)
        }