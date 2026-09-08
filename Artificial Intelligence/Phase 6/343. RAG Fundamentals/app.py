from chunker import create_chunks
from document_loader import load_document
from embeddings import generate_embeddings
from vector_store import (
    create_store,
    search_store
)
from rag_pipeline import generate_answer


def main():
    print("=" * 60)
    print("RAG QUESTION ANSWERING SYSTEM")
    print("=" * 60)

    document_path = input(
        "\nDocument path > "
    ).strip()

    try:
        text = load_document(
            document_path
        )

        if not text.strip():
            print(
                "\nError: Document is empty."
            )
            return

        chunks = create_chunks(text)

        print(
            f"\nCreated {len(chunks)} chunks."
        )

        embeddings = generate_embeddings(
            chunks
        )

        index = create_store(
            embeddings
        )

        print(
            "\nDocument indexed successfully."
        )

        while True:
            question = input(
                "\nQuestion > "
            ).strip()

            if question.lower() == "exit":
                print("\nGoodbye!")
                break

            if not question:
                continue

            try:
                question_embedding = (
                    generate_embeddings(
                        [question]
                    )
                )

                results = search_store(
                    index,
                    question_embedding[0],
                    chunks
                )

                context = "\n\n".join(
                    results
                )

                answer = generate_answer(
                    question,
                    context
                )

                print(
                    f"\nAnswer:\n{answer}"
                )

            except Exception as error:
                print(
                    f"\nError: {error}"
                )

    except Exception as error:
        print(
            f"\nApplication Error: {error}"
        )


if __name__ == "__main__":
    main()