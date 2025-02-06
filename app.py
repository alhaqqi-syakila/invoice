from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from fpdf import FPDF
import os
from datetime import datetime

# Inisialisasi Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ganti dengan kunci yang lebih aman
UPLOAD_FOLDER = 'invoices'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Daftar harga untuk jumlah tangkai (untuk 3 hingga 20 tangkai)
PRICE_LIST = [
    750000, 975000, 1250000, 1480000, 1720000, 1950000, 2250000, 2400000, 
    2600000, 2850000, 3200000, 3550000, 3750000, 3900000, 4150000, 4400000, 
    4750000, 5000000
]

ITEMS = {
    "Rangkaian Bunga Anggrek": 0,  # Harga dihitung berdasarkan jumlah tangkai
    "Papan Bunga Anggrek": 0,      # Harga dihitung berdasarkan jumlah tangkai
}

# Halaman utama untuk mengisi form
@app.route('/')
def home():
    return render_template('index.html', items=ITEMS)

# Endpoint untuk menghitung total harga secara dinamis (AJAX)
@app.route('/get_price', methods=['POST'])
def get_price():
    item_name = request.json.get('item_name')
    quantity = int(request.json.get('quantity'))
    
    if item_name in ITEMS:
        # Pastikan kuantitas tidak melebihi 20 dan minimal 3 tangkai
        if 3 <= quantity <= 20:
            price = PRICE_LIST[quantity - 3]  # Sesuaikan harga berdasarkan kuantitas
            return jsonify({"price": price})
        return jsonify({"error": "Jumlah tangkai tidak valid (3 hingga 20)"}, 400)
    return jsonify({"error": "Item tidak ditemukan"}), 404

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
            qty = int(qty)
            # Tentukan harga berdasarkan jumlah tangkai
            if 3 <= qty <= 20:
                price = PRICE_LIST[qty - 3]
            else:
                price = 0
            total_price = price * qty  # Total harga = harga unit * kuantitas
            items.append((name, qty, total_price))

        # Nomor rekening toko
        rekening_toko = "BCA: 2870346690"  # Nomor rekening toko yang tetap
        
        # Buat invoice PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Header Invoice
        pdf.set_font("Arial", size=12, style="B")
        pdf.cell(0, 10, "FLOTIST ORCHID COLLECTION", ln=True, align="C")
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, "Jakarta - Telp: +6282324663758", ln=True, align="C")
        pdf.cell(0, 10, "", ln=True)  # Empty line
        
        # Informasi pelanggan
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, f"No Invoice: {invoice_number}", ln=True)
        pdf.cell(0, 10, f"Tanggal: {datetime.now().strftime('%d-%m-%Y')}", ln=True)
        pdf.cell(0, 10, f"Tenggat Waktu: {due_date}", ln=True)
        pdf.cell(0, 10, f"Nama kostumer: {customer_name}", ln=True)
        pdf.cell(0, 10, f"Alamat: {customer_address}", ln=True)
        pdf.cell(0, 10, f"No.Telp: {customer_phone}", ln=True)
        pdf.cell(0, 10, "", ln=True)  # Empty line
        
        # Header tabel
        pdf.cell(10, 10, "No", border=1, align="C")
        pdf.cell(90, 10, "Deskripsi", border=1, align="C")
        pdf.cell(30, 10, "Kuantitas", border=1, align="C")
        pdf.cell(60, 10, "Jumlah Harga", border=1, ln=True, align="C")
        
        # Isi tabel
        total_payment = 0
        for i, item in enumerate(items, 1):
            description, quantity, total_price = item
            total_payment += total_price
            pdf.cell(10, 10, str(i), border=1, align="C")
            pdf.cell(90, 10, description, border=1, align="L")
            pdf.cell(30, 10, str(quantity), border=1, align="C")
            pdf.cell(60, 10, f"Rp {total_price:,.2f}", border=1, ln=True, align="R")
        
        # Total
        pdf.cell(150, 10, "Total Bayar:", border=1, align="R")
        pdf.cell(40, 10, f"Rp {total_payment:,.2f}", border=1, ln=True, align="R")

        # Nomor Rekening Toko
        pdf.cell(150, 10, "No Rek:", border=1, align="R")
        pdf.cell(40, 10, rekening_toko, border=1, ln=True, align="C")
        
        # Simpan file PDF
        file_name = f"{UPLOAD_FOLDER}/invoice_{invoice_number}.pdf"
        pdf.output(file_name)
        
        flash(f"Invoice berhasil dibuat: {file_name}", "success")
        return redirect(url_for('home'))
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", "danger")
        return redirect(url_for('home'))

# Pastikan server dijalankan dengan benar
if __name__ == '__main__':
    app.run(debug=True)
