def get_friendly_error(error):
    """
    Convert common API errors into
    user-friendly messages.
    """

    error_text = str(error).lower()

    if (
        "429" in error_text
        or "resource_exhausted" in error_text
        or "rate limit" in error_text
    ):
        return (
            "Gemini's API usage limit has been reached. "
            "Please try again later."
        )

    if (
        "api key" in error_text
        or "unauthenticated" in error_text
        or "401" in error_text
    ):
        return (
            "The Gemini API key appears to be missing "
            "or invalid."
        )

    if (
        "503" in error_text
        or "unavailable" in error_text
        or "overloaded" in error_text
    ):
        return (
            "Gemini is temporarily unavailable. "
            "Please try again shortly."
        )

    if "json" in error_text:

        return (
            "Gemini returned an unexpected response format. "
            "Please generate the results again."
        )

    return (
        "An unexpected error occurred while processing "
        "your request."
    )