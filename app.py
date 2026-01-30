from flask import Flask, render_template, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import psutil
import io
from datetime import datetime

# 1. Sarvath aadhi 'app' define kara
app = Flask(__name__)

# 2. Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 3. Model define kara (Import karnyachi garaj nahi, ithech lihava)
class SystemStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpu = db.Column(db.Float)
    ram = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# 4. Tables create kara
with app.app_context():
    db.create_all()

# 5. Routes (Ata 'app' defined aahe, mhanun error yenar nahi)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/live-data')
def live_data():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    current_time = datetime.now().strftime("%H:%M:%S")

    # DB madhe save kara
    new_stat = SystemStats(cpu=cpu, ram=ram)
    db.session.add(new_stat)
    db.session.commit()

    return jsonify({"cpu": cpu, "ram": ram, "time": current_time})

@app.route('/download-report')
def download_report():
    all_stats = SystemStats.query.all()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.drawString(100, 750, "System Performance Report")
    y = 700
    for stat in all_stats[-10:]: # Last 10 records
        c.drawString(100, y, f"CPU: {stat.cpu}% | RAM: {stat.ram}% | Time: {stat.timestamp}")
        y -= 20
    c.save()
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name="Report.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)