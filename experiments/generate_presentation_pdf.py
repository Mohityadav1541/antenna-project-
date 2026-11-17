"""
Generates the comprehensive 20-minute Presentation Guide PDF:
- Complete minute-by-minute timeline (00:00 - 20:00)
- Spoken presenter script for each segment
- Exact live demo walkthrough actions with parameters & expected outputs
- Comprehensive viva voce Q&A with mathematical proofs
- Presenter emergency cue card & timing checklist
"""

import os
import sys
from pathlib import Path
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

OUTPUT_PDF = project_root / "output" / "Antenna_Array_20Min_Presentation_Guide.pdf"

def setup_page(fig, page_num, total_pages, title, subtitle, time_badge=None):
    fig.patch.set_facecolor("#ffffff")
    
    # Top banner bar
    top_bar = fig.add_axes([0.08, 0.94, 0.84, 0.038])
    top_bar.axis("off")
    top_bar.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02,rounding_size=0.15",
                                     facecolor="#0f172a", edgecolor="none"))
    top_bar.text(0.025, 0.5, "ANTENNA ARRAY SIMULATION  |  20-MINUTE PRESENTATION & VIVA MASTER GUIDE",
                 color="#38bdf8", fontsize=8.5, weight="bold", va="center")
    if time_badge:
        top_bar.text(0.975, 0.5, time_badge, color="#fbbf24", fontsize=8.5, weight="bold",
                     ha="right", va="center")
    
    # Page Title & Subtitle
    fig.text(0.08, 0.905, title, fontsize=15, weight="bold", color="#0f172a")
    fig.text(0.08, 0.885, subtitle, fontsize=9.5, color="#475569")
    
    # Divider line
    fig.text(0.08, 0.875, "—" * 68, fontsize=10, color="#cbd5e1")
    
    # Bottom footer
    fig.text(0.08, 0.035, "Interactive Antenna Array Simulation — Academic Defense & Presentation Protocol",
             fontsize=8, color="#64748b")
    fig.text(0.92, 0.035, f"Page {page_num} of {total_pages}", fontsize=8, color="#64748b", ha="right")

def draw_card(ax, x, y, w, h, bg="#f8fafc", border="#cbd5e1", title="", title_color="#0284c7"):
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.02",
                           facecolor=bg, edgecolor=border, linewidth=1.2)
    ax.add_patch(patch)
    if title:
        ax.text(x + 0.02, y + h - 0.04, title, fontsize=10.5, weight="bold", color=title_color)

def generate_guide_pdf():
    os.makedirs(OUTPUT_PDF.parent, exist_ok=True)
    pdf = PdfPages(str(OUTPUT_PDF))
    total_pages = 5

    # ==========================================
    # PAGE 1: TIMELINE ROADMAP & SEGMENT 1 (00:00 - 03:00)
    # ==========================================
    fig1 = plt.figure(figsize=(8.5, 11))
    setup_page(fig1, 1, total_pages,
               "Master 20-Minute Timeline & Theoretical Foundation",
               "Executive timing schedule and electromagnetics physics speech",
               "TIMELINE & THEORY (00:00 - 03:00)")
    ax1 = fig1.add_axes([0.08, 0.06, 0.84, 0.80])
    ax1.axis("off")
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)

    # Master Timeline Table Card
    draw_card(ax1, 0, 0.69, 1.0, 0.30, bg="#f1f5f9", border="#0284c7",
              title="1. EXECUTIVE 20-MINUTE TIMING SCHEDULE", title_color="#0f172a")
    
    timeline_items = [
        ("00:00 - 03:00 (3 mins)", "Segment 1: Theory & Physics Formulations",
         "Introduction, ULA geometry, Array Factor, psi, beta, closed-form & L'Hopital rule."),
        ("03:00 - 07:00 (4 mins)", "Segment 2: Software Architecture & UI Design",
         "Decoupled MVC architecture, 81/81 test suite, zero-scroll layout, desktop & Vercel web SPA."),
        ("07:00 - 15:00 (8 mins)", "Segment 3: Live Demonstration of 4 Key Phenomena",
         "Broadside baseline, N-scaling, phased beam steering, grating lobe onset, and Hann tapering."),
        ("15:00 - 20:00 (5 mins)", "Segment 4: Viva Voce & Technical Defense Q&A",
         "Answering faculty questions with mathematical proofs, boundary analysis, and applications.")
    ]
    y_pos = 0.89
    for t_time, t_title, t_desc in timeline_items:
        ax1.text(0.02, y_pos, t_time, fontsize=8.5, weight="bold", color="#0284c7")
        ax1.text(0.24, y_pos, t_title, fontsize=8.5, weight="bold", color="#0f172a")
        ax1.text(0.24, y_pos - 0.022, t_desc, fontsize=7.8, color="#475569")
        y_pos -= 0.052

    # Segment 1 Card: Spoken Script & Physics
    draw_card(ax1, 0, 0.02, 1.0, 0.65, bg="#ffffff", border="#cbd5e1",
              title="2. SEGMENT 1 SCRIPT: THEORY & FORMULATIONS (00:00 - 03:00)", title_color="#0284c7")

    speech1 = (
        '"Good morning, respected professors and evaluation committee. Today, I am presenting our Interactive '
        'Antenna Array Simulation platform, engineered for high-precision radiation modeling, phased-array beam '
        'steering, and automated electromagnetic analysis.\n\n'
        'In modern communication systems—such as 5G massive MIMO, active phased radar, and Starlink satellite '
        'terminals—individual antenna elements lack sufficient directivity. By arranging N isotropic elements into '
        'a Uniform Linear Array (ULA) along the z-axis and controlling their relative feed phase beta and amplitude '
        'weights a_n, we achieve dynamic electronic beam steering without mechanical gimbals.\n\n'
        'Our computational engine models the total radiated field via the Array Factor (AF):"'
    )
    ax1.text(0.02, 0.60, speech1, fontsize=8.2, color="#1e293b", wrap=True, va="top")

    # Formula Box
    draw_card(ax1, 0.02, 0.22, 0.96, 0.17, bg="#0f172a", border="#38bdf8",
              title="GOVERNING ELECTROMAGNETIC EQUATIONS", title_color="#38bdf8")
    formulas = [
        "Spatial-Electrical Phase:    psi = k*d*cos(theta) + beta       [k = 2*pi / lambda,  lambda = c / f]",
        "Excitation Steering Phase:   beta = -k*d*cos(theta_0)          [theta_0: Desired Main Beam Angle]",
        "Complex Summation:          AF(theta) = sum_{n=0}^{N-1} a_n * exp(j * n * psi)",
        "Closed-Form (Uniform):       |AF(theta)| = |sin(N*psi/2) / sin(psi/2)|",
        "L'Hopital Singularity Limit:  lim_{psi -> 2m*pi} |AF(theta)| = N     [Removes 0/0 indeterminate crashes]"
    ]
    f_y = 0.33
    for f in formulas:
        ax1.text(0.04, f_y, f, fontsize=7.8, family="monospace", weight="bold", color="#f8fafc")
        f_y -= 0.026

    key_points1 = (
        "Key Points to Emphasize to the Examiner:\n"
        "1. Angle theta is measured from the array axis (z-axis), meaning theta=90 deg is broadside, theta=0 deg is positive end-fire.\n"
        "2. The array factor is normalized so the main beam maximum is referenced to exactly 0 dB (AF_dB = 20*log10(|AF_norm|)).\n"
        "3. Removable singularities at psi = 2m*pi are resolved using strict analytical limits, ensuring zero NaN crashes."
    )
    ax1.text(0.02, 0.18, key_points1, fontsize=8.0, color="#0369a1", weight="bold", wrap=True, va="top")

    pdf.savefig(fig1)
    plt.close(fig1)

    # ==========================================
    # PAGE 2: SEGMENT 2 ARCHITECTURE & CONTROLS (03:00 - 07:00)
    # ==========================================
    fig2 = plt.figure(figsize=(8.5, 11))
    setup_page(fig2, 2, total_pages,
               "Software Architecture & Interface Engineering",
               "Decoupled MVC architecture, controls synchronization, and test validation",
               "ARCHITECTURE (03:00 - 07:00)")
    ax2 = fig2.add_axes([0.08, 0.06, 0.84, 0.80])
    ax2.axis("off")
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)

    # Architecture Overview Card
    draw_card(ax2, 0, 0.54, 1.0, 0.45, bg="#ffffff", border="#cbd5e1",
              title="1. DECOUPLED MULTI-LAYER ARCHITECTURE", title_color="#0284c7")

    speech2 = (
        '"To guarantee engineering rigor, we structured the software under a clean Model-View-Controller paradigm:\n\n'
        '• Core Computational Engine (core/): Pure NumPy implementation evaluating analytical array factor formulations, '
        'phase delays, and window tapering weights (Uniform, Hann, Binomial) with zero GUI dependency.\n'
        '• Automated Metrics Extractor (analysis/): Fast sub-grid numerical routines calculating exact Half-Power '
        'Beamwidth (HPBW, -3 dB width), First-Null Beamwidth (FNBW), Peak Sidelobe Level (PSLL), and visible grating lobes.\n'
        '• Dual Presentation Platforms: A native desktop GUI built with PyQt6 and Matplotlib, alongside a zero-config '
        'Web Single Page Application deployed to Vercel running Plotly.js at 60 FPS.\n'
        '• Automated Verification Suite: 81 passing unit and integration tests covering numerical tolerances, edge '
        'angles, phase wrapping, and UI synchronization."'
    )
    ax2.text(0.02, 0.93, speech2, fontsize=8.2, color="#1e293b", wrap=True, va="top")

    # UI Controls & Zero-Scroll Card
    draw_card(ax2, 0, 0.02, 1.0, 0.50, bg="#f8fafc", border="#cbd5e1",
              title="2. REAL-TIME CONTROLS, SYNCHRONIZATION & ZERO-SCROLL LAYOUT", title_color="#0284c7")

    ui_text = (
        "Presenter Spoken Walkthrough:\n"
        '"When designing the user interface, we prioritized ergonomics and readability:\n'
        '1. Bidirectional Synchronization: Sliders and spinboxes are linked bidirectionally. Adjusting slider N from '
        '2 to 64 immediately updates the numeric spinbox, recomputes the array factor, and re-renders the graphs.\n'
        '2. Dynamic mm Readout: Whenever the frequency (0.1 to 30 GHz) or d/lambda changes, the interface automatically '
        'displays the physical wavelength and element spacing in millimeters (e.g., at 2.4 GHz and d=0.5 lambda, '
        'spacing is exactly 62.5 mm).\n'
        '3. Zero-Scroll Architecture: The desktop window is engineered with optimized dock spacing and a high-contrast '
        'theme so all 4 control panels, 3 live plots, array geometry canvas, and numerical metrics are visible simultaneously '
        'without any scrollbars during evaluation.\n'
        '4. Theme Flexibility: Built-in dark and light theme toggle ensures clear projection regardless of room lighting."'
    )
    ax2.text(0.02, 0.46, ui_text, fontsize=8.2, color="#1e293b", wrap=True, va="top")

    # Summary table box
    draw_card(ax2, 0.02, 0.04, 0.96, 0.17, bg="#ffffff", border="#0284c7",
              title="SYNCHRONIZED CONTROL SPECIFICATIONS", title_color="#0284c7")
    specs = [
        "Elements N: 2 - 64  |  Spacing d/lambda: 0.05 - 2.00  |  Progressive Phase beta: -360 deg to +360 deg",
        "Steering Angle theta_0: 0 deg - 180 deg  |  Frequency: 0.1 - 30.0 GHz  |  Sampling Step: 0.01 deg - 2.00 deg",
        "Presets: Broadside (90 deg, 0 deg)  |  +End-Fire (0 deg, -kd)  |  -End-Fire (180 deg, +kd)  |  Auto-Steer",
        "Tapering Windows: Uniform (-13.26 dB PSLL), Hann/Cosine (-31.5 dB PSLL), Binomial (Zero Sidelobes)"
    ]
    s_y = 0.16
    for s in specs:
        ax2.text(0.04, s_y, s, fontsize=7.6, family="monospace", color="#0f172a")
        s_y -= 0.026

    pdf.savefig(fig2)
    plt.close(fig2)

    # ==========================================
    # PAGE 3: SEGMENT 3 LIVE DEMO SCRIPT (07:00 - 15:00)
    # ==========================================
    fig3 = plt.figure(figsize=(8.5, 11))
    setup_page(fig3, 3, total_pages,
               "Step-by-Step Live Demonstration Protocol",
               "Exact actions, parameters, expected numerical outputs, and verbal commentary",
               "LIVE DEMO (07:00 - 15:00)")
    ax3 = fig3.add_axes([0.08, 0.06, 0.84, 0.80])
    ax3.axis("off")
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)

    demos = [
        ("DEMO 1: Broadside Benchmark", "07:00 - 08:30 (1.5 min)",
         "Action: Click 'Broadside' preset button.\n"
         "Parameters: N = 8, d/lambda = 0.5, beta = 0 deg, f = 2.4 GHz.\n"
         "Expected Readout: Main beam at theta = 90.0 deg, HPBW = 12.8 deg, FNBW = 28.9 deg, "
         "PSLL = -13.26 dB, Null count = 7 (N - 1), Grating lobes = 0.\n"
         "Verbal Highlight: 'Point to the -13.26 dB peak sidelobe level—the physical limit of uniform arrays.'"),

        ("DEMO 2: Element Count Scaling", "08:30 - 10:00 (1.5 min)",
         "Action: Drag the N slider smoothly from 4 -> 8 -> 16 -> 32.\n"
         "Parameters: Keep d = 0.5 lambda, beta = 0 deg constant.\n"
         "Expected Readout: Main lobe narrows drastically (HPBW drops from 26 deg at N=4 down to 3.2 deg at N=32). "
         "PSLL remains strictly constant at -13.26 dB while total nulls increase to N - 1.\n"
         "Verbal Highlight: 'Demonstrates that directivity scales with N while main beamwidth shrinks as 1/N.'"),

        ("DEMO 3: Phased Beam Steering", "10:00 - 12:00 (2.0 mins)",
         "Action: Set steering angle theta_0 = 45 deg or click 'Auto Steer'. Turn on 'Play Animation'.\n"
         "Parameters: N = 8, d = 0.5 lambda, auto-calculated beta = -127.28 deg.\n"
         "Expected Readout: Main beam shifts to 45.0 deg. HPBW widens from 12.8 deg to ~18.1 deg.\n"
         "Verbal Highlight: 'Explain beam broadening: effective array aperture contracts to L*sin(theta_0), "
         "causing HPBW to broaden by 1/sin(theta_0). Highlight continuous electronic scanning without gimbals.'"),

        ("DEMO 4: Spacing & Grating Lobes", "12:00 - 13:30 (1.5 mins)",
         "Action: Set broadside (theta_0 = 90 deg). Gradually increase d/lambda from 0.5 -> 0.8 -> 1.0 -> 1.5.\n"
         "Parameters: N = 8, beta = 0 deg.\n"
         "Expected Readout: At d=0.5 lambda, grating lobes = 0. At d=1.0 lambda, two 0 dB grating lobes emerge at "
         "0 deg and 180 deg. At d=1.5 lambda, multiple secondary beams appear in visible space.\n"
         "Verbal Highlight: 'Explain spatial aliasing analogous to Nyquist sampling theorem in DSP.'"),

        ("DEMO 5: Tapering & 3D Export", "13:30 - 15:00 (1.5 mins)",
         "Action: Change weighting from Uniform to 'Hann (Cosine)' and then 'Binomial'. Switch to 3D tab.\n"
         "Parameters: N = 8, d = 0.5 lambda, broadside.\n"
         "Expected Readout: Hann drops PSLL to -31.5 dB (HPBW widens to ~17.5 deg). Binomial eliminates sidelobes.\n"
         "Verbal Highlight: 'Demonstrates the resolution vs. sidelobe suppression engineering trade-off. "
         "Rotate 3D radiation torus and click Export CSV / Save Plot.'")
    ]

    card_y = 0.80
    for d_title, d_time, d_content in demos:
        draw_card(ax3, 0, card_y, 1.0, 0.18, bg="#ffffff", border="#cbd5e1",
                  title=f"{d_title}  |  {d_time}", title_color="#0284c7")
        ax3.text(0.02, card_y + 0.135, d_content, fontsize=7.6, color="#1e293b", wrap=True, va="top")
        card_y -= 0.195

    pdf.savefig(fig3)
    plt.close(fig3)

    # ==========================================
    # PAGE 4: SEGMENT 4 VIVA VOCE DEFENSE PART 1 (15:00 - 20:00)
    # ==========================================
    fig4 = plt.figure(figsize=(8.5, 11))
    setup_page(fig4, 4, total_pages,
               "Viva Voce Defense & Technical Q&A — Part 1",
               "Rigorous mathematical answers to core electromagnetics and array theory questions",
               "VIVA DEFENSE (15:00 - 20:00)")
    ax4 = fig4.add_axes([0.08, 0.06, 0.84, 0.80])
    ax4.axis("off")
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)

    qa_list_1 = [
        ("Q1: What is the physical distinction between excitation phase beta and total phase psi?",
         "Answer: beta is the electronic phase delay applied to adjacent feed lines. psi is the net spatial-electrical "
         "phase difference between waves arriving at observation angle theta: psi = k*d*cos(theta) + beta. It accounts "
         "for both spatial path delay (d*cos theta) and feed excitation phase beta."),

        ("Q2: Why is the observation angle theta measured from the array axis instead of broadside?",
         "Answer: In classical antenna array literature (Balanis, Stutzman), linear line arrays are oriented along "
         "the z-axis in spherical coordinates. Polar angle theta is measured from +z: theta=0 deg is positive end-fire, "
         "theta=90 deg is broadside, and theta=180 deg is negative end-fire. This simplifies path delay to d*cos(theta)."),

        ("Q3: What causes grating lobes and what is the exact mathematical onset condition?",
         "Answer: Grating lobes are equal-amplitude secondary maxima (|AF_norm|=1, 0 dB) caused by spatial aliasing "
         "when constructive interference occurs at psi = 2m*pi (m != 0) within visible space -1 <= cos(theta) <= 1. "
         "To completely avoid grating lobes over all steering angles theta_0, spacing must satisfy: d/lambda < 1 / (1 + |cos theta_0|). "
         "For broadside (theta_0 = 90 deg), grating lobes appear when d/lambda >= 1.0."),

        ("Q4: How does your code resolve 0/0 indeterminate singularities in the closed-form Array Factor?",
         "Answer: As psi -> 2m*pi, both numerator and denominator in |sin(N*psi/2)/sin(psi/2)| approach 0. Applying "
         "L'Hopital's rule: d/dpsi[sin(N*psi/2)] / d/dpsi[sin(psi/2)] = (N/2)*cos(N*psi/2) / (1/2)*cos(psi/2) -> N. "
         "Our physics engine detects |sin(psi/2)| < 1e-12 and substitutes the analytical limit N, preventing NaN or division-by-zero crashes."),

        ("Q5: Why is the Peak Sidelobe Level (PSLL) of a uniform array locked at -13.26 dB regardless of N?",
         "Answer: For large N, the array factor approaches the continuous sinc function sin(u)/u, where u = N*psi/2. "
         "The first sidelobe peak occurs near u = 1.4303*pi = 4.493 rad. The ratio |sin(4.493)/4.493| = 0.2172. "
         "In decibels: 20*log10(0.2172) = -13.26 dB. As N increases, the sidelobe gets closer to the main beam but its relative power remains -13.26 dB.")
    ]

    card_y = 0.80
    for q_title, q_ans in qa_list_1:
        draw_card(ax4, 0, card_y, 1.0, 0.18, bg="#ffffff", border="#cbd5e1",
                  title=q_title, title_color="#0f172a")
        ax4.text(0.02, card_y + 0.135, q_ans, fontsize=7.6, color="#334155", wrap=True, va="top")
        card_y -= 0.195

    pdf.savefig(fig4)
    plt.close(fig4)

    # ==========================================
    # PAGE 5: VIVA PART 2 & PRESENTER CUE CARD
    # ==========================================
    fig5 = plt.figure(figsize=(8.5, 11))
    setup_page(fig5, 5, total_pages,
               "Viva Defense Part 2 & Presenter Quick Cue Card",
               "Advanced questions on tapering, steering broadening, and presenter time-management checklist",
               "CUE CARD & ADVANCED Q&A")
    ax5 = fig5.add_axes([0.08, 0.06, 0.84, 0.80])
    ax5.axis("off")
    ax5.set_xlim(0, 1)
    ax5.set_ylim(0, 1)

    qa_list_2 = [
        ("Q6: Why does the main beam broaden when steered away from broadside?",
         "Answer: The physical aperture length projected onto the wavefront normal is L_eff = L*sin(theta_0). "
         "Because beamwidth is inversely proportional to effective aperture, HPBW(theta_0) approximately equals "
         "HPBW_broadside / sin(theta_0). As theta_0 approaches 0 deg (end-fire), sin(theta_0) -> 0, causing beam broadening."),

        ("Q7: What are the engineering trade-offs of Hann and Binomial amplitude tapering?",
         "Answer: Uniform has highest directivity and narrowest beam, but high sidelobes (-13.26 dB). "
         "Hann (Cosine) suppresses sidelobes to -31.5 dB with a modest ~35% beam broadening penalty. "
         "Binomial completely eliminates sidelobes (d <= lambda/2) but results in very low aperture efficiency and wide HPBW."),

        ("Q8: How did you verify the numerical correctness of your implementation?",
         "Answer: Automated cross-validation: 1) Complex summation matches closed-form evaluation within < 1e-10 relative error. "
         "2) Benchmark cases (N=8, d=0.5 lambda) verified against theoretical HPBW, FNBW, and -13.26 dB PSLL. "
         "3) Full pytest suite of 81 automated unit and integration tests passing in CI/CD.")
    ]

    card_y = 0.69
    for q_title, q_ans in qa_list_2:
        draw_card(ax5, 0, card_y, 1.0, 0.145, bg="#ffffff", border="#cbd5e1",
                  title=q_title, title_color="#0f172a")
        ax5.text(0.02, card_y + 0.105, q_ans, fontsize=7.6, color="#334155", wrap=True, va="top")
        card_y -= 0.16

    # Presenter Quick Timing Cue Card
    draw_card(ax5, 0, 0.02, 1.0, 0.18, bg="#0f172a", border="#38bdf8",
              title="PRESENTER EMERGENCY TIMING CUE CARD (KEEP ON PODIUM)", title_color="#38bdf8")

    cue_text = [
        "Minute 00-03: State ULA orientation (z-axis), state AF formula, state psi = kd cos theta + beta.",
        "Minute 03-07: Highlight MVC architecture, dynamic mm readout, zero-scroll interface, 81/81 tests.",
        "Minute 07-10: Demo Broadside (point out -13.26 dB PSLL, 7 nulls), then slide N (narrowing beam).",
        "Minute 10-13: Demo Auto-Steer to 45 deg (explain 1/sin theta_0 broadening), then slide d/lambda to 1.0 (grating lobes).",
        "Minute 13-15: Switch to Hann tapering (-31.5 dB sidelobes), rotate 3D radiation torus, click Export CSV.",
        "Minute 15-20: Answer questions confidently using exact formulas. Always reference physics first!"
    ]
    c_y = 0.14
    for ct in cue_text:
        ax5.text(0.02, c_y, ct, fontsize=7.5, family="monospace", color="#f8fafc")
        c_y -= 0.022

    pdf.savefig(fig5)
    plt.close(fig5)

    pdf.close()
    print(f"Guide PDF generated successfully: {OUTPUT_PDF}")

if __name__ == "__main__":
    generate_guide_pdf()
