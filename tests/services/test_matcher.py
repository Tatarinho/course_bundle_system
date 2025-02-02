import pytest
from app.models.schemas import Quote
from app.services.matcher import get_top_3_topics, calculate_single_topic_price, get_provider_matches


def test_get_top_3_topics():
    """Test sorting and limiting to top 3 topics"""
    topics = {
        "reading": 20,
        "math": 50,
        "science": 30,
        "history": 15,
        "art": 10
    }

    result = get_top_3_topics(topics)
    expected = [("math", 50), ("science", 30), ("reading", 20)]
    assert result == expected


def test_calculate_single_topic_price():
    """Test price calculation for single topics based on their position"""
    # First position (20%)
    assert calculate_single_topic_price(100, 0) == 20.0

    # Second position (25%)
    assert calculate_single_topic_price(100, 1) == 25.0

    # Third position (30%)
    assert calculate_single_topic_price(100, 2) == 30.0

    # Invalid position should return 0
    assert calculate_single_topic_price(100, 3) == 0


def test_provider_matches_consecutive_topics():
    """Test providers with consecutive topics in top 3"""
    topics = {
        "math": 50,
        "science": 30,
        "reading": 20,
        "history": 15
    }

    provider_config = {
        "provider_topics": {
            "provider_a": "math+science",  # consecutive (0,1) -> 10% of 80
            "provider_b": "science+reading",  # consecutive (1,2) -> 10% of 50
            "provider_c": "math+reading"  # not consecutive (0,2) -> use math (20% of 50)
        }
    }

    result = get_provider_matches(topics, provider_config)
    result_dict = {quote.provider: quote.price for quote in result}

    assert result_dict["provider_a"] == 8.0  # 10% of (50 + 30)
    assert result_dict["provider_b"] == 5.0  # 10% of (30 + 20)
    assert result_dict["provider_c"] == 10.0  # 20% of 50


def test_provider_matches_edge_cases():
    """Test various edge cases for provider matching"""
    topics = {
        "math": 50,
        "science": 30,
        "reading": 20
    }

    provider_config = {
        "provider_topics": {
            "provider_a": "art+history",  # no matches in top 3
            "provider_b": "math",  # single topic
            "provider_c": "reading+art",  # one match in top 3
            "provider_d": "reading+science"  # reverse order of consecutive
        }
    }

    result = get_provider_matches(topics, provider_config)
    result_dict = {quote.provider: quote.price for quote in result}

    # Provider with no matches should not be in results
    assert "provider_a" not in result_dict

    # Single topic provider
    assert result_dict["provider_b"] == 10.0  # 20% of 50

    # One match in top 3
    assert result_dict["provider_c"] == 6.0  # 30% of 20

    # Topics in reverse order still count as consecutive
    assert "provider_d" in result_dict


def test_empty_cases():
    """Test empty or invalid input cases"""
    # Empty topics
    assert get_top_3_topics({}) == []

    # Empty provider config
    result = get_provider_matches({"math": 50}, {"provider_topics": {}})
    assert result == []

    # All topics have same value
    topics = {
        "math": 30,
        "science": 30,
        "reading": 30
    }
    top_3 = get_top_3_topics(topics)
    assert len(top_3) == 3
    assert all(count == 30 for _, count in top_3)