"""
Tests for Subtitle Editor, ASS Generation, and Video Burning Export
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web_server import app, generate_ass_script, hex_to_ass_color, srt_time_to_ass_time


def test_hex_to_ass_color():
    # White with full opacity
    assert hex_to_ass_color("#FFFFFF", 1.0) == "&H00FFFFFF"
    # Yellow with full opacity (#FFE600 -> BGR is 00, E6, FF)
    assert hex_to_ass_color("#FFE600", 1.0) == "&H0000E6FF"
    # Black with 50% opacity (alpha=0.5 -> 128 = 0x80)
    assert hex_to_ass_color("#000000", 0.5) == "&H80000000"


def test_srt_time_to_ass_time():
    assert srt_time_to_ass_time("00:01:23,456") == "0:01:23.46"
    assert srt_time_to_ass_time("01:00:05,000") == "1:00:05.00"


def test_generate_ass_script():
    subs = [
        {
            "index": 1,
            "startTime": "00:00:01,000",
            "endTime": "00:00:03,500",
            "text": "Namaste dosto, kaise hain aap?"
        }
    ]
    styles = {
        "fontName": "Montserrat",
        "fontSize": 36,
        "primaryColor": "#FFE600",
        "primaryAlpha": 1.0,
        "outlineColor": "#000000",
        "outlineWidth": 3.0,
        "backColor": "#000000",
        "backAlpha": 0.0,
        "borderStyle": 1,
        "shadow": 2.0,
        "alignment": 2,
        "marginV": 50,
        "uppercase": True
    }
    ass_text = generate_ass_script(subs, styles)
    assert "[Script Info]" in ass_text
    assert "[V4+ Styles]" in ass_text
    assert "Montserrat" in ass_text
    assert "NAMASTE DOSTO, KAISE HAIN AAP?" in ass_text
    assert "Dialogue: 0,0:00:01.00,0:00:03.50,Default,,0,0,0,,NAMASTE DOSTO, KAISE HAIN AAP?" in ass_text


def test_export_ass_endpoint():
    client = app.test_client()
    payload = {
        "subtitles": [
            {
                "index": 1,
                "startTime": "00:00:01,000",
                "endTime": "00:00:02,000",
                "text": "Testing ASS endpoint"
            }
        ],
        "styles": {
            "fontName": "Inter",
            "fontSize": 28,
            "primaryColor": "#FFFFFF"
        },
        "filename": "test.ass"
    }
    response = client.post('/export-ass', json=payload)
    assert response.status_code == 200
    assert b"Testing ASS endpoint" in response.data


def test_async_export_and_progress_endpoints():
    client = app.test_client()
    # Test progress with invalid job_id
    res_404 = client.get('/export-progress/non-existent-job-id')
    assert res_404.status_code == 404

    # Test starting job without files
    res_bad = client.post('/start-export-video')
    assert res_bad.status_code == 400


if __name__ == '__main__':
    test_hex_to_ass_color()
    test_srt_time_to_ass_time()
    test_generate_ass_script()
    test_export_ass_endpoint()
    test_async_export_and_progress_endpoints()
    print("✓ All subtitle editor & export tests passed successfully!")
