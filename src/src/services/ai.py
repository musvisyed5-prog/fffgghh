from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def get_client():
    """
    Retrieve the AI client instance.
    
    Returns:
        The initialized client object for AI operations.
    """
    return client


def rewrite_text(text: str) -> str:
    """
    Rewrites the given text in a professional manner using an AI chat model.
    Args:
        text (str): The input text to be rewritten professionally.
    Returns:
        str: The rewritten text with professional tone and formatting.
    Example:
        >>> result = company_rewrite_text("this is a bad written text")
        >>> print(result)
        "This is a poorly written text."
    """

    prompt = f"""
        Rewrite the following text professionally.

        Output rules:
        - Only return the rewritten text.
        - No explanations.

        Text:
        {text}
    """
    suggested_text = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a professional editor."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.5
    )
    return suggested_text.choices[0].message.content