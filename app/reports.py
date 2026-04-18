import os
from fpdf import FPDF
from datetime import datetime

class ExecutiveReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.set_text_color(33, 37, 41)
        self.cell(0, 10, 'STRATEGIC DATA INTELLIGENCE REPORT', 0, 1, 'C')
        self.set_draw_color(0, 102, 204)
        self.line(10, 22, 200, 22)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.now().strftime("%Y-%m-%d")}', 0, 0, 'C')

    def generate(self, data_summary, chart_path=None):
        self.add_page()
        
        # Resumen
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, f"Executive Summary: {data_summary['country']}", 0, 1, 'L')
        self.ln(2)
        
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 7, (
            f"This report presents a multidimensional analysis of '{data_summary['indicator']}'. "
            f"The data was processed through the Strategic Quality Firewall, ensuring integrity before analysis."
        ))
        self.ln(5)

        # INSERTAR GRÁFICA
        if chart_path and os.path.exists(chart_path):
            self.set_font('Arial', 'B', 11)
            self.cell(0, 10, " 1. Visual Trend Analysis", 0, 1, 'L')
            # Intentamos insertar la imagen. Si kaleido funcionó, aquí aparecerá.
            self.image(chart_path, x=10, y=None, w=190)
            self.ln(5)

        # Auditoría y ML
        self.set_fill_color(240, 240, 240)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 10, " 2. Technical Audit & Insights", 1, 1, 'L', True)
        self.set_font('Arial', '', 10)
        self.ln(2)
        self.cell(0, 7, f"- Health Score: {data_summary['health_score']:.1f}%", 0, 1)
        self.cell(0, 7, f"- Status: {'PASSED' if data_summary['health_score'] >= 80 else 'REJECTED'}", 0, 1)
        self.cell(0, 7, f"- Model: Polynomial (Degree {data_summary['degree']})", 0, 1)
        self.cell(0, 7, f"- Insight: {data_summary['forecast_insight']}", 0, 1)
        
        return self.output(dest='S')