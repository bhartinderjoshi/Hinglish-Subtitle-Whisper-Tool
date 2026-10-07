"""
Unit test for word grouping function
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video_to_srt import group_words_for_subtitles


def test_group_words_for_subtitles():
    """Test group_words_for_subtitles function with sample segments"""
    sample_segments = [
        {
            "id": 0,
            "start": 0.0,
            "end": 3.8,
            "text": "Hello world how are you doing today",
            "words": [
                {"text": "Hello", "start": 0.0, "end": 0.3, "confidence": 0.9},
                {"text": "world", "start": 0.35, "end": 0.8, "confidence": 0.95},
                {"text": "how", "start": 0.85, "end": 1.2, "confidence": 0.92},
                {"text": "are", "start": 1.25, "end": 1.5, "confidence": 0.91},
                # Pause of 0.9s (1.5s to 2.4s)
                {"text": "you", "start": 2.4, "end": 2.7, "confidence": 0.88},
                {"text": "doing", "start": 2.75, "end": 3.2, "confidence": 0.95},
                {"text": "today", "start": 3.25, "end": 3.8, "confidence": 0.94},
            ],
        }
    ]

    result = group_words_for_subtitles(sample_segments, max_words=4, max_pause_gap=0.5)

    assert len(result) == 2
    assert result[0][0] == "Hello world how are"
    assert abs(result[0][1] - 0.0) < 0.01
    assert abs(result[0][2] - 1.5) < 0.01
    assert result[1][0] == "you doing today"
    assert abs(result[1][1] - 2.4) < 0.01
    assert abs(result[1][2] - 3.8) < 0.01


if __name__ == "__main__":
    test_group_words_for_subtitles()
    print("✓ test_group_words_for_subtitles passed")
