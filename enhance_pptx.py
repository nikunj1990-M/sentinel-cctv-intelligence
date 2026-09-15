from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import copy

PATH = "Sentinel_Presentation.pptx"
prs = Presentation(PATH)

# ---- palette (extracted from existing deck) ----
BG = RGBColor(0x0B, 0x11, 0x1C)
CARD = RGBColor(0x14, 0x22, 0x3A)
CARD_ALT = RGBColor(0x18, 0x2C, 0x4C)
BORDER_SOFT = RGBColor(0x18, 0x2C, 0x4C)
BLUE = RGBColor(0x2B, 0x8C, 0xFF)
CYAN = RGBColor(0x25, 0xD8, 0xF0)
GREEN = RGBColor(0x2A, 0xD4, 0x77)
AMBER = RGBColor(0xF5, 0xB6, 0x38)
RED = RGBColor(0xFF, 0x3B, 0x5C)
WHITE = RGBColor(0xEA, 0xF1, 0xFA)
MUTED = RGBColor(0x93, 0xA9, 0xC2)
DARK_ON_BRIGHT = RGBColor(0x0B, 0x11, 0x1C)
FONT = "Segoe UI"

blank_layout = None
for layout in prs.slide_layouts:
    if layout.name == "Blank":
        blank_layout = layout
        break
if blank_layout is None:
    blank_layout = prs.slide_layouts[6]


def set_bg(slide):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = BG


def add_rect(slide, left, top, width, height, fill=None, line=None, line_w=Emu(12700), shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    sp = slide.shapes.add_shape(shape, Emu(left), Emu(top), Emu(width), Emu(height))
    sp.fill.solid()
    if fill is not None:
        sp.fill.fore_color.rgb = fill
    else:
        sp.fill.background()
    if line is not None:
        sp.line.color.rgb = line
        sp.line.width = line_w
    else:
        sp.line.fill.background()
    sp.shadow.inherit = False
    return sp


def add_text(slide, left, top, width, height, lines, valign=None, align=PP_ALIGN.LEFT):
    """lines: list of (text, size_pt, bold, color, font=None) tuples, one per paragraph."""
    tb = slide.shapes.add_textbox(Emu(left), Emu(top), Emu(width), Emu(height))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, (text, size, bold, color) in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.name = FONT
        run.font.color.rgb = color
    return tb


def add_eyebrow_title(slide, eyebrow, title):
    add_text(slide, 822960, 502920, 10058400, 365760, [(eyebrow, 13, True, CYAN)])
    add_text(slide, 822960, 914400, 10515600, 640080, [(title, 26, True, WHITE)])


def add_footer(slide, page_num):
    add_text(slide, 822960, 6419088, 7315200, 320040,
             [("SENTINEL  ·  Gujarat Police Innovation Hackathon 2026", 10, False, MUTED)])
    add_text(slide, 11430000, 6419088, 548640, 320040,
             [(str(page_num), 10, False, MUTED)], align=PP_ALIGN.RIGHT)


# =========================================================
# NEW SLIDE: PREDICTIVE POLICING & DRONE RESPONSE
# =========================================================
s = prs.slides.add_slide(blank_layout)
set_bg(s)
add_eyebrow_title(s, "PREDICTIVE POLICING & AUTONOMOUS RESPONSE",
                   "From last-seen to intercepted — before it arrives")

col_w = 5120640
col_h = 3931920
gap = 182880
left1 = 868680
left2 = left1 + col_w + gap
top = 1874519

# Column 1 — Predictive next-camera
add_rect(s, left1, top, col_w, col_h, fill=CARD_ALT, line=BLUE)
add_text(s, left1 + 274320, top + 182880, col_w - 548640, 365760,
         [("PREDICTIVE NEXT-CAMERA", 14, True, CYAN)])
bullets1 = [
    "•  Scores every camera in range by direction + distance from the vehicle's last sighting",
    "",
    "•  score = 0.6 × bearing alignment + 0.4 × proximity  (haversine distance + compass bearing)",
    "",
    "•  Predicted camera and ETA appear instantly on the live map — an amber marker + dotted path",
    "",
    "•  No manual guesswork: patrol units know exactly where to look next",
]
tb = add_text(s, left1 + 274320, top + 685800, col_w - 548640, col_h - 914400,
              [(bullets1[0], 15, False, WHITE)])
tf = tb.text_frame
for line in bullets1[1:]:
    p = tf.add_paragraph()
    run = p.add_run()
    run.text = line
    run.font.size = Pt(15)
    run.font.name = FONT
    run.font.color.rgb = WHITE if line.strip() else WHITE

# Column 2 — Drone dispatch
add_rect(s, left2, top, col_w, col_h, fill=CARD_ALT, line=GREEN)
add_text(s, left2 + 274320, top + 182880, col_w - 548640, 365760,
         [("AUTONOMOUS DRONE DISPATCH", 14, True, GREEN)])
bullets2 = [
    "•  One click on any alert dispatches a drone toward the interception point",
    "",
    "•  Simulated flight path animates in real time, with a live trailing route on the map",
    "",
    "•  Status panel shows next waypoint, live ETA and a one-click recall",
    "",
    "•  Integration-ready for real hardware via MAVLink / DJI SDK",
]
tb2 = add_text(s, left2 + 274320, top + 685800, col_w - 548640, col_h - 914400,
               [(bullets2[0], 15, False, WHITE)])
tf2 = tb2.text_frame
for line in bullets2[1:]:
    p = tf2.add_paragraph()
    run = p.add_run()
    run.text = line
    run.font.size = Pt(15)
    run.font.name = FONT
    run.font.color.rgb = WHITE

# Bottom highlight bar
bar = add_rect(s, 868680, 5931408, 10424160, 365760, fill=CARD_ALT, line=AMBER)
add_text(s, 868680, 5931408, 10424160, 365760,
          [("★  Sentinel doesn't just alert — it predicts where the target is going, and can act on it.",
            13, True, AMBER)], align=PP_ALIGN.CENTER)

add_footer(s, 8)

# =========================================================
# NEW SLIDE: PRODUCT IN ACTION (real screenshots)
# =========================================================
s2 = prs.slides.add_slide(blank_layout)
set_bg(s2)
add_eyebrow_title(s2, "PRODUCT IN ACTION",
                   "Real screens, real detections — captured from the running system")

img_w = 4700000
img_h = int(img_w * 1536 / 2048)  # true 4:3 content aspect (no pillarbox bars)
img_top = 1655760
gap = 182880
content_left = 868680
content_w = 10424160
pair_w = img_w * 2 + gap
img_left1 = content_left + (content_w - pair_w) // 2
img_left2 = img_left1 + img_w + gap

frame_pad = 27432
add_rect(s2, img_left1 - frame_pad, img_top - frame_pad, img_w + 2 * frame_pad, img_h + 2 * frame_pad,
         fill=None, line=BORDER_SOFT, shape=MSO_SHAPE.RECTANGLE)
add_rect(s2, img_left2 - frame_pad, img_top - frame_pad, img_w + 2 * frame_pad, img_h + 2 * frame_pad,
         fill=None, line=BORDER_SOFT, shape=MSO_SHAPE.RECTANGLE)
s2.shapes.add_picture("demo_assets/gis_route_crop.png", Emu(img_left1), Emu(img_top), Emu(img_w), Emu(img_h))
s2.shapes.add_picture("demo_assets/predict_drone_crop.png", Emu(img_left2), Emu(img_top), Emu(img_w), Emu(img_h))

cap_top = img_top + img_h + 91440
add_text(s2, img_left1, cap_top, img_w, 365760,
         [("Cross-camera alert + automatic route reconstruction", 13, True, CYAN)], align=PP_ALIGN.CENTER)
add_text(s2, img_left2, cap_top, img_w, 365760,
         [("Predictive next-camera + one-click drone dispatch", 13, True, CYAN)], align=PP_ALIGN.CENTER)

bar_top = cap_top + 365760 + 137160
add_rect(s2, 868680, bar_top, 10424160, 548640, fill=CARD_ALT, line=GREEN)
add_text(s2, 868680, bar_top, 10424160, 548640,
          [("Also live on the same dashboard: natural-language video search across every camera, and a full camera registry with live health status.",
            13, True, GREEN)], align=PP_ALIGN.CENTER)

add_footer(s2, 9)

# =========================================================
# Reorder: move the two new slides to positions 8 and 9 (1-indexed)
# =========================================================
xml_slides = prs.slides._sldIdLst
slides_list = list(xml_slides)
new1 = slides_list[-2]
new2 = slides_list[-1]
xml_slides.remove(new1)
xml_slides.remove(new2)
xml_slides.insert(7, new1)   # becomes slide 8
xml_slides.insert(8, new2)  # becomes slide 9

# =========================================================
# Renumber footer page numbers for all slides after insertion
# =========================================================
for idx, slide in enumerate(prs.slides):
    page_no = idx + 1
    for shape in slide.shapes:
        if shape.has_text_frame and shape.text_frame.text.strip().isdigit():
            # only touch shapes that are clearly a lone page-number box (small width)
            if shape.width and shape.width < 900000:
                shape.text_frame.paragraphs[0].runs[0].text = str(page_no)

prs.save("Sentinel_Presentation.pptx")
print("Saved. Total slides:", len(prs.slides))
