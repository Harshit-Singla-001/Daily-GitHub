from calculator_tool import calculate
from database_tool import search_database, get_database_tables
from file_tool import search_files

def calculator(expression):
    return calculate(expression)

def database_search(table, limit=20):
    return search_database(table, limit)

def file_search(query, max_results=5):
    return search_files(query, max_results)

def database_tables():
    return get_database_tables()