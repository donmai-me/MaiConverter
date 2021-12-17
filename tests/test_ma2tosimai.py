from maiconverter.maima2 import MaiMa2
from maiconverter.converter import ma2_to_simai


def test_slide360_conversion():
    """Tests whether a ma2 360 degree slide is properly converted in Simai.
    Addresses https://github.com/donmai-me/MaiConverter/issues/9"""
    ma2_cw_360_1 = MaiMa2()
    ma2_cw_360_1.set_bpm(0.0, 120)
    ma2_cw_360_1.add_slide(1.0, 1, 1, 1.0, 3)  # Pattern 3 is CW

    ma2_cw_360_2 = MaiMa2()
    ma2_cw_360_2.set_bpm(0.0, 120)
    ma2_cw_360_2.add_slide(1.0, 4, 4, 1.0, 3)  # Pattern 3 is CW

    ma2_ccw_360_1 = MaiMa2()
    ma2_ccw_360_1.set_bpm(0.0, 120)
    ma2_ccw_360_1.add_slide(1.0, 1, 1, 1.0, 2)  # Pattern 2 is CCW

    ma2_ccw_360_2 = MaiMa2()
    ma2_ccw_360_2.set_bpm(0.0, 120)
    ma2_ccw_360_2.add_slide(1.0, 4, 4, 1.0, 2)  # Pattern 2 is CCW

    simai_cw_360_1 = ma2_to_simai(ma2_cw_360_1)
    assert len(simai_cw_360_1.notes) == 1
    simai_cw_360_slide = simai_cw_360_1.notes[0]
    assert simai_cw_360_slide.position == simai_cw_360_slide.end_position
    assert simai_cw_360_slide.pattern == ">"

    simai_cw_360_2 = ma2_to_simai(ma2_cw_360_2)
    assert len(simai_cw_360_2.notes) == 1
    simai_cw_360_slide = simai_cw_360_2.notes[0]
    assert simai_cw_360_slide.position == simai_cw_360_slide.end_position
    assert simai_cw_360_slide.pattern == "<"

    simai_ccw_360_1 = ma2_to_simai(ma2_ccw_360_1)
    assert len(simai_ccw_360_1.notes) == 1
    simai_ccw_360_slide = simai_ccw_360_1.notes[0]
    assert simai_ccw_360_slide.position == simai_ccw_360_slide.end_position
    assert simai_ccw_360_slide.pattern == "<"

    simai_ccw_360_2 = ma2_to_simai(ma2_ccw_360_2)
    assert len(simai_ccw_360_2.notes) == 1
    simai_ccw_360_slide = simai_ccw_360_2.notes[0]
    assert simai_ccw_360_slide.position == simai_ccw_360_slide.end_position
    assert simai_ccw_360_slide.pattern == ">"
