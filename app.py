from flask import Flask, request, jsonify, render_template_string, send_file, render_template, session, redirect, url_for
from flask_babel import Babel, _
import whisper
import os
import tempfile
from video_editor import VideoAIEditor
import json
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tera-secret-key-123'
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = './translations'

# Create necessary directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('output', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Languages dictionary empty - no language selector
LANGUAGES = {}

# Load model
try:
    model = whisper.load_model("base")
    print("✅ Whisper model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

editor = VideoAIEditor()

# Initialize Babel
babel = Babel(app)

def get_locale():
    return 'en'  # Always English

babel.locale_selector_func = get_locale

# Professional Design HTML Template
ANIME_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>✨ TERA AI Editor - Professional Video Editing</title>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <!-- Font Awesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            transition: background-color 0.3s ease,
                        color 0.3s ease,
                        border-color 0.3s ease,
                        transform 0.3s ease,
                        box-shadow 0.3s ease;
        }

        /* Typography */
        body {
            font-family: 'Inter', sans-serif;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Space Grotesk', sans-serif;
        }

        code, pre {
            font-family: 'Fira Code', monospace;
        }

        /* Animated Background */
        .animated-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -2;
            background: linear-gradient(-45deg, #6366f1, #8b5cf6, #ec4899, #10b981);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            opacity: 0.8;
        }

        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Dark Mode Overlay */
        body.dark-mode .animated-bg {
            opacity: 0.3;
            filter: brightness(0.5);
        }

        body.light-mode {
            color: #1e293b;
        }

        body.dark-mode {
            color: #f1f5f9;
        }

        /* Glass Card Effect */
        .glass-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        body.dark-mode .glass-card {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        /* Theme Toggle Button */
        .theme-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
        }

        .theme-btn {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.3);
            font-size: 1.8em;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .theme-btn:hover {
            transform: scale(1.1) rotate(15deg);
            border-color: white;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        }

        body.dark-mode .theme-btn {
            background: rgba(30, 41, 59, 0.6);
            border-color: rgba(255, 255, 255, 0.2);
        }

        /* Dashboard Layout */
        .dashboard {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            position: relative;
            z-index: 1;
        }

        /* Header */
        .main-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 30px;
            margin-bottom: 30px;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .logo i {
            font-size: 2.5em;
            color: #6366f1;
            filter: drop-shadow(0 4px 10px rgba(99, 102, 241, 0.3));
        }

        .logo h1 {
            font-size: 2em;
            background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }

        .header-actions {
            display: flex;
            gap: 15px;
        }

        .btn-icon {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 1.2em;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-icon:hover {
            transform: translateY(-3px);
            background: rgba(255, 255, 255, 0.25);
            border-color: white;
        }

        body.dark-mode .btn-icon {
            background: rgba(30, 41, 59, 0.6);
            color: #f1f5f9;
        }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            display: flex;
            align-items: center;
            gap: 20px;
            padding: 25px;
        }

        .stat-icon {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8em;
            color: white;
        }

        .stat-info h3 {
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 5px;
        }

        .stat-info p {
            font-size: 1.8em;
            font-weight: 700;
        }

        /* Mode Selector */
        .mode-selector {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 30px;
        }

        .mode-btn {
            padding: 15px 30px;
            border-radius: 50px;
            font-weight: 600;
            text-decoration: none;
            text-align: center;
            position: relative;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            transition: all 0.3s ease;
        }

        .mode-btn::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }

        .mode-btn:hover::before {
            width: 300px;
            height: 300px;
        }

        .mode-btn.active {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            border-color: transparent;
        }

        body.dark-mode .mode-btn {
            background: rgba(30, 41, 59, 0.6);
            color: #f1f5f9;
        }

        body.dark-mode .mode-btn.active {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
        }

        /* Upload Area */
        .upload-area {
            border: 3px dashed rgba(255, 255, 255, 0.3);
            border-radius: 30px;
            padding: 60px;
            text-align: center;
            cursor: pointer;
            margin-bottom: 30px;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(5px);
        }

        .upload-area:hover {
            border-color: #6366f1;
            background: rgba(99, 102, 241, 0.1);
            transform: scale(1.02);
        }

        .upload-icon {
            font-size: 4em;
            margin-bottom: 20px;
            color: #6366f1;
            animation: bounce 2s infinite;
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        .upload-area h3 {
            font-size: 1.5em;
            margin-bottom: 10px;
        }

        .file-info {
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            display: none;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
            animation: slideIn 0.5s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Progress Bar */
        .progress-bar {
            height: 10px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 5px;
            margin: 30px 0;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
            width: 0%;
            transition: width 0.5s ease;
            border-radius: 5px;
            animation: shimmer 2s infinite;
        }

        @keyframes shimmer {
            0% { opacity: 1; }
            50% { opacity: 0.8; }
            100% { opacity: 1; }
        }

        /* Step Indicator */
        .step-indicator {
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
            position: relative;
        }

        .step-indicator::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            width: 100%;
            height: 2px;
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-50%);
            z-index: 1;
        }

        .step-dot {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(5px);
            border: 2px solid rgba(255, 255, 255, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            position: relative;
            z-index: 2;
            transition: all 0.3s ease;
        }

        .step-dot.active {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            border-color: transparent;
            transform: scale(1.1);
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
        }

        .step-dot.completed {
            background: #10b981;
            border-color: transparent;
        }

        /* Quote Box */
        .quote-box {
            padding: 20px;
            border-radius: 15px;
            margin-top: 20px;
            font-style: italic;
            border-left: 4px solid #6366f1;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
        }

        /* Transcription Box */
        .transcription-box {
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            max-height: 200px;
            overflow-y: auto;
            display: none;
            border: 2px solid #6366f1;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
        }

        /* Action Buttons */
        .action-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 30px;
        }

        .btn-primary {
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
            border: none;
            position: relative;
            overflow: hidden;
        }

        .btn-primary::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }

        .btn-primary:hover::before {
            width: 300px;
            height: 300px;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.4);
        }

        .btn-secondary {
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: translateY(-2px);
        }

        body.dark-mode .btn-secondary {
            background: rgba(30, 41, 59, 0.6);
            color: #f1f5f9;
        }

        /* Social Share */
        .social-share {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }

        .social-btn {
            flex: 1;
            padding: 12px;
            border-radius: 10px;
            color: white;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            font-weight: 600;
        }

        .social-btn:hover {
            transform: translateY(-3px);
            filter: brightness(1.1);
        }

        .twitter { background: #1DA1F2; }
        .facebook { background: #4267B2; }
        .whatsapp { background: #25D366; }

        /* Loading Spinner */
        .loading {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(5px);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .loading.active {
            display: flex;
        }

        .pulse-loader {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899);
            animation: pulse 1.5s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.7; }
        }

        /* Recent Projects */
        .recent-projects {
            padding: 25px;
            margin-top: 30px;
        }

        .recent-projects h2 {
            margin-bottom: 20px;
            font-size: 1.5em;
        }

        .projects-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .project-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.05);
            transition: all 0.3s ease;
        }

        .project-item:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateX(5px);
        }

        .project-name {
            font-weight: 600;
        }

        .project-date {
            font-size: 0.9em;
            opacity: 0.7;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .dashboard {
                padding: 10px;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }

            .mode-selector {
                grid-template-columns: 1fr;
            }

            .upload-area {
                padding: 30px;
            }

            .action-buttons {
                flex-direction: column;
            }

            .step-indicator::before {
                width: 90%;
                left: 5%;
            }
        }

        @media (min-width: 769px) and (max-width: 1024px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body class="light-mode">
    <!-- Animated Background -->
    <div class="animated-bg"></div>

    <!-- Theme Toggle Button -->
    <div class="theme-toggle">
        <button class="theme-btn" onclick="toggleTheme()" id="themeToggle">🌙</button>
    </div>

    <!-- Loading Spinner -->
    <div class="loading" id="loading">
        <div class="pulse-loader"></div>
    </div>

    <!-- Main Dashboard -->
    <div class="dashboard">
        <!-- Header -->
        <header class="main-header glass-card">
            <div class="logo">
                <i class="fas fa-film"></i>
                <h1>TERA AI Editor</h1>
            </div>
            <div class="header-actions">
                <button class="btn-icon"><i class="fas fa-bell"></i></button>
                <button class="btn-icon"><i class="fas fa-user"></i></button>
            </div>
        </header>

        <!-- Stats Cards -->
        <div class="stats-grid">
            <div class="stat-card glass-card">
                <div class="stat-icon"><i class="fas fa-video"></i></div>
                <div class="stat-info">
                    <h3>Total Videos</h3>
                    <p>0</p>
                </div>
            </div>
            <div class="stat-card glass-card">
                <div class="stat-icon"><i class="fas fa-clock"></i></div>
                <div class="stat-info">
                    <h3>Processing Time</h3>
                    <p>0 min</p>
                </div>
            </div>
            <div class="stat-card glass-card">
                <div class="stat-icon"><i class="fas fa-database"></i></div>
                <div class="stat-info">
                    <h3>Storage Used</h3>
                    <p>0 MB</p>
                </div>
            </div>
        </div>

        <!-- Mode Selector -->
        <div class="mode-selector">
            <a href="/" class="mode-btn active">🏠 Home</a>
            <a href="/normal-edit" class="mode-btn">🎬 Normal Edit</a>
        </div>

        <!-- Progress Bar -->
        <div class="progress-bar">
            <div class="progress-fill" id="progressFill"></div>
        </div>

        <!-- Step Indicator -->
        <div class="step-indicator">
            <div class="step-dot" id="step1Dot">1</div>
            <div class="step-dot" id="step2Dot">2</div>
            <div class="step-dot" id="step3Dot">3</div>
        </div>

        <!-- Step 1: Upload -->
        <div id="step1" class="step active">
            <div class="upload-area" id="uploadArea">
                <div class="upload-icon"><i class="fas fa-cloud-upload-alt"></i></div>
                <h3>Drop your video here!</h3>
                <p style="margin: 10px 0;">or click to upload</p>
                <p style="font-size: 0.9em; opacity: 0.8;">MP4, MOV, AVI (Max 100MB)</p>
                <input type="file" id="fileInput" accept="video/*" style="display: none;">
            </div>
            <div class="file-info" id="fileInfo"></div>
            <div style="text-align: center; opacity: 0.8;">
                <span>🌟 No signup required</span> • 
                <span>⚡ Fast processing</span> • 
                <span>✨ AI Powered</span>
            </div>
        </div>

        <!-- Step 2: Processing -->
        <div id="step2" class="step">
            <div class="loading" style="display: block; position: relative; background: none; backdrop-filter: none;">
                <div class="pulse-loader"></div>
                <p id="loadingText" style="font-size: 1.2em; margin: 20px 0; text-align: center;">Processing your video...</p>
            </div>
            <div class="quote-box" id="quoteBox">
                <i class="fas fa-quote-left" style="color: #6366f1; margin-right: 10px;"></i>
                <span id="animeQuote">🌸 Even a fool has his moment of glory...</span>
            </div>
            <div class="transcription-box" id="transcriptionBox">
                <strong><i class="fas fa-scroll" style="margin-right: 10px;"></i>Script:</strong>
                <p id="transcriptionText" style="margin-top: 10px;"></p>
            </div>
        </div>

        <!-- Step 3: Download -->
        <div id="step3" class="step">
            <div style="text-align: center;">
                <span class="step-dot completed" style="margin: 0 auto 20px;">✓</span>
                <h2 style="margin: 20px 0;">🎉 Your video is ready!</h2>
                <p style="margin-bottom: 30px; opacity: 0.8;">Your video has been transformed with AI magic!</p>
                
                <button onclick="downloadVideo()" id="downloadBtn" class="btn-primary">
                    <i class="fas fa-download" style="margin-right: 10px;"></i>Download Video
                </button>
                
                <button onclick="startOver()" class="btn-secondary" style="margin-top: 10px;">
                    <i class="fas fa-redo" style="margin-right: 10px;"></i>Create New
                </button>

                <div class="social-share">
                    <button class="social-btn twitter" onclick="shareOnTwitter()"><i class="fab fa-twitter"></i> Twitter</button>
                    <button class="social-btn facebook" onclick="shareOnFacebook()"><i class="fab fa-facebook"></i> Facebook</button>
                    <button class="social-btn whatsapp" onclick="shareOnWhatsApp()"><i class="fab fa-whatsapp"></i> WhatsApp</button>
                </div>
            </div>
        </div>

        <!-- Recent Projects -->
        <div class="recent-projects glass-card">
            <h2><i class="fas fa-history" style="margin-right: 10px;"></i>Recent Projects</h2>
            <div class="projects-list" id="recentProjects">
                <div class="project-item">
                    <span class="project-name"><i class="fas fa-video" style="margin-right: 10px;"></i>No projects yet</span>
                    <span class="project-date">-</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Theme Toggle Function
        function toggleTheme() {
            const body = document.body;
            const themeBtn = document.getElementById('themeToggle');
            
            if (body.classList.contains('light-mode')) {
                body.classList.remove('light-mode');
                body.classList.add('dark-mode');
                themeBtn.innerHTML = '☀️';
                localStorage.setItem('theme', 'dark');
            } else {
                body.classList.remove('dark-mode');
                body.classList.add('light-mode');
                themeBtn.innerHTML = '🌙';
                localStorage.setItem('theme', 'light');
            }
        }

        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.remove('light-mode');
            document.body.classList.add('dark-mode');
            document.getElementById('themeToggle').innerHTML = '☀️';
        }

        let currentVideo = null;
        let transcription = null;
        
        const animeQuotes = [
            "🌸 Even a fool has his moment of glory...",
            "⚡ Believe it!",
            "🔥 I'm not giving up, I'm just getting started!",
            "💫 The moment you give up is the moment you let someone else win.",
            "🍜 Hard work is worthless for those that don't believe in themselves.",
            "⚔️ A lesson without pain is meaningless.",
            "🦊 The difference between the novice and the master is that the master has failed more times.",
            "🌙 I never go back on my word!",
            "🎯 Even if we forget the faces of our friends, we will never forget the bonds that were carved into our souls.",
            "💢 If you don't like your destiny, don't accept it."
        ];

        function rotateQuote() {
            const quoteElement = document.getElementById('animeQuote');
            let index = 0;
            setInterval(() => {
                index = (index + 1) % animeQuotes.length;
                quoteElement.style.opacity = '0';
                setTimeout(() => {
                    quoteElement.textContent = animeQuotes[index];
                    quoteElement.style.opacity = '1';
                }, 500);
            }, 3000);
        }

        document.getElementById('uploadArea').onclick = () => {
            document.getElementById('fileInput').click();
        };

        document.getElementById('uploadArea').ondragover = (e) => {
            e.preventDefault();
            document.getElementById('uploadArea').style.borderColor = '#6366f1';
            document.getElementById('uploadArea').style.transform = 'scale(1.02)';
        };

        document.getElementById('uploadArea').ondragleave = (e) => {
            e.preventDefault();
            document.getElementById('uploadArea').style.borderColor = 'rgba(255, 255, 255, 0.3)';
            document.getElementById('uploadArea').style.transform = 'scale(1)';
        };

        document.getElementById('uploadArea').ondrop = (e) => {
            e.preventDefault();
            document.getElementById('uploadArea').style.borderColor = 'rgba(255, 255, 255, 0.3)';
            document.getElementById('uploadArea').style.transform = 'scale(1)';
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('video/')) {
                handleFile(file);
            } else {
                alert('🌟 Please upload a video file!');
            }
        };

        document.getElementById('fileInput').onchange = async (e) => {
            const file = e.target.files[0];
            if (file) {
                handleFile(file);
            }
        };

        async function handleFile(file) {
            const fileInfo = document.getElementById('fileInfo');
            fileInfo.style.display = 'block';
            fileInfo.innerHTML = `
                <div style="display: flex; align-items: center; gap: 15px;">
                    <i class="fas fa-check-circle" style="font-size: 2em;"></i>
                    <div>
                        <strong>${file.name}</strong><br>
                        Size: ${(file.size / (1024*1024)).toFixed(2)} MB
                    </div>
                </div>
            `;

            document.getElementById('progressFill').style.width = '33%';
            document.getElementById('step1Dot').className = 'step-dot completed';

            const formData = new FormData();
            formData.append('video', file);

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();

                if (result.success) {
                    currentVideo = result.filename;
                    
                    // Update recent projects
                    const projectsList = document.getElementById('recentProjects');
                    projectsList.innerHTML = `
                        <div class="project-item">
                            <span class="project-name"><i class="fas fa-video" style="margin-right: 10px;"></i>${file.name.substring(0, 20)}...</span>
                            <span class="project-date">Just now</span>
                        </div>
                    `;

                    document.getElementById('step1').classList.remove('active');
                    document.getElementById('step2').classList.add('active');
                    document.getElementById('step2Dot').className = 'step-dot active';
                    document.getElementById('progressFill').style.width = '66%';
                    
                    document.getElementById('loading').style.display = 'flex';
                    document.getElementById('loadingText').innerText = '🎤 Transcribing with AI...';
                    
                    rotateQuote();
                    await transcribeVideo();
                } else {
                    alert('Upload failed: ' + result.error);
                }
            } catch (error) {
                alert('Upload failed: ' + error);
            }
        }

        async function transcribeVideo() {
            try {
                const response = await fetch('/transcribe_video', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({filename: currentVideo})
                });
                const result = await response.json();

                if (result.success) {
                    transcription = result.transcription;
                    
                    document.getElementById('loadingText').innerText = '🎬 Adding AI captions...';
                    document.getElementById('transcriptionText').innerText = result.transcription;
                    document.getElementById('transcriptionBox').style.display = 'block';
                    
                    await addCaptions();
                } else {
                    alert('Transcription failed: ' + result.error);
                }
            } catch (error) {
                alert('Transcription failed: ' + error);
            }
        }

        async function addCaptions() {
            try {
                const response = await fetch('/add_captions', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        filename: currentVideo,
                        transcription: transcription
                    })
                });
                const result = await response.json();

                if (result.success) {
                    currentVideo = result.output;
                    
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('step2').classList.remove('active');
                    document.getElementById('step3').classList.add('active');
                    document.getElementById('step2Dot').className = 'step-dot completed';
                    document.getElementById('step3Dot').className = 'step-dot active';
                    document.getElementById('progressFill').style.width = '100%';
                } else {
                    alert('Failed to add captions: ' + result.error);
                }
            } catch (error) {
                alert('Failed to add captions: ' + error);
            }
        }

        async function downloadVideo() {
            try {
                const response = await fetch('/export/' + encodeURIComponent(currentVideo));
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'ai_video_' + new Date().getTime() + '.mp4';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    
                    alert('✨ Download started! Share your creation!');
                } else {
                    const error = await response.json();
                    alert('Download failed: ' + (error.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Download failed: ' + error);
            }
        }

        function startOver() {
            currentVideo = null;
            transcription = null;
            
            document.getElementById('step3').classList.remove('active');
            document.getElementById('step1').classList.add('active');
            document.getElementById('progressFill').style.width = '0%';
            document.getElementById('step1Dot').className = 'step-dot';
            document.getElementById('step2Dot').className = 'step-dot';
            document.getElementById('step3Dot').className = 'step-dot';
            document.getElementById('fileInfo').style.display = 'none';
            document.getElementById('transcriptionBox').style.display = 'none';
            document.getElementById('fileInput').value = '';
        }

        function shareOnTwitter() {
            window.open('https://twitter.com/intent/tweet?text=' + encodeURIComponent('Check out my AI video created with TERA AI Editor! 🎬✨ ₹9 mein 2 mahine!'), '_blank');
        }

        function shareOnFacebook() {
            window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(window.location.href), '_blank');
        }

        function shareOnWhatsApp() {
            window.open('https://wa.me/?text=' + encodeURIComponent('Check out my AI video created with TERA AI Editor! 🎬✨ ₹9 mein 2 mahine!'), '_blank');
        }
    </script>
</body>
</html>
"""

# Normal Edit Page Route
@app.route('/normal-edit')
def normal_edit():
    return render_template('normal_edit.html', session=session)

@app.route('/')
def home():
    return render_template_string(ANIME_HTML_TEMPLATE, session=session)

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    ext = file.filename.split('.')[-1]
    unique_filename = f"uploads/{uuid.uuid4().hex}.{ext}"
    file.save(unique_filename)
    
    file_size = os.path.getsize(unique_filename) / (1024 * 1024)
    
    return jsonify({
        'success': True, 
        'filename': unique_filename,
        'size': round(file_size, 2)
    })

@app.route('/transcribe_video', methods=['POST'])
def transcribe_video():
    if not model:
        return jsonify({'success': False, 'error': 'Model not loaded'}), 500
    
    data = request.json
    video_path = data.get('filename')
    
    if not video_path or not os.path.exists(video_path):
        return jsonify({'success': False, 'error': 'Video file not found'}), 404
    
    audio_path = video_path + '_audio.mp3'
    
    try:
        if not editor.extract_audio(video_path, audio_path):
            return jsonify({'success': False, 'error': 'Could not extract audio'}), 500
        
        result = model.transcribe(audio_path)
        
        if os.path.exists(audio_path):
            os.unlink(audio_path)
        
        return jsonify({
            'success': True,
            'transcription': result['text'],
            'language': result.get('language', 'unknown')
        })
    
    except Exception as e:
        if os.path.exists(audio_path):
            os.unlink(audio_path)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/detect_scenes', methods=['POST'])
def detect_scenes():
    data = request.json
    video_path = data.get('filename')
    
    if not video_path or not os.path.exists(video_path):
        return jsonify({'success': False, 'error': 'Video file not found'}), 404
    
    try:
        scenes = editor.detect_scenes(video_path)
        return jsonify({'success': True, 'scenes': scenes})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/add_captions', methods=['POST'])
def add_captions():
    data = request.json
    video_path = data.get('filename')
    transcription = data.get('transcription')
    
    if not video_path or not os.path.exists(video_path):
        return jsonify({'success': False, 'error': 'Video file not found'}), 404
    
    if not transcription:
        return jsonify({'success': False, 'error': 'No transcription provided'}), 400
    
    output_path = f"output/captioned_{uuid.uuid4().hex}.mp4"
    os.makedirs('output', exist_ok=True)
    
    try:
        if editor.add_captions(video_path, transcription, output_path):
            return jsonify({
                'success': True,
                'output': output_path
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to add captions'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/export/<path:filename>')
def export_video(filename):
    if not os.path.exists(filename):
        return jsonify({'error': 'File not found'}), 404
    
    download_name = 'ai_video_' + os.path.basename(filename)
    return send_file(filename, as_attachment=True, download_name=download_name)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("     ✨ TERA AI VIDEO EDITOR - PROFESSIONAL EDITION ✨    ")
    print("="*60)
    print(" 🚀 India ka sabse sasta AI editor!")
    print(" 💰 ₹9 mein 2 mahine!")
    print(" 🎨 Glassmorphism + Modern UI")
    print("="*60 + "\n")
    print("📂 Uploads folder: ./uploads")
    print("📂 Output folder: ./output")
    print("🌐 Open http://127.0.0.1:5000 in your browser")
    print("🎬 Normal Edit Mode: http://127.0.0.1:5000/normal-edit")
    app.run(debug=True, host='0.0.0.0', port=5000)
