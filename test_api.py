import requests

API_URL = "http://localhost:8000"

def test_question(question: str):
    response = requests.post(
        f"{API_URL}/ask",
        json={"question": question}
    )
    
    result = response.json()
    
    print(f"\n❓ Question: {question}")
    print("="*80)
    print(f"\n💡 Answer:\n{result['answer']}\n")
    print(f"📚 Sources:")
    for source in result['sources']:
        print(f"  - {source}")
    print("="*80)

if __name__ == "__main__":
    questions = [
        "How do I install Python?",
        "What are Python loops?",
        "How to define a function?"
    ]
    
    for q in questions:
        test_question(q)