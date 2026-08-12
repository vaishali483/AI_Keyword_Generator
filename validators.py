def validate_topic(topic):
    """
    Validate the seed topic entered by the user.

    Returns:
        (is_valid, cleaned_topic_or_error)
    """

    if not topic:
        return False, "Please enter a topic or seed keyword."

    cleaned_topic = topic.strip()

    if len(cleaned_topic) < 2:
        return False, "The topic is too short."

    if len(cleaned_topic) > 100:
        return False, "Please keep the topic under 100 characters."

    return True, cleaned_topic