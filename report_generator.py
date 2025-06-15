from fpdf import FPDF
from io import BytesIO
from PIL import Image
import base64

# ================================
# 🔁 Emoji Replacement Dictionary
# ================================
EMOJI_REPLACEMENTS = {
    "⚠️": "[WARNING]",
    "⚠": "[WARNING]",
    "🚨": "[ALERT]",
    "✅": "[OK]",
    "📄": "[PDF]",
    "📥": "[DOWNLOAD]",
    "⬇️": "[DOWNLOAD]",
    "📊": "[CHART]",
    "🔍": "[FILTER]",
    "🔎": "[SEARCH]",
    "🔥": "[HEATMAP]",
    "💡": "[TIPS]",
    "⏳": "[WAIT]",
}


# ===================================
# 🔁 Replace emojis with plain text
# ===================================
def replace_emojis(text: str) -> str:
    """
    Replace emojis in the input text with plain-text equivalents.

    Args:
        text (str): Input text possibly containing emojis.

    Returns:
        str: Text with emojis replaced.
    """
    for emoji, replacement in EMOJI_REPLACEMENTS.items():
        text = text.replace(emoji, replacement)
    return text


# =========================
# 📄 PDF Report Class
# =========================
class PDFReport(FPDF):
    """
    Custom FPDF class for generating structured reports.
    """

    def __init__(self, title: str):
        super().__init__()
        self.title = title
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, self.title, ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def add_section_title(self, title: str):
        self.set_font("Arial", "B", 12)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, replace_emojis(title), ln=True)
        self.ln(2)

    def add_paragraph(self, text: str):
        self.set_font("Arial", "", 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 8, replace_emojis(text))
        self.ln(3)

    def insert_base64_image(self, base64_str: str, w: int = 180):
        """
        Insert a base64-encoded image into the PDF.

        Args:
            base64_str (str): Base64-encoded PNG or JPEG.
            w (int): Width of the image in mm.
        """
        try:
            image_data = base64.b64decode(base64_str)
            buf = BytesIO(image_data)
            image = Image.open(buf).convert("RGB")
            temp_buf = BytesIO()
            image.save(temp_buf, format="JPEG")
            temp_buf.seek(0)
            self.image(temp_buf, w=w)
            self.ln(5)
        except Exception as e:
            self.add_paragraph(f"[ERROR LOADING IMAGE] {e}")


# ========================================
# 🧾 PDF Generation Function
# ========================================
def generate_pdf(summary_text: str, figs: dict, alerts: list) -> bytes | None:
    """
    Generate a full PDF report summarizing employee attrition survey data.

    Args:
        summary_text (str): Executive summary text.
        figs (dict): Dictionary of base64-encoded figures (Plotly or Matplotlib).
        alerts (list): List of alert strings to display.

    Returns:
        bytes | None: PDF content in bytes (for download or saving).
    """
    try:
        pdf = PDFReport("Employee Attrition Survey Report")
        pdf.add_page()

        # ➤ Section: Executive Summary
        pdf.add_section_title("Executive Summary")
        pdf.add_paragraph(summary_text)

        # ➤ Section: Verdict Pie Chart
        pdf.add_section_title("Attrition Verdict Breakdown")
        if "verdict_pie" in figs:
            pie_base64 = (
                figs["verdict_pie"]
                .to_image(format="png", width=800, height=500)
                .decode("latin1")
            )
            pdf.insert_base64_image(pie_base64)
        else:
            pdf.add_paragraph("No verdict pie chart available.")

        # ➤ Section: Correlation Heatmap
        pdf.add_section_title("Survey Metric Correlations")
        if "heatmap" in figs:
            pdf.insert_base64_image(figs["heatmap"])
        else:
            pdf.add_paragraph("No correlation heatmap available.")

        # ➤ Section: Grouped Bar Charts (by Location, Position, Dept)
        for key in ["bar_location", "bar_position", "bar_dept"]:
            label = key.replace("bar_", "").title()
            pdf.add_section_title(f"Survey Question Scores by {label}")
            if key in figs:
                pdf.insert_base64_image(figs[key])
            else:
                pdf.add_paragraph(f"No bar chart found for {label}.")

        # ➤ Section: Alerts Summary
        pdf.add_section_title("Alerts Summary")
        if alerts:
            for alert in alerts:
                pdf.add_paragraph(alert)
        else:
            pdf.add_paragraph("✅ No alerts triggered based on thresholds.")

        # ✅ Return PDF as bytes
        return bytes(pdf.output(dest="S"))

    except Exception as e:
        print(f"[PDF Generation Error] {e}")
        return None
