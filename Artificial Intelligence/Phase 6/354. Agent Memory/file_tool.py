import os
from config import FILES_FOLDER


def search_files(query):
    query = query.lower().strip()
    results = []

    if not os.path.exists(FILES_FOLDER):
        return {
            "success": False,
            "error": "Files folder does not exist."
        }

    for filename in os.listdir(FILES_FOLDER):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(FILES_FOLDER, filename)

        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()

            if query in content.lower() or query in filename.lower():
                results.append({
                    "file": filename,
                    "content": content[:3000]
                })

        except Exception as error:
            results.append({
                "file": filename,
                "error": str(error)
            })

    return {
        "success": True,
        "query": query,
        "results": results
    }