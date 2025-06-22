# 🧑‍🎓 Face Recognition Attendance System

This is a Python-based face recognition attendance system that uses **AWS Rekognition** for facial matching and stores attendance logs in a **SQLite database**.

- 📸 Captures real-time webcam feed
- 🧠 Compares with stored student photos using AWS Rekognition
- 🟢 Marks students present if matched
- 📝 Logs attendance (Present/Absent) with timestamps
- 📂 Structured, modular, and ready for deployment

---

## 📁 Project Structure

```
attendance-system/
│
├── main.py                 # Main script to run the system
├── config.py               # Configuration (DB path, AWS region, etc.)
├── requirements.txt        # Dependencies
├── .gitignore              # Ignore rules
│
├── core/
│   ├── camera/
│   │   └── webcam.py
│   ├── db/
│   │   ├── connection.py
│   │   └── models.py
│   ├── recognition/
│   │   └── rekognition_handler.py
│   └── utils/
│       └── logger.py
│
├── data/                   # SQLite database (`attendance.db`)
├── logs/                   # Application log files
└── assets/ (optional)      # Student images (for insert script)
```

---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/attendance-system.git
cd attendance-system
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure AWS

- Set up AWS credentials (using `~/.aws/credentials` or environment variables)
- Ensure Rekognition is enabled in your AWS account

### 4. Add Students to Database

Use a helper script to add students:

```python
from core.db.connection import get_connection
from core.db.models import create_tables

def add_student(id, name, image_path):
    conn = get_connection()
    create_tables(conn)
    with open(image_path, 'rb') as f:
        photo = f.read()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO students (id, name, photo) VALUES (?, ?, ?)', (id, name, photo))
    conn.commit()
    conn.close()
```

Run this script for each student image.

---

## ▶️ Run the Application

```bash
python main.py
```

- Press `q` to stop the session
- Absent students will be automatically marked at the end

---

## 📦 Dependencies

- `opencv-python`
- `boto3`
- `pillow`
- `sqlite3` (built-in)

Install them with:

```bash
pip install -r requirements.txt
```

---

## 📌 Features

- ✅ AWS Rekognition for face comparison
- ✅ SQLite for offline, lightweight data storage
- ✅ Logs attendance and errors in `logs/attendance.log`
- ✅ Modular code with clean architecture

---

## 🚫 .gitignore Includes

```
__pycache__/
*.db
logs/
.env
```

---

## 📄 License

This project is licensed under the **MIT License**. Feel free to modify and use it for educational or production purposes.

---

## 🙋‍♂️ Author

**Aditya Gautam**  
Feel free to reach out for collaboration or questions!

