import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation(output_path="output/Antenna_Array_Presentation.pptx"):
    prs = Presentation()
    # 16:9 widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # completely blank layout

    # Color Palette
    C_BG = RGBColor(15, 23, 42)          # Slate 900 #0F172A
    C_CARD = RGBColor(30, 41, 59)        # Slate 800 #1E293B
    C_CARD_BORDER = RGBColor(51, 65, 85) # Slate 700 #334155
    C_CYAN = RGBColor(14, 165, 233)      # Sky 500 #0EA5E9
    C_EMERALD = RGBColor(16, 185, 129)   # Emerald 500 #10B981
    C_WHITE = RGBColor(248, 250, 252)    # Slate 50 #F8FAFC
    C_MUTED = RGBColor(148, 163, 184)    # Slate 400 #94A3B8
    C_AMBER = RGBColor(245, 158, 11)     # Amber 500 #F59E0B

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background()
        return bg

    def add_card(slide, left, top, width, height, bg_color=C_CARD, border_color=C_CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.5)
        else:
            card.line.fill.background()
        return card

    def add_header(slide, title_text, category="LINEAR ANTENNA ARRAY SIMULATION"):
        # Category pill/subtitle
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_CYAN
        p_cat.font.name = "Arial"

        # Main Slide Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.6))
        tf = t_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.font.name = "Arial"

    # ==========================================
    # SLIDE 1: TITLE SLIDE
    # ==========================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1)

    # Accent decorative glow/bar
    glow = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.1), Inches(3.2))
    glow.fill.solid()
    glow.fill.fore_color.rgb = C_CYAN
    glow.line.fill.background()

    # Title box
    tbox = slide1.shapes.add_textbox(Inches(1.2), Inches(1.6), Inches(11.0), Inches(2.5))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "ELECTROMAGNETIC ENGINEERING & SIMULATION"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = C_CYAN
    p0.font.name = "Arial"
    p0.space_after = Pt(12)

    p1 = tf1.add_paragraph()
    p1.text = "Interactive Linear Antenna\nArray Simulation"
    p1.font.size = Pt(40)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    p1.font.name = "Arial"
    p1.space_after = Pt(14)

    p2 = tf1.add_paragraph()
    p2.text = "High-Precision Radiation Pattern Modeling, Real-Time Phased Beam Steering & Automated Metrics Analysis"
    p2.font.size = Pt(16)
    p2.font.color.rgb = C_MUTED
    p2.font.name = "Arial"

    # Bottom feature badges
    badges = [
        ("Uniform Linear Arrays (ULA)", "N = 2 to 64 Elements"),
        ("Dual Platform Deployment", "PyQt6 Desktop + Vercel Web SPA"),
        ("Analytical Physics Engine", "Summation & Closed-Form Singularity-Free"),
        ("Comprehensive Metrics", "HPBW, FNBW, PSLL & Grating Lobes")
    ]
    card_w = Inches(2.7)
    card_gap = Inches(0.25)
    for i, (b_title, b_sub) in enumerate(badges):
        bx = Inches(0.8) + i * (card_w + card_gap)
        by = Inches(5.3)
        add_card(slide1, bx, by, card_w, Inches(1.4))
        cbox = slide1.shapes.add_textbox(bx + Inches(0.15), by + Inches(0.15), card_w - Inches(0.3), Inches(1.1))
        ctf = cbox.text_frame
        ctf.word_wrap = True
        cp0 = ctf.paragraphs[0]
        cp0.text = b_title
        cp0.font.size = Pt(12)
        cp0.font.bold = True
        cp0.font.color.rgb = C_CYAN
        cp0.font.name = "Arial"
        cp0.space_after = Pt(4)
        cp1 = ctf.add_paragraph()
        cp1.text = b_sub
        cp1.font.size = Pt(10)
        cp1.font.color.rgb = C_WHITE
        cp1.font.name = "Arial"

    slide1.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT (Slide 1 - 2 mins):\n"
        "Welcome professors and evaluation committee. Today I am presenting our Interactive Antenna Array Simulator.\n"
        "Antenna arrays are the backbone of modern wireless infrastructure—from 5G massive MIMO and phased-array radar "
        "to satellite constellations like Starlink. Our project bridges rigorous electromagnetic theory and software engineering, "
        "providing a dual-platform tool (PyQt6 Desktop and Web SPA) that computes and visualizes radiation patterns in real-time."
    )

    # ==========================================
    # SLIDE 2: MATHEMATICAL FORMULATION
    # ==========================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2)
    add_header(slide2, "Mathematical Foundation: Governing Array Factor Physics")

    # 3 Column Cards
    col_w = Inches(3.7)
    col_gap = Inches(0.3)
    col_h = Inches(5.3)
    c_y = Inches(1.5)

    # Card 1: Geometry & Phase
    add_card(slide2, Inches(0.8), c_y, col_w, col_h)
    tb = slide2.shapes.add_textbox(Inches(1.0), c_y + Inches(0.2), col_w - Inches(0.4), col_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Geometry & Phase Shift"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p.space_after = Pt(12)

    bullets1 = [
        ("Coordinate System:", "Line source along z-axis. Observation angle θ measured from positive array axis (0° to 180°)."),
        ("Wave Number k:", "k = 2π / λ, where λ = c / f is the operating wavelength in free space."),
        ("Spatial-Electrical Phase ψ:", "ψ = k·d·cos(θ) + β\nAccounts for both spatial path delay (d·cos θ) and progressive excitation phase (β)."),
        ("Excitation Phase β:", "Applied per-element to steer the main beam to a desired angle θ₀:\nβ = -k·d·cos(θ₀)")
    ]
    for b_title, b_desc in bullets1:
        p_t = tf.add_paragraph()
        p_t.text = b_title
        p_t.font.bold = True
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = C_EMERALD
        p_d = tf.add_paragraph()
        p_d.text = b_desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_WHITE
        p_d.space_after = Pt(8)

    # Card 2: Array Factor Formulations
    add_card(slide2, Inches(0.8) + col_w + col_gap, c_y, col_w, col_h)
    tb = slide2.shapes.add_textbox(Inches(1.0) + col_w + col_gap, c_y + Inches(0.2), col_w - Inches(0.4), col_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. Array Factor Equations"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p.space_after = Pt(12)

    bullets2 = [
        ("Complex Summation:", "AF(θ) = Σₙ₌₀ᴺ⁻¹ aₙ · e^(j·n·ψ)\nSupports arbitrary element amplitude tapers aₙ."),
        ("Closed-Form Solution:", "|AF(θ)| = |sin(Nψ/2) / sin(ψ/2)|\nExact analytical solution for uniform excitation (aₙ = 1)."),
        ("Power Pattern & dB Scale:", "P(θ) = |AF_norm(θ)|²\nAF_dB = 20·log₁₀|AF_norm(θ)|\nClipped at selectable floor (-100 to -20 dB)."),
        ("Normalized Representation:", "AF_norm(θ) = AF(θ) / max(|AF|)\nEnsures global main beam is referenced to exactly 0 dB.")
    ]
    for b_title, b_desc in bullets2:
        p_t = tf.add_paragraph()
        p_t.text = b_title
        p_t.font.bold = True
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = C_EMERALD
        p_d = tf.add_paragraph()
        p_d.text = b_desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_WHITE
        p_d.space_after = Pt(8)

    # Card 3: Numerical Singularity Handling
    add_card(slide2, Inches(0.8) + 2*(col_w + col_gap), c_y, col_w, col_h)
    tb = slide2.shapes.add_textbox(Inches(1.0) + 2*(col_w + col_gap), c_y + Inches(0.2), col_w - Inches(0.4), col_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. Singularity Handling"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p.space_after = Pt(12)

    bullets3 = [
        ("Removable Singularities:", "When ψ → 2mπ, sin(ψ/2) → 0, yielding a 0/0 indeterminate form in the closed-form expression."),
        ("L'Hôpital's Exact Limit:", "lim_{ψ→2mπ} sin(Nψ/2)/sin(ψ/2) = N\nOur engine identifies |sin(ψ/2)| < 1e-12 and applies the analytical limit N."),
        ("Numerical Agreement:", "Verified that complex summation matches closed-form evaluation within relative error < 1e-10."),
        ("Zero-Crossing Safety:", "Avoids log₁₀(0) crashes by clamping |AF| to 1e-15 prior to decibel conversion.")
    ]
    for b_title, b_desc in bullets3:
        p_t = tf.add_paragraph()
        p_t.text = b_title
        p_t.font.bold = True
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = C_EMERALD
        p_d = tf.add_paragraph()
        p_d.text = b_desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_WHITE
        p_d.space_after = Pt(8)

    slide2.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT (Slide 2 - 3 mins):\n"
        "Here we establish our theoretical foundation. The total radiated field of a line array is the product of the single-element "
        "pattern and the Array Factor AF(θ). Note that θ is measured from the array axis (z-axis).\n"
        "The crucial parameter is ψ = kd cos(θ) + β. By adjusting the feed phase β, we control where constructive interference occurs.\n"
        "In software implementation, closed-form equations suffer from 0/0 indeterminate singularities at ψ = 2mπ. We implemented "
        "strict L'Hôpital resolution (|AF|=N), guaranteeing crash-free execution and 1e-10 precision against complex summation."
    )

    # ==========================================
    # SLIDE 3: ARCHITECTURE & INTERACTIVE CONTROLS
    # ==========================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3)
    add_header(slide3, "System Architecture: Decoupled Multi-Layer Design")

    # 2 Big Cards: Left = Architecture Layers, Right = Automated Numerical Metrics & Tapering
    w_left = Inches(5.7)
    w_right = Inches(5.7)
    h_body = Inches(5.3)

    # Left: Architecture
    add_card(slide3, Inches(0.8), c_y, w_left, h_body)
    tb = slide3.shapes.add_textbox(Inches(1.0), c_y + Inches(0.2), w_left - Inches(0.4), h_body - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Modular Multi-Layer Architecture"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p.space_after = Pt(12)

    arch_layers = [
        ("Core Computational Engine (core/):", "Pure Python & NumPy routines. Closed-form AF, complex summation, phase propagation, and window tapering functions with zero GUI coupling."),
        ("Automated Metrics Extractor (analysis/):", "Sub-grid interpolation for accurate Half-Power Beamwidth (HPBW), First-Null Beamwidth (FNBW), Peak Sidelobe Level (PSLL), and visible grating lobe detection."),
        ("Desktop Presentation (PyQt6 & Matplotlib):", "Fully interactive desktop GUI: 4 synchronized control panels, 2D Cartesian, Polar, and 3D radiation plots, HTML5 array geometry view, dark/light themes."),
        ("Zero-Config Web SPA (Vercel Edge):", "Client-side high-performance JavaScript engine running Plotly.js charts at 60 FPS, eliminating server cold starts and lambda bundle limits.")
    ]
    for l_title, l_desc in arch_layers:
        p_t = tf.add_paragraph()
        p_t.text = l_title
        p_t.font.bold = True
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = C_EMERALD
        p_d = tf.add_paragraph()
        p_d.text = l_desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_WHITE
        p_d.space_after = Pt(8)

    # Right: Controls & Metrics
    add_card(slide3, Inches(0.8) + w_left + Inches(0.3), c_y, w_right, h_body)
    tb = slide3.shapes.add_textbox(Inches(1.0) + w_left + Inches(0.3), c_y + Inches(0.2), w_right - Inches(0.4), h_body - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Real-Time Controls & Metrics Engine"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p.space_after = Pt(12)

    controls_info = [
        ("Continuous Parameter Sliders:", "• Elements N: 2 to 64\n• Spacing d/λ: 0.05 to 2.00 (with live mm display)\n• Phase β: -360° to +360°\n• Steering Angle θ₀: 0° to 180°\n• Frequency: 0.1 to 30.0 GHz"),
        ("One-Click Presets & Animation:", "• Broadside (θ₀ = 90°, β = 0°)\n• Positive End-Fire (θ₀ = 0°, β = -kd)\n• Negative End-Fire (θ₀ = 180°, β = +kd)\n• Continuous dynamic beam scanning animation"),
        ("Live Numerical Analysis Panel:", "Outputs exact Beam Peak angle, HPBW (-3 dB width), FNBW (null-to-null width), PSLL in dB, visible null count, and visible grating lobe count without manual curve reading."),
        ("Amplitude Tapering Windows:", "Uniform (maximum directivity), Hann/Cosine (-31.5 dB sidelobes), and Binomial (zero sidelobes for d ≤ λ/2).")
    ]
    for c_title, c_desc in controls_info:
        p_t = tf.add_paragraph()
        p_t.text = c_title
        p_t.font.bold = True
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = C_EMERALD
        p_d = tf.add_paragraph()
        p_d.text = c_desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_WHITE
        p_d.space_after = Pt(6)

    slide3.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT (Slide 3 - 3 mins):\n"
        "Turning to software architecture, we adhered strictly to Model-View-Controller principles.\n"
        "Notice the complete separation: our core physics routines have zero dependency on Qt or Matplotlib, "
        "which allowed us to port the exact same analytical mathematics into our standalone Web SPA running on Vercel.\n"
        "The control panel provides real-time slider and spinbox synchronization. Whenever frequency changes, the physical "
        "spacing d in millimeters updates dynamically based on the calculated wavelength."
    )

    # ==========================================
    # SLIDE 4: BENCHMARK EXPERIMENTS & PHYSICAL INSIGHTS
    # ==========================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4)
    add_header(slide4, "Experimental Verification: The 4 Core Antenna Phenomena")

    # 4 Grid Cards (2x2)
    grid_w = Inches(5.7)
    grid_h = Inches(2.5)
    g_gap_x = Inches(0.3)
    g_gap_y = Inches(0.3)

    experiments = [
        ("Experiment 1: N-Scaling & Beam Sharpening",
         "N = 2, 4, 8, 16, 32, 64 (d = 0.5λ, β = 0°)",
         "• HPBW narrows proportionally to 1/N (from ~50° down to ~3.2° for N=32).\n"
         "• Directivity increases linearly with element count N.\n"
         "• First sidelobe remains fixed at theoretical -13.26 dB for uniform excitation.\n"
         "• Visible null count equals exactly N - 1."),

        ("Experiment 2: Spacing & Grating Lobes",
         "d/λ = 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0 (N = 8)",
         "• For d < 0.5λ: Single broadside beam, no grating lobes.\n"
         "• At d = 1.0λ: Grating lobes emerge at end-fire angles (0° and 180°) at 0 dB.\n"
         "• For d > 1.0λ: Multiple equal-amplitude grating lobes alias into visible space.\n"
         "• Condition to prevent grating lobes: d/λ < 1 / (1 + |cos θ₀|)."),

        ("Experiment 3: Phased Beam Steering",
         "Steering angles θ₀ = 0°, 30°, 45°, 60°, 90°, 120°, 180°",
         "• Electronic scanning achieved via linear phase progression β = -kd cos(θ₀).\n"
         "• Beam broadening observed away from broadside: HPBW(θ₀) ≈ HPBW_broadside / sin(θ₀).\n"
         "• Effective array aperture decreases from L to L·sin(θ₀).\n"
         "• End-fire beams (0° & 180°) exhibit the widest main lobes."),

        ("Experiment 4: Amplitude Window Tapering",
         "Uniform vs. Hann (Cosine) vs. Binomial (N = 8, d = 0.5λ)",
         "• Uniform: Narrowest beam (HPBW = 12.8°), highest sidelobes (-13.26 dB).\n"
         "• Hann: Sidelobes suppressed to -31.5 dB; HPBW broadens by ~35% (17.5°).\n"
         "• Binomial: Complete elimination of sidelobes; widest main beam (HPBW ~ 25°).\n"
         "• Demonstrates the fundamental engineering trade-off: resolution vs. interference.")
    ]

    for idx, (e_title, e_sub, e_bullets) in enumerate(experiments):
        row = idx // 2
        col = idx % 2
        ex = Inches(0.8) + col * (grid_w + g_gap_x)
        ey = c_y + row * (grid_h + g_gap_y)

        add_card(slide4, ex, ey, grid_w, grid_h)
        tb = slide4.shapes.add_textbox(ex + Inches(0.2), ey + Inches(0.15), grid_w - Inches(0.4), grid_h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p0 = tf.paragraphs[0]
        p0.text = e_title
        p0.font.size = Pt(12)
        p0.font.bold = True
        p0.font.color.rgb = C_CYAN

        p1 = tf.add_paragraph()
        p1.text = e_sub
        p1.font.size = Pt(9)
        p1.font.bold = True
        p1.font.color.rgb = C_AMBER
        p1.space_after = Pt(4)

        p2 = tf.add_paragraph()
        p2.text = e_bullets
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = C_WHITE

    slide4.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT (Slide 4 - 4 mins):\n"
        "This slide encapsulates the 4 primary electromagnetic phenomena verified in our live simulation:\n"
        "1. Element Count: Increasing N sharpens the main beam inversely (1/N) while clamping the first sidelobe at -13.26 dB.\n"
        "2. Element Spacing: Spacing d >= 1.0 lambda introduces spatial aliasing, generating unwanted 0 dB grating lobes.\n"
        "3. Phased Steering: Demonstrates how linear phase shift beta steers the beam, and why the beam broadens by 1/sin(theta_0).\n"
        "4. Tapering: Proves the classic engineering compromise: Hann tapering achieves -31.5 dB sidelobe suppression at the cost of a slightly wider beam."
    )

    # ==========================================
    # SLIDE 5: VERIFICATION, TESTING & APPLICATIONS
    # ==========================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5)
    add_header(slide5, "Verification Rigor, Real-World Applications & Conclusion")

    # 3 Cards
    add_card(slide5, Inches(0.8), c_y, col_w, col_h)
    tb = slide5.shapes.add_textbox(Inches(1.0), c_y + Inches(0.2), col_w - Inches(0.4), col_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Automated Test Suite"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p.space_after = Pt(12)

    verif_items = [
        ("81 / 81 Tests Passing:", "Exhaustive pytest suite covering unit, integration, and edge-case validation."),
        ("Physics Engine Precision:", "Zero-error check between closed-form and summation across all valid N and d/λ."),
        ("Singularity & Edge Cases:", "Tests boundary angles (0°, 180°), phase wrapping (-360° to +360°), and removable singularities."),
        ("GUI & Input Sync:", "Verified slider-spinbox bidirectional updates, invalid input rejections, and theme toggling.")
    ]
    for v_title, v_desc in verif_items:
        p_t = tf.add_paragraph()
        p_t.text = v_title
        p_t.font.bold = True
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = C_EMERALD
        p_d = tf.add_paragraph()
        p_d.text = v_desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_WHITE
        p_d.space_after = Pt(8)

    add_card(slide5, Inches(0.8) + col_w + col_gap, c_y, col_w, col_h)
    tb = slide5.shapes.add_textbox(Inches(1.0) + col_w + col_gap, c_y + Inches(0.2), col_w - Inches(0.4), col_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. Real-World Engineering"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p.space_after = Pt(12)

    apps = [
        ("5G / 6G Massive MIMO:", "Enables multi-user beamforming, spatial multiplexing, and dynamic null-steering to cancel co-channel interference."),
        ("Phased-Array Radar (AESA):", "Inertia-free electronic scanning allows simultaneous multi-target tracking and missile defense surveillance."),
        ("LEO Satellite Communications:", "Ground terminals (e.g., Starlink) dynamically track low-earth orbit satellites without mechanical gimbals."),
        ("Radio Astronomy & Imaging:", "Interferometric arrays synthesize kilometer-scale effective apertures for deep-space observation.")
    ]
    for a_title, a_desc in apps:
        p_t = tf.add_paragraph()
        p_t.text = a_title
        p_t.font.bold = True
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = C_EMERALD
        p_d = tf.add_paragraph()
        p_d.text = a_desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_WHITE
        p_d.space_after = Pt(8)

    add_card(slide5, Inches(0.8) + 2*(col_w + col_gap), c_y, col_w, col_h)
    tb = slide5.shapes.add_textbox(Inches(1.0) + 2*(col_w + col_gap), c_y + Inches(0.2), col_w - Inches(0.4), col_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. Project Summary"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p.space_after = Pt(12)

    summary_items = [
        ("100% Requirement Compliance:", "Satisfied all requirements specified in the project charter and academic brief."),
        ("Dual-Platform Accessibility:", "Seamless transition between desktop Python application and global Vercel cloud deployment."),
        ("Interactive Pedagogical Tool:", "Bridges abstract electromagnetic theory with intuitive, real-time visualization."),
        ("Live Demo & Codebase:", "Open-source codebase on GitHub with automated CI/CD and comprehensive audit documentation.")
    ]
    for s_title, s_desc in summary_items:
        p_t = tf.add_paragraph()
        p_t.text = s_title
        p_t.font.bold = True
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = C_EMERALD
        p_d = tf.add_paragraph()
        p_d.text = s_desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = C_WHITE
        p_d.space_after = Pt(8)

    slide5.notes_slide.notes_text_frame.text = (
        "SPEAKER SCRIPT (Slide 5 - 3 mins):\n"
        "To conclude, our simulator has undergone rigorous engineering validation, backed by an 81-test automated suite.\n"
        "The principles modeled here directly empower 5G Massive MIMO beamforming, Active Electronically Scanned Array (AESA) radar, "
        "and satellite communication systems.\n"
        "We are now ready for the live demonstration and welcome questions from the evaluation committee. Thank you!"
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "output/Antenna_Array_Presentation.pptx"
    build_presentation(out_file)
