from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from fpdf import FPDF
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'invoices'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Data item (Anda dapat mengganti ini dengan data dari database)
ITEMS = {
    "Premium Peach Stripes": 250000,
    "Premium White": 250000,
    "Premium Pink Bubblegum": 250000,
    "Premium Orange Stripes": 250000,
    "Premium Sweetpea Pink": 250000,
    "Premium White Pattern": 250000,
    "Premium Mullberry Pink": 250000,
}

# Halaman utama untuk mengisi form
@app.route('/')
def home():
    return render_template('index.html', items=ITEMS)

# Endpoint untuk menghitung total harga secara dinamis (AJAX)
@app.route('/get_price', methods=['POST'])
def get_price():
    item_name = request.json.get('item_name')
    if item_name in ITEMS:
        return jsonify({"price": ITEMS[item_name]})
    return jsonify({"error": "Item not found"}), 404

# Endpoint untuk menangani form dan membuat invoice
@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    try:
        # Ambil data dari form
        customer_name = request.form['customer_name']
        customer_address = request.form['customer_address']
        customer_phone = request.form['customer_phone']
        invoice_number = request.form['invoice_number']
        due_date = request.form['due_date']
        
        # Ambil item dari form
        items = []
        item_names = request.form.getlist('item_name')
        quantities = request.form.getlist('quantity')
        
        for name, qty in zip(item_names, quantities):
            price = ITEMS.get(name, 0)
            items.append((name, int(qty), price))
        
        # Buat invoice PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Header Invoice
        pdf.set_font("Arial", size=12, style="B")
        pdf.cell(0, 10, "TOKO BUNGA FLORIST", ln=True, align="C")
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, "Jl. [Alamat Toko], [Kota] - Telp: [Nomor Telepon]", ln=True, align="C")
        pdf.cell(0, 10, "", ln=True)  # Empty line
        
        # Informasi pelanggan
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, f"Invoice No: {invoice_number}", ln=True)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%d-%m-%Y')}", ln=True)
        pdf.cell(0, 10, f"Due Date: {due_date}", ln=True)
        pdf.cell(0, 10, f"Customer Name: {customer_name}", ln=True)
        pdf.cell(0, 10, f"Address: {customer_address}", ln=True)
        pdf.cell(0, 10, f"Phone: {customer_phone}", ln=True)
        pdf.cell(0, 10, "", ln=True)  # Empty line
        
        # Header tabel
        pdf.cell(10, 10, "No", border=1, align="C")
        pdf.cell(80, 10, "Description", border=1, align="C")
        pdf.cell(30, 10, "Qty", border=1, align="C")
        pdf.cell(30, 10, "Unit Price", border=1, align="C")
        pdf.cell(30, 10, "Total", border=1, ln=True, align="C")
        
        # Isi tabel
        total_payment = 0
        for i, item in enumerate(items, 1):
            description, quantity, unit_price = item
            total = quantity * unit_price
            total_payment += total
            pdf.cell(10, 10, str(i), border=1, align="C")
            pdf.cell(80, 10, description, border=1, align="L")
            pdf.cell(30, 10, str(quantity), border=1, align="C")
            pdf.cell(30, 10, f"Rp {unit_price:,.2f}", border=1, align="R")
            pdf.cell(30, 10, f"Rp {total:,.2f}", border=1, ln=True, align="R")
        
        # Total
        pdf.cell(150, 10, "Total Payment:", border=1, align="R")
        pdf.cell(30, 10, f"Rp {total_payment:,.2f}", border=1, ln=True, align="R")
        
        # Simpan file PDF
        file_name = f"{UPLOAD_FOLDER}/invoice_{invoice_number}.pdf"
        pdf.output(file_name)
        
        flash(f"Invoice berhasil dibuat: {file_name}", "success")
        return redirect(url_for('home'))
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", "danger")
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
