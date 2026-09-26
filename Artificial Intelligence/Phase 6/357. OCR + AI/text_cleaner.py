import re


def clean_text(text):
    if not text:
        return ""

    text = text.replace(
        "\r\n",
        "\n"
    )

    text = text.replace(
        "\r",
        "\n"
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    lines = []

    for line in text.split("\n"):
        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


def get_text_statistics(text):
    words = re.findall(
        r"\b\w+\b",
        text
    )

    lines = [
        line
        for line in text.splitlines()
        if line.strip()
    ]

    paragraphs = [
        paragraph
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    return {
        "characters": len(text),
        "words": len(words),
        "lines": len(lines),
        "paragraphs": len(paragraphs)
    }