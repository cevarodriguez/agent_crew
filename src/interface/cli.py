import logging
from agents.crew import Crew

def main():
    logging.basicConfig(level=logging.INFO)
    crew = Crew()

    print("Dopamine Q&A Assistant (type 'exit' or empty line to quit)\n")

    while True:
        question = input("Ask a question about dopamine: ").strip()
        if not question or question.lower() == "exit":
            print("Goodbye!")
            break

        print("\nThinking...")
        response = crew.handle_question(question)

        print("\nAnswer:\n", response["answer"])
        print("\nSources:")
        for source in response["sources"]:
            # Show PDF or web citation
            if "filename" in source:
                print(f" PDF: {source['filename']} (page {source.get('page', '?')})")
            elif "url" in source:
                print(f" Web: {source['title']} ({source['url']})")
            print("-" * 40)
            

if __name__ == "__main__":
    main()