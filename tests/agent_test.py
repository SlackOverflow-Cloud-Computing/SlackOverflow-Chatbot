from app.agent.assistant_manager import AssistantManager

if __name__ == "__main__":
    manager = AssistantManager()
    user_inputs = {
        "recommendation": """
            My playlist:
            - I Don't Care (with Justin Bieber) - Loud Luxury Remix
            - Memories - Dillon Francis Remix
            - All the Time - Don Diablo Remix
            - Call You Mine - Keanu Silva Remix
            - Someone You Loved - Future Humans Remix
            """,
        "chat": "What's the best way to discover new indie artists?",
        "analysis": "I love listening to Coldplay, Radiohead, and The Beatles. I enjoy relaxing music, but I also appreciate deep lyrics that make me think."
    }

    recommendation = manager.generate_response("recommendation", user_inputs["recommendation"])
    print("=== Recommendation ===")
    for rec in recommendation:
        print(rec)

    chat_response = manager.generate_response("chat", user_inputs["chat"])
    print("\n=== Chat Response ===")
    for resp in chat_response:
        print(resp)

    analysis = manager.generate_response("analysis", user_inputs["analysis"])
    print("\n=== Analysis ===")
    for ana in analysis:
        print(ana)