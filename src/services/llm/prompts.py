def summary_prompt(lang: str) -> tuple[str, str]:
    """
    Возвращает:
    - system_instruction
    - user_prompt_template (c {title}, {content}, {published_at})
    """

    if lang == "ru":
        system = (
            "Ты помощник новостного сервиса. "
            "Сделай краткое нейтральное описание новости "
            "на русском языке в 2–3 предложениях. "
            "Без эмоций, оценок и эмодзи."
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