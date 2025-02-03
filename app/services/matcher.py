import logging
from typing import Dict, List, Tuple
from app.models.schemas import Quote
from app.core.exceptions import InvalidTopicsError, InvalidProviderConfigError

logger = logging.getLogger(__name__)


def get_top_3_topics(topics: Dict[str, int]) -> List[Tuple[str, int]]:
    """
    Returns the top three topics sorted by resource count (highest first).

    For example, given:
        {
            "reading": 20,
            "math": 50,
            "science": 30,
            "history": 15,
            "art": 10
        }
    This function returns:
        [("math", 50), ("science", 30), ("reading", 20)]
    """
    if not isinstance(topics, dict):
        logger.error("Invalid type for topics: expected Dict[str, int], got %s", type(topics))
        raise InvalidTopicsError("Topics must be a dictionary of {str: int}.")

    if not topics:
        logger.warning("Received an empty topics dictionary.")
        return []

    for key, value in topics.items():
        if not isinstance(key, str) or not isinstance(value, int):
            logger.error("Invalid data in topics: key=%s, value=%s", key, value)
            raise InvalidTopicsError("All keys in topics must be strings and values must be integers.")

    return sorted(topics.items(), key=lambda item: item[1], reverse=True)[:3]


def calculate_single_topic_price(count: int, teacher_index: int) -> float:
    """
    Calculates the price for a single topic based on its importance.

    The percentages are defined as:
      - Teacher index 0 (highest request) -> 20%
      - Teacher index 1 -> 25%
      - Teacher index 2 -> 30%
    """
    percentage_mapping = {0: 0.20, 1: 0.25, 2: 0.30}
    if teacher_index not in percentage_mapping:
        logger.warning("Unexpected teacher_index: %d", teacher_index)

    return count * percentage_mapping.get(teacher_index, 0)


def get_provider_matches(topics: Dict[str, int], provider_config: Dict) -> List[Quote]:
    """
    Generates a list of quotes from providers based on the teacher's requested topics.

    Pricing rules:
      1. If a provider matches exactly 2 topics and these topics appear in teacher's
         top three in consecutive order (i.e. teacher indices are consecutive and in ascending order),
         then the provider's quote is 10% of the combined resource counts for both topics.
      2. Otherwise, use only the first matching topic (in the order defined by the provider's config)
         and calculate the quote using its associated percentage:
             - Teacher index 0 -> 20%
             - Teacher index 1 -> 25%
             - Teacher index 2 -> 30%
    """
    if not isinstance(provider_config, dict):
        logger.error("Invalid provider_config type: expected Dict, got %s", type(provider_config))
        raise InvalidProviderConfigError("Provider config must be a dictionary.")

    if "provider_topics" not in provider_config or not isinstance(provider_config["provider_topics"], dict):
        logger.error("provider_config is missing 'provider_topics' or has an invalid format.")
        raise InvalidProviderConfigError("Provider config must contain a dictionary under the key 'provider_topics'.")

    quotes = []
    teacher_top3 = get_top_3_topics(topics)
    if not teacher_top3:
        logger.warning("No top 3 topics found, skipping provider matching.")
        return []

    # Create a mapping from topic name to (count, teacher_index)
    teacher_topics = {topic: (count, index) for index, (topic, count) in enumerate(teacher_top3)}

    # Iterate over each provider in the configuration
    for provider, provider_topics_str in provider_config["provider_topics"].items():
        if not isinstance(provider_topics_str, str):
            logger.error("Provider %s has an invalid topics format: expected str, got %s", provider,
                         type(provider_topics_str))
            continue

        # Split provider's topics while preserving their order
        provider_topics = provider_topics_str.split("+")

        # Build a list of topics that are in the teacher's top 3
        matching_topics = []
        for topic in provider_topics:
            if topic in teacher_topics:
                count, teacher_index = teacher_topics[topic]
                matching_topics.append((topic, count, teacher_index))

        # If no topics match, skip this provider.
        if not matching_topics:
            logger.info("No matching topics found for provider %s.", provider)
            continue

        # If there are exactly 2 matching topics, check if they are consecutive and in order.
        if len(matching_topics) == 2:
            teacher_indices = [entry[2] for entry in matching_topics]
            if teacher_indices[0] < teacher_indices[1] and (teacher_indices[1] - teacher_indices[0] == 1):
                total_count = matching_topics[0][1] + matching_topics[1][1]
                price = total_count * 0.1  # Apply 10% rule
                logger.info("Applying 10%% rule for provider %s: price=%.2f", provider, price)
                quotes.append(Quote(provider=provider, price=price))
                continue

        # For a single matching topic or non-consecutive two topics,
        # use the first matching topic as defined by the provider's order.
        topic, count, teacher_index = matching_topics[0]
        price = calculate_single_topic_price(count, teacher_index)
        logger.info("Provider %s matched topic %s with price %.2f", provider, topic, price)
        quotes.append(Quote(provider=provider, price=price))

    return quotes
