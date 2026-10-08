"""
Unit tests for video_to_srt core helper functions
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video_to_srt import format_timestamp, group_words_for_subtitles


def test_format_timestamp():
    """Test SRT timestamp formatting"""
    assert format_timestamp(0.0) == "00:00:00,000"
    assert format_timestamp(1.5) == "00:00:01,500"
    assert format_timestamp(65.25) == "00:01:05,250"
    assert format_timestamp(3661.123) == "01:01:01,123"


def test_group_words_empty():
    """Test word grouping with empty input"""
    assert group_words_for_subtitles([]) == []


def test_group_words_basic():
    """Test word grouping with sample word tokens"""
    segments = [
        {
            "id": 0,
            "start": 0.0,
            "end": 2.0,
            "text": "Namaste dosto kaise hain",
            "words": [
                {"text": "Namaste", "start": 0.0, "end": 0.5, "confidence": 0.95},
                {"text": "dosto", "start": 0.55, "end": 1.0, "confidence": 0.92},
                {"text": "kaise", "start": 1.05, "end": 1.5, "confidence": 0.94},
                {"text": "hain", "start": 1.55, "end": 2.0, "confidence": 0.91},
            ],
        }
    ]

    subs = group_words_for_subtitles(segments, max_words=2)
    assert len(subs) == 2
    assert subs[0][0] == "Namaste dosto"
    assert subs[1][0] == "kaise hain"


if __name__ == "__main__":
    test_format_timestamp()
    test_group_words_empty()
    test_group_words_basic()
    print("✓ All video_to_srt unit tests passed")
