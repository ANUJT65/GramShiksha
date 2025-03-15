import json
import os
from aixplain.factories import ModelFactory
from fpdf import FPDF

def generate_notes_pdf(text: str, output_path: str = "Generated_Notes.pdf") -> str:
    """
    Generates detailed, well-structured notes from input text using the Gemini 1.5 Flash model
    and saves them as a PDF file.
    """
    model = ModelFactory.get("674b73f06eb563a748561d41")
    
    prompt = (
        "Generate detailed, well-structured notes. "
        "Ensure the content is divided into multiple sections with headings, "
        "bullet points, and proper formatting for readability."
    )
    
    result = model.run({
        "text": text,
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": 1000
    })
    
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'Generated Notes', ln=True, align='C')
            self.ln(10)

        def chapter_content(self, content):
            self.set_font('Arial', '', 12)
            self.multi_cell(0, 10, content)
            self.ln()
    
    pdf = PDF()
    pdf.add_page()
    pdf.chapter_content(str(result.get("output", "No content generated.")))
    
    pdf.output(output_path)
    return output_path

# Example Usage
if __name__ == "__main__":
    input_text = (
        "The mitochondrion is often referred to as the powerhouse of the cell. "
        "It is responsible for generating ATP, the energy currency of the cell, "
        "through a process called cellular respiration. This organelle is found "
        "in most eukaryotic cells and plays a crucial role in energy production and metabolism."
    )
    pdf_path = generate_notes_pdf(input_text)
    print(f"PDF generated successfully: {pdf_path}")
