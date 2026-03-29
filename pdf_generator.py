from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO

def generate_transaction_pdf(transactions: list, buffer: BytesIO):
    """
    Generates a PDF document containing transaction history.

    Args:
        transactions (list): A list of transaction dictionaries.
        buffer (BytesIO): A BytesIO object to write the PDF content to.
    """
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("Transaction Statement", styles['h1']))
    story.append(Spacer(1, 0.2 * inch))

    if not transactions:
        story.append(Paragraph("No transactions found for the selected criteria.", styles['Normal']))
    else:
        # Table Header
        data = [['Date', 'Type', 'Description', 'Amount', 'Currency']]

        # Table Rows
        for tx in transactions:
            data.append([
                tx['transaction_date'].strftime('%Y-%m-%d'),
                tx['transaction_type'].capitalize(),
                tx['description'],
                f"{tx['amount']:.2f}",
                tx['currency']
            ])

        table = Table(data, colWidths=[1.2*inch, 0.8*inch, 3*inch, 1*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'), # Align amount to right
        ]))
        story.append(table)

    doc.build(story)
