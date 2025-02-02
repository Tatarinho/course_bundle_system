from typing import Dict, List, Tuple
from app.models.schemas import Quote


def get_top_3_topics(topics: Dict[str, int]) -> List[Tuple[str, int]]:
    """
    Return the top three topics sorted by resource count (highest first).

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
    return sorted(topics.items(), key=lambda item: item[1], reverse=True)[:3]


def calculate_single_topic_price(count: int, teacher_index: int) -> float:
    """
    Calculate the price for a single topic based on its importance.

    The percentages are defined as:
      - Teacher index 0 (highest request) -> 20%
      - Teacher index 1 -> 25%
      - Teacher index 2 -> 30%
    """
    percentage_mapping = {0: 0.20, 1: 0.25, 2: 0.30}
    return count * percentage_mapping.get(teacher_index, 0)


def get_provider_matches(topics: Dict[str, int], provider_config: Dict) -> List[Quote]:
    """
    Generate a list of quotes from providers based on the teacher's requested topics.

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
    quotes = []
    teacher_top3 = get_top_3_topics(topics)

    # Create a mapping from topic name to (count, teacher_index)
    teacher_topics = {topic: (count, index) for index, (topic, count) in enumerate(teacher_top3)}

    # Iterate over each provider in the configuration
    for provider, provider_topics_str in provider_config["provider_topics"].items():
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
            continue

        # If there are exactly 2 matching topics, check if they are consecutive and in order.
        if len(matching_topics) == 2:
            teacher_indices = [entry[2] for entry in matching_topics]
            # Check for ascending order and consecutiveness (difference == 1)
            if teacher_indices[0] < teacher_indices[1] and (teacher_indices[1] - teacher_indices[0] == 1):
                total_count = matching_topics[0][1] + matching_topics[1][1]
                price = total_count * 0.1  # Apply 10% rule
                quotes.append(Quote(provider=provider, price=price))
                continue
            # Otherwise, fall back to using just the first matching topic.

        # For a single matching topic or non-consecutive two topics,
        # use the first matching topic as defined by the provider's order.
        topic, count, teacher_index = matching_topics[0]
        price = calculate_single_topic_price(count, teacher_index)
        quotes.append(Quote(provider=provider, price=price))

    return quotes
