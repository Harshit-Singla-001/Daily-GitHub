import os

from config import FILES_FOLDER

ALLOWED_EXTENSIONS = {
    ".txt"
}

def search_files(
    query,
    max_results=5
):
    try:
        query = query.strip().lower()

        if not query:
            return {
                "success": False,
                "error": "Search query is empty."
            }

        if not os.path.exists(FILES_FOLDER):
            return {
                "success": False,
                "error": "Files directory does not exist."
            }

        results = []

        for filename in os.listdir(
            FILES_FOLDER
        ):
            file_path = os.path.join(
                FILES_FOLDER,
                filename
            )

            if not os.path.isfile(file_path):
                continue

            extension = os.path.splitext(
                filename
            )[1].lower()

            if extension not in ALLOWED_EXTENSIONS:
                continue

            try:
                with open(
                    file_path,
                    "r",
                    encoding="utf-8"
                ) as file:
                    content = file.read()

            except UnicodeDecodeError:
                continue

            content_lower = content.lower()

            if query not in content_lower:
                continue

            index = content_lower.find(query)

            start = max(
                0,
                index - 300
            )

            end = min(
                len(content),
                index + len(query) + 500
            )

            results.append({
                "file": filename,
                "snippet": content[start:end]
            })

            if len(results) >= max_results:
                break

        return {
            "success": True,
            "query": query,
            "results": results
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }