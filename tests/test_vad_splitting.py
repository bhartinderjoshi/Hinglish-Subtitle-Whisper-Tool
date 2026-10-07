"""
Test VAD-based word and timing grouping
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video_to_srt import group_words_for_subtitles


def test_vad_timing_grouping():
    """Test subtitle grouping with pause gap threshold"""
    sample_segments = [
        {
            "id": 0,
            "start": 0.0,
            "end": 8.0,
            "text": "Sabka favorite ice cream tender coconut from natural",
            "words": [
                {"text": "Sabka", "start": 0.0, "end": 0.5, "confidence": 0.95},
                {"text": "favorite", "start": 0.55, "end": 1.1, "confidence": 0.92},
                {"text": "ice", "start": 1.15, "end": 1.5, "confidence": 0.94},
                {"text": "cream", "start": 1.55, "end": 2.0, "confidence": 0.91},
                # Pause of 1.0s
                {"text": "tender", "start": 3.0, "end": 3.5, "confidence": 0.89},
                {"text": "coconut", "start": 3.55, "end": 4.1, "confidence": 0.95},
                {"text": "from", "start": 4.15, "end": 4.5, "confidence": 0.92},
                {"text": "natural", "start": 4.55, "end": 5.0, "confidence": 0.94},
            ],
        }
    ]

    subs = group_words_for_subtitles(sample_segments, max_words=4, max_pause_gap=0.5)
    assert len(subs) == 2
    assert subs[0][0] == "Sabka favorite ice cream"
    assert subs[1][0] == "tender coconut from natural"


if __name__ == "__main__":
    test_vad_timing_grouping()
    print("✓ test_vad_timing_grouping passed")
