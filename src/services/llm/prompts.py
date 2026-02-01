def summary_prompt(lang: str) -> tuple[str, str]:
    """
    Возвращает:
    - system_instruction
    - user_prompt_template (c {title}, {content}, {published_at})
    """

    if lang == "ru":
        system = (
            "You're a news service assistant."
            "Write a brief, neutral description of the news item"
            "in Russian in 2-3 sentences."
            "Without emotions, judgments, or emojis."
        )
    else:
        system = (
            "You are a news assistant. "
            "Summarize the news in 2–3 short neutral sentences. "
            "No opinions, no emojis."
        )

    user = (
        "Title:\n{title}\n\n"
        "Date:\n{published_at}\n\n"
        "Content:\n{content}"
    )

    return system, user