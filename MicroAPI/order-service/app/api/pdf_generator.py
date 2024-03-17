from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Product Quote', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, data):
        self.set_font('Arial', '', 12)
        self.set_fill_color(200, 220, 255)
        # Table header
        self.cell(40, 10, 'Product ID', 1, 0, 'C', 1)
        self.cell(40, 10, 'Quantity', 1, 0, 'C', 1)
        self.cell(40, 10, 'Unit Price', 1, 0, 'C', 1)
        self.cell(40, 10, 'Total Price', 1, 1, 'C', 1)
        self.set_fill_color(255, 255, 255)
        total_price = 0
        for product_id, details in data.items():
            quantity = details["quantity"]
            price = details["price"]
            total = quantity * price
            total_price += total
            self.cell(40, 10, str(product_id), 1, 0, 'C', 1)
            self.cell(40, 10, str(quantity), 1, 0, 'C', 1)
            self.cell(40, 10, f"{price} EUR", 1, 0, 'C', 1)
            self.cell(40, 10, f"{total} EUR", 1, 1, 'C', 1)
        self.cell(120, 10, 'Grand Total', 1, 0, 'C', 1)
        self.cell(40, 10, f"{total_price} EUR", 1, 1, 'C', 1)
