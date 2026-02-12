import streamlit as st
import tempfile
import pandas as pd
from datetime import datetime
import os
import requests
import time
import re
import hashlib
from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Page configuration
st.set_page_config(
    page_title="Speaking Proficiency Test",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 Classroom Speaking Proficiency Test")
st.write("Please complete all parts. Speak clearly and naturally.")

# Input fields
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Full Name", placeholder="Enter your full name")
    institution = st.text_input("Institution", placeholder="Enter your institution")
with col2:
    email = st.text_input("Your Email Address", placeholder="your.email@example.com")
    head_teacher_email = st.text_input("Head Teacher Email (Optional)", placeholder="headteacher@example.com", 
                                       help="If provided, your head teacher will receive a copy of your report")

def transcribe_audio_assemblyai(audio_bytes):
    API_KEY = st.secrets.get("ASSEMBLYAI_API_KEY", "")
    
    if not API_KEY:
        return None, "Error: API key not configured."
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm', mode='wb') as tmp:
        tmp.write(audio_bytes.getvalue())
        tmp_path = tmp.name
    
    try:
        headers = {"authorization": API_KEY}
 # Upload audio
        with open(tmp_path, "rb") as f:
            upload_response = requests.post(
                "https://api.assemblyai.com/v2/upload",
                headers=headers,
                data=f
            )
        
        if upload_response.status_code != 200:
            return None, f"Upload error: {upload_response.text}"
        
        upload_url = upload_response.json().get("upload_url")
        if not upload_url:
            return None, "Error: Failed to get upload URL"
        
        # Request transcription
        transcript_response = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            json={
                "audio_url": upload_url,
                "speech_models": ["universal-2"],
                "punctuate": True,
                "format_text": True
            },
            headers=headers
        )
        
        if transcript_response.status_code != 200:
            return None, f"Transcription request error: {transcript_response.text}"
        
        transcript_data = transcript_response.json()
        transcript_id = transcript_data.get("id")
        
        if not transcript_id:
            return None, f"Error: No transcript ID received."
        
def validate_email(email)
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_html_report(name, institution, email, component_scores, avg_scores, 
                        part1_scores, part2_scores, part3_score, total_score, 
                        max_score, percentage, proficiency_level, strengths, improvements):
    """Generate HTML email report"""
    
    # Determine color and emoji based on proficiency
    if percentage >= 90:
        color = "#00C851"
        emoji = "🌟"
    elif percentage >= 75:
        color = "#33B5E5"
        emoji = "🎯"
    elif percentage >= 60:
        color = "#FFB733"
        emoji = "📈"
    elif percentage >= 45:
        color = "#FF8800"
        emoji = "🌱"
    else:
        color = "#FF4444"
        emoji = "🔰"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 3px solid {color};
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: {color};
                margin: 0;
                font-size: 32px;
            }}
            .score-summary {{
                background: linear-gradient(135deg, {color}22 0%, {color}44 100%);
                padding: 25px;
                border-radius: 10px;
                margin: 20px 0;
                text-align: center;
            }}
            .score-summary h2 {{
                color: {color};
                margin: 0 0 15px 0;
                font-size: 28px;
            }}
            .score-metrics {{
                display: flex;
                justify-content: space-around;
                margin-top: 20px;
            }}
            .metric {{
                text-align: center;
            }}
            .metric-value {{
                font-size: 36px;
                font-weight: bold;
                color: {color};
            }}
            .metric-label {{
                font-size: 14px;
                color: #666;
                margin-top: 5px;
            }}
            .component {{
                margin: 15px 0;
            }}
            .component-header {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 5px;
                font-weight: 600;
            }}
            .progress-bar {{
                background-color: #e0e0e0;
                border-radius: 10px;
                height: 30px;
                overflow: hidden;
            }}
            .progress-fill {{
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                transition: width 0.3s ease;
            }}
            .section {{
                margin: 30px 0;
            }}
            .section h3 {{
                color: {color};
                border-left: 4px solid {color};
                padding-left: 15px;
                margin-bottom: 15px;
            }}
            .feedback-box {{
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid {color};
                margin: 15px 0;
            }}
            .tip {{
                background-color: #e8f5e9;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
                border-left: 3px solid #4CAF50;
            }}
            .tip strong {{
                color: #2e7d32;
            }}
            ul {{
                margin: 10px 0;
                padding-left: 25px;
            }}
            li {{
                margin: 5px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #e0e0e0;
                color: #666;
                font-size: 14px;
            }}
            .info-row {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #eee;
            }}
            .info-label {{
                font-weight: 600;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{emoji} Speaking Proficiency Test Report</h1>
                <p style="color: #666; margin-top: 10px;">Assessment Date: {datetime.now().strftime("%B %d, %Y")}</p>
            </div>
            
            <div class="section">
                <h3>📋 Participant Information</h3>
                <div class="info-row">
                    <span class="info-label">Name:</span>
                    <span>{name}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Institution:</span>
                    <span>{institution}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Email:</span>
                    <span>{email}</span>
                </div>
            </div>
            
            <div class="score-summary">
                <h2>Overall Performance: {proficiency_level}</h2>
                <div class="score-metrics">
                    <div class="metric">
                        <div class="metric-value">{total_score:.1f}</div>
                        <div class="metric-label">Total Score (out of {max_score:.0f})</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{percentage:.1f}%</div>
                        <div class="metric-label">Percentage</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{emoji}</div>
                        <div class="metric-label">{proficiency_level}</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h3>📊 Component Breakdown</h3>
    """
    
    # Add component bars
    for component, avg in avg_scores.items():
        percentage_comp = (avg / 5) * 100
        
        if avg >= 4.5:
            bar_color = "#00C851"
        elif avg >= 3.5:
            bar_color = "#33B5E5"
        elif avg >= 2.5:
            bar_color = "#FFB733"
        else:
            bar_color = "#FF8800"
        
        html += f"""
                <div class="component">
                    <div class="component-header">
                        <span>{component}</span>
                        <span>{avg:.1f}/5</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {percentage_comp}%; background-color: {bar_color};">
                            {percentage_comp:.0f}%
                        </div>
                    </div>
                </div>
        """
    
    html += """
            </div>
            
            <div class="section">
                <h3>✅ Your Strengths</h3>
    """
    
    if strengths:
        html += f"""
                <div class="feedback-box">
                    <p><strong>Excellent performance in:</strong> {', '.join(strengths)}</p>
                    <p>These areas showcase your natural abilities. Continue to leverage these skills in your teaching!</p>
                </div>
        """
    else:
        html += """
                <div class="feedback-box">
                    <p>Keep working on all areas to identify your strengths. Consistent practice will help you discover where you excel!</p>
                </div>
        """
    
    html += """
            </div>
            
            <div class="section">
                <h3>🎯 Areas for Growth</h3>
    """
    
    if improvements:
        html += f"""
                <div class="feedback-box">
                    <p><strong>Focus on:</strong> {', '.join(improvements)}</p>
                    <p>Targeted practice in these areas will significantly improve your overall performance.</p>
                </div>
                
                <h4 style="margin-top: 20px;">Personalized Development Tips:</h4>
        """
        
        for area in improvements:
            if area == "Accuracy":
                html += """
                <div class="tip">
                    <strong>Accuracy</strong>
                    <ul>
                        <li>Listen carefully to the complete sentence before speaking</li>
                        <li>Practice repeating slowly and clearly rather than rushing</li>
                        <li>Record yourself and compare with the original</li>
                        <li>Focus on pronouncing each word distinctly</li>
                    </ul>
                </div>
                """
            elif area == "Fluency":
                html += """
                <div class="tip">
                    <strong>Fluency</strong>
                    <ul>
                        <li>Aim for 120-160 words per minute (natural conversational pace)</li>
                        <li>Reduce filler words ('um', 'uh', 'like') through awareness</li>
                        <li>Practice speaking on topics for 60 seconds without stopping</li>
                        <li>Record yourself daily to track improvement</li>
                    </ul>
                </div>
                """
            elif area == "Intonation":
                html += """
                <div class="tip">
                    <strong>Intonation</strong>
                    <ul>
                        <li>Vary your pitch for questions (rising) and statements (falling)</li>
                        <li>Emphasize key words in sentences</li>
                        <li>Read children's stories aloud with expression to practice</li>
                        <li>Listen to skilled speakers and mimic their patterns</li>
                    </ul>
                </div>
                """
            elif area == "Vocabulary":
                html += """
                <div class="tip">
                    <strong>Vocabulary</strong>
                    <ul>
                        <li>Learn 3-5 new academic/professional words weekly</li>
                        <li>Use synonyms when explaining familiar concepts</li>
                        <li>Read educational articles and note useful phrases</li>
                        <li>Practice using varied vocabulary in daily conversations</li>
                    </ul>
                </div>
                """
            elif area == "Grammar":
                html += """
                <div class="tip">
                    <strong>Grammar</strong>
                    <ul>
                        <li>Speak in complete sentences with clear subjects and verbs</li>
                        <li>Practice organizing your thoughts before speaking</li>
                        <li>Review basic sentence structure patterns</li>
                        <li>Listen to your recordings to identify grammar patterns</li>
                    </ul>
                </div>
                """
    else:
        html += """
                <div class="feedback-box">
                    <p>Great job! You're performing well across all areas. Continue practicing to maintain your skills!</p>
                </div>
        """
    
    html += """
            </div>
            
            <div class="section">
                <h3>📚 Daily Practice Recommendations</h3>
                <div class="feedback-box">
                    <h4>Daily Routines (10-15 minutes)</h4>
                    <ul>
                        <li>Record 2-minute explanations of simple topics</li>
                        <li>Practice classroom instructions aloud</li>
                        <li>Read educational content aloud</li>
                        <li>Shadow native speakers from videos</li>
                        <li>Review and compare your recordings</li>
                    </ul>
                    
                    <h4>Weekly Goals</h4>
                    <ul>
                        <li>Join a speaking practice group</li>
                        <li>Record a 5-minute lesson segment</li>
                        <li>Practice with a colleague and give feedback</li>
                        <li>Watch teaching videos and analyze speech</li>
                        <li>Set specific improvement targets</li>
                    </ul>
                </div>
            </div>
            
            <div class="section">
                <h3>🎓 Next Steps</h3>
                <div class="feedback-box">
                    <ol>
                        <li>Review your component scores and focus areas</li>
                        <li>Implement the personalized tips in your daily practice</li>
                        <li>Track your progress by retaking the test in 4-6 weeks</li>
                        <li>Share your goals with a colleague for accountability</li>
                    </ol>
                    <p style="margin-top: 15px;"><em>Remember: Effective communication is a journey. Every practice session brings you closer to becoming a more confident and effective educator!</em></p>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>Speaking Proficiency Assessment System v2.0</strong></p>
                <p>This report was automatically generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
                <p>Keep practicing, stay confident, and celebrate every improvement! 🌟</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def send_email_report(recipient_email, name, html_content):
    """Send email with HTML report"""
    try:
        # Get email configuration from secrets
        sender_email = st.secrets.get("SENDER_EMAIL", "")
        sender_password = st.secrets.get("SENDER_PASSWORD", "")
        smtp_server = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = st.secrets.get("SMTP_PORT", 587)
        
        if not sender_email or not sender_password:
            return False, "Email credentials not configured in secrets"
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Your Speaking Proficiency Test Results - {name}"
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True, "Email sent successfully!"
        
    except smtplib.SMTPAuthenticationError:
        return False, "Email authentication failed. Please check your credentials."
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

def generate_head_teacher_report(name, institution, teacher_email, component_scores, avg_scores, 
                                 part1_scores, part2_scores, part3_score, total_score, 
                                 max_score, percentage, proficiency_level, strengths, improvements):
    """Generate HTML report for head teacher with summary focus"""
    
    # Determine color and emoji based on proficiency
    if percentage >= 90:
        color = "#00C851"
        emoji = "🌟"
    elif percentage >= 75:
        color = "#33B5E5"
        emoji = "🎯"
    elif percentage >= 60:
        color = "#FFB733"
        emoji = "📈"
    elif percentage >= 45:
        color = "#FF8800"
        emoji = "🌱"
    else:
        color = "#FF4444"
        emoji = "🔰"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 3px solid #2196F3;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: #2196F3;
                margin: 0;
                font-size: 32px;
            }}
            .header p {{
                color: #666;
                margin-top: 10px;
            }}
            .admin-badge {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 8px 20px;
                border-radius: 20px;
                display: inline-block;
                font-size: 14px;
                margin-top: 10px;
            }}
            .score-summary {{
                background: linear-gradient(135deg, {color}22 0%, {color}44 100%);
                padding: 25px;
                border-radius: 10px;
                margin: 20px 0;
                text-align: center;
            }}
            .score-summary h2 {{
                color: {color};
                margin: 0 0 15px 0;
                font-size: 28px;
            }}
            .score-metrics {{
                display: flex;
                justify-content: space-around;
                margin-top: 20px;
                flex-wrap: wrap;
            }}
            .metric {{
                text-align: center;
                min-width: 120px;
                margin: 10px;
            }}
            .metric-value {{
                font-size: 36px;
                font-weight: bold;
                color: {color};
            }}
            .metric-label {{
                font-size: 14px;
                color: #666;
                margin-top: 5px;
            }}
            .component {{
                margin: 15px 0;
            }}
            .component-header {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 5px;
                font-weight: 600;
            }}
            .progress-bar {{
                background-color: #e0e0e0;
                border-radius: 10px;
                height: 30px;
                overflow: hidden;
            }}
            .progress-fill {{
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                transition: width 0.3s ease;
            }}
            .section {{
                margin: 30px 0;
            }}
            .section h3 {{
                color: #2196F3;
                border-left: 4px solid #2196F3;
                padding-left: 15px;
                margin-bottom: 15px;
            }}
            .info-card {{
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 8px;
                margin: 15px 0;
                border-left: 4px solid #2196F3;
            }}
            .info-row {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #eee;
            }}
            .info-label {{
                font-weight: 600;
                color: #666;
            }}
            .recommendation-box {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 20px;
                border-radius: 5px;
                margin: 15px 0;
            }}
            .recommendation-box h4 {{
                color: #856404;
                margin-top: 0;
            }}
            .strength-box {{
                background-color: #d4edda;
                border-left: 4px solid #28a745;
                padding: 20px;
                border-radius: 5px;
                margin: 15px 0;
            }}
            .strength-box h4 {{
                color: #155724;
                margin-top: 0;
            }}
            .table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            .table th, .table td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            .table th {{
                background-color: #2196F3;
                color: white;
            }}
            .table tr:hover {{
                background-color: #f5f5f5;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #e0e0e0;
                color: #666;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Speaking Proficiency Assessment Report</h1>
                <div class="admin-badge">👨‍💼 Head Teacher Copy</div>
                <p>Assessment Date: {datetime.now().strftime("%B %d, %Y")}</p>
            </div>
            
            <div class="section">
                <h3>👤 Teacher Information</h3>
                <div class="info-card">
                    <div class="info-row">
                        <span class="info-label">Teacher Name:</span>
                        <span><strong>{name}</strong></span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Institution:</span>
                        <span>{institution}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Email:</span>
                        <span>{teacher_email}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Assessment Date:</span>
                        <span>{datetime.now().strftime("%B %d, %Y at %I:%M %p")}</span>
                    </div>
                </div>
            </div>
            
            <div class="score-summary">
                <h2>{emoji} Overall Performance: {proficiency_level}</h2>
                <div class="score-metrics">
                    <div class="metric">
                        <div class="metric-value">{total_score:.1f}</div>
                        <div class="metric-label">Total Score (out of {max_score:.0f})</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{percentage:.1f}%</div>
                        <div class="metric-label">Percentage</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{proficiency_level}</div>
                        <div class="metric-label">Proficiency Level</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h3>📊 Detailed Performance Breakdown</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Component</th>
                            <th>Score (out of 5)</th>
                            <th>Percentage</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for component, avg in avg_scores.items():
        percentage_comp = (avg / 5) * 100
        if avg >= 4.0:
            status = "✅ Strong"
            status_color = "#28a745"
        elif avg >= 3.0:
            status = "⚠️ Developing"
            status_color = "#ffc107"
        else:
            status = "🎯 Needs Focus"
            status_color = "#dc3545"
        
        html += f"""
                        <tr>
                            <td><strong>{component}</strong></td>
                            <td>{avg:.1f}</td>
                            <td>{percentage_comp:.0f}%</td>
                            <td style="color: {status_color};">{status}</td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h3>📈 Component Analysis Chart</h3>
    """
    
    for component, avg in avg_scores.items():
        percentage_comp = (avg / 5) * 100
        
        if avg >= 4.5:
            bar_color = "#00C851"
        elif avg >= 3.5:
            bar_color = "#33B5E5"
        elif avg >= 2.5:
            bar_color = "#FFB733"
        else:
            bar_color = "#FF8800"
        
        html += f"""
                <div class="component">
                    <div class="component-header">
                        <span>{component}</span>
                        <span>{avg:.1f}/5 ({percentage_comp:.0f}%)</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {percentage_comp}%; background-color: {bar_color};">
                        </div>
                    </div>
                </div>
        """
    
    html += """
            </div>
    """
    
    if strengths:
        html += f"""
            <div class="section">
                <div class="strength-box">
                    <h4>✅ Key Strengths</h4>
                    <p><strong>{name}</strong> demonstrates strong performance in: <strong>{', '.join(strengths)}</strong></p>
                    <p>These areas indicate natural teaching communication abilities that should be encouraged and utilized in professional development opportunities.</p>
                </div>
            </div>
        """
    
    if improvements:
        html += f"""
            <div class="section">
                <div class="recommendation-box">
                    <h4>🎯 Recommended Focus Areas</h4>
                    <p><strong>{name}</strong> would benefit from targeted development in: <strong>{', '.join(improvements)}</strong></p>
                    <p><strong>Suggested Actions for Administration:</strong></p>
                    <ul>
        """
        
        for area in improvements:
            if area == "Fluency":
                html += "<li>Consider enrolling in speaking fluency workshops or coaching sessions</li>"
            elif area == "Pronunciation" or area == "Accuracy":
                html += "<li>Provide access to pronunciation improvement resources or speech coaching</li>"
            elif area == "Vocabulary":
                html += "<li>Encourage participation in academic vocabulary development programs</li>"
            elif area == "Grammar":
                html += "<li>Recommend grammar refresher courses or peer mentoring</li>"
            elif area == "Intonation":
                html += "<li>Suggest voice modulation and public speaking training</li>"
        
        html += """
                    </ul>
                </div>
            </div>
        """
    
    html += f"""
            <div class="section">
                <h3>📋 Summary Assessment</h3>
                <div class="info-card">
                    <table class="table">
                        <tr>
                            <th>Assessment Part</th>
                            <th>Completion</th>
                            <th>Average Score</th>
                        </tr>
                        <tr>
                            <td>Part 1: Sentence Repetition</td>
                            <td>{len(part1_scores)}/5 sentences</td>
                            <td>{(sum(part1_scores) / len(part1_scores)):.1f}/5 if part1_scores else 0</td>
                        </tr>
                        <tr>
                            <td>Part 2: Question Responses</td>
                            <td>{len(part2_scores)}/3 questions</td>
                            <td>{(sum(part2_scores) / len(part2_scores)):.1f}/5 if part2_scores else 0</td>
                        </tr>
                        <tr>
                            <td>Part 3: Free Explanation</td>
                            <td>{'✓ Completed' if part3_score > 0 else '✗ Not Completed'}</td>
                            <td>{part3_score:.1f}/5</td>
                        </tr>
                    </table>
                </div>
            </div>
            
            <div class="section">
                <h3>💡 Administrative Recommendations</h3>
                <div class="info-card">
    """
    
    if percentage >= 90:
        html += f"""
                    <p><strong>Recognition:</strong> {name} demonstrates exceptional speaking proficiency. Consider this teacher for:</p>
                    <ul>
                        <li>Peer mentoring or coaching roles</li>
                        <li>Professional development workshop facilitation</li>
                        <li>Demonstration lessons for new teachers</li>
                        <li>Leading communication skills training</li>
                    </ul>
        """
    elif percentage >= 75:
        html += f"""
                    <p><strong>Development:</strong> {name} shows strong speaking skills with room for refinement. Recommendations:</p>
                    <ul>
                        <li>Encourage participation in advanced communication workshops</li>
                        <li>Provide opportunities to present at staff meetings</li>
                        <li>Consider for professional development committee membership</li>
                        <li>Support with targeted improvement in identified focus areas</li>
                    </ul>
        """
    elif percentage >= 60:
        html += f"""
                    <p><strong>Support Needed:</strong> {name} demonstrates developing speaking skills. Recommended actions:</p>
                    <ul>
                        <li>Enroll in professional communication development programs</li>
                        <li>Assign a peer mentor with strong communication skills</li>
                        <li>Provide regular feedback and observation opportunities</li>
                        <li>Schedule follow-up assessment in 3-6 months</li>
                    </ul>
        """
    else:
        html += f"""
                    <p><strong>Immediate Support Required:</strong> {name} requires focused support for speaking proficiency. Action plan:</p>
                    <ul>
                        <li>Priority enrollment in speaking skills development program</li>
                        <li>Weekly coaching sessions with communication specialist</li>
                        <li>Structured improvement plan with clear milestones</li>
                        <li>Monthly progress assessments and feedback sessions</li>
                        <li>Consider additional language support resources if needed</li>
                    </ul>
        """
    
    html += """
                </div>
            </div>
            
            <div class="section">
                <h3>📅 Follow-up Recommendations</h3>
                <div class="info-card">
                    <ul>
                        <li><strong>Next Assessment:</strong> Schedule reassessment in 4-6 months to track progress</li>
                        <li><strong>Development Plan:</strong> Create personalized improvement plan based on focus areas</li>
                        <li><strong>Resources:</strong> Provide access to recommended training materials and workshops</li>
                        <li><strong>Monitoring:</strong> Schedule quarterly check-ins to review progress and adjust support</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>Speaking Proficiency Assessment System v2.0</strong></p>
                <p><em>Administrative Report - Confidential</em></p>
                <p>This report was automatically generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
                <p style="margin-top: 15px; font-size: 12px;">
                    Note: This assessment is designed to support teacher development and should be used 
                    constructively as part of a comprehensive professional development program.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def send_head_teacher_email(recipient_email, teacher_name, html_content):
    """Send email to head teacher with assessment summary"""
    try:
        # Get email configuration from secrets
        sender_email = st.secrets.get("SENDER_EMAIL", "")
        sender_password = st.secrets.get("SENDER_PASSWORD", "")
        smtp_server = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = st.secrets.get("SMTP_PORT", 587)
        
        if not sender_email or not sender_password:
            return False, "Email credentials not configured in secrets"
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Speaking Assessment Report - {teacher_name}"
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True, "Email sent successfully!"
        
    except smtplib.SMTPAuthenticationError:
        return False, "Email authentication failed. Please check your credentials."
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

def transcribe_audio_assemblyai(audio_bytes):
    """Transcribe audio using AssemblyAI API with improved error handling"""
    API_KEY = st.secrets.get("ASSEMBLYAI_API_KEY", "")
    
    if not API_KEY:
        return None, "Error: AssemblyAI API key not configured in Streamlit secrets."
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm', mode='wb') as tmp:
        tmp.write(audio_bytes.getvalue())
        tmp_path = tmp.name
    
    try:
        headers = {"authorization": API_KEY}
        
        # Upload audio
        with open(tmp_path, "rb") as f:
            upload_response = requests.post(
                "https://api.assemblyai.com/v2/upload",
                headers=headers,
                data=f,
                timeout=30
            )
        
        if upload_response.status_code != 200:
            return None, f"Upload error: {upload_response.text}"
        
        upload_url = upload_response.json().get("upload_url")
        if not upload_url:
            return None, "Error: Failed to get upload URL"
        
        # Request transcription
        transcript_response = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            json={
                "audio_url": upload_url,
                "speech_models": ["best"],
                "punctuate": True,
                "format_text": True
            },
            headers=headers,
            timeout=30
        )
        
        if transcript_response.status_code != 200:
            return None, f"Transcription request error: {transcript_response.text}"
        
        transcript_data = transcript_response.json()
        transcript_id = transcript_data.get("id")
        
        if not transcript_id:
            return None, "Error: No transcript ID received"
        
        # Poll for completion with timeout
        max_attempts = 90
        for attempt in range(max_attempts):
            status_response = requests.get(
                f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                headers=headers,
                timeout=30
            )
            
            if status_response.status_code != 200:
                return None, f"Status check error: {status_response.text}"
            
            result = status_response.json()
            status = result.get("status")
            
            if status == "completed":
                return result, None
            elif status == "error":
                error_msg = result.get("error", "Unknown error")
                return None, f"Transcription failed: {error_msg}"
            
            time.sleep(2)
        
        return None, "Error: Transcription timeout (exceeded 3 minutes)"
    
    except requests.exceptions.Timeout:
        return None, "Error: Request timeout. Please check your internet connection."
    except requests.exceptions.RequestException as e:
        return None, f"Error: Network error - {str(e)}"
    except Exception as e:
        return None, f"Error: {str(e)}"
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass

def display_star_rating(score, label):
    """Display score as stars (out of 5)"""
    filled_stars = int(round(score))
    empty_stars = 5 - filled_stars
    stars = "⭐" * filled_stars + "☆" * empty_stars
    st.write(f"**{label}:** {stars} ({score:.1f}/5)")

def calculate_accuracy_score(transcript, reference):
    """Calculate word accuracy score based on reference text"""
    if not transcript or not reference:
        return 0.5
    
    # Normalize text
    transcript_lower = transcript.lower()
    reference_lower = reference.lower()
    
    # Remove punctuation for comparison
    transcript_clean = re.sub(r'[^\w\s]', '', transcript_lower)
    reference_clean = re.sub(r'[^\w\s]', '', reference_lower)
    
    transcript_words = set(transcript_clean.split())
    reference_words = set(reference_clean.split())
    
    if not reference_words:
        return 0.5
    
    # Calculate matches
    matches = len(transcript_words & reference_words)
    total_ref_words = len(reference_words)
    
    # Score based on percentage of reference words found
    accuracy_ratio = matches / total_ref_words
    
    # Convert to 5-point scale with better distribution
    if accuracy_ratio >= 0.95:
        score = 5.0
    elif accuracy_ratio >= 0.85:
        score = 4.5
    elif accuracy_ratio >= 0.75:
        score = 4.0
    elif accuracy_ratio >= 0.65:
        score = 3.5
    elif accuracy_ratio >= 0.55:
        score = 3.0
    elif accuracy_ratio >= 0.45:
        score = 2.5
    elif accuracy_ratio >= 0.35:
        score = 2.0
    elif accuracy_ratio >= 0.25:
        score = 1.5
    elif accuracy_ratio >= 0.15:
        score = 1.0
    else:
        score = 0.5
    
    return round(score, 1)

def calculate_fluency_score(transcript, audio_duration=None):
    """
    Calculate fluency based on:
    1. Speaking rate (words per minute)
    2. Pronunciation quality (approximated via word completeness)
    3. Verbal pauses (filler words and hesitations)
    """
    if not transcript or len(transcript.strip()) < 3:
        return 0.5
    
    words = transcript.split()
    word_count = len(words)
    
    if word_count == 0:
        return 0.5
    
    # === 1. SPEAKING RATE (Speed) ===
    # Ideal rate: 120-160 words per minute
    if audio_duration and audio_duration > 0:
        wpm = (word_count / audio_duration) * 60
    else:
        # Estimate: assume 2 seconds per word for short clips
        estimated_duration = max(word_count * 2, 10)
        wpm = (word_count / estimated_duration) * 60
    
    # Score speaking rate
    if 120 <= wpm <= 160:
        rate_score = 2.0  # Optimal rate
    elif 100 <= wpm < 120 or 160 < wpm <= 180:
        rate_score = 1.5  # Acceptable
    elif 80 <= wpm < 100 or 180 < wpm <= 200:
        rate_score = 1.0  # Needs improvement
    else:
        rate_score = 0.5  # Too slow or too fast
    
    # === 2. PRONUNCIATION QUALITY ===
    # Approximate pronunciation by checking for complete, recognizable words
    well_formed_words = [w for w in words if len(w) > 2 and w.isalpha()]
    pronunciation_ratio = len(well_formed_words) / word_count if word_count > 0 else 0
    
    if pronunciation_ratio >= 0.85:
        pronunciation_score = 2.0
    elif pronunciation_ratio >= 0.70:
        pronunciation_score = 1.5
    elif pronunciation_ratio >= 0.55:
        pronunciation_score = 1.0
    else:
        pronunciation_score = 0.5
    
    # === 3. VERBAL PAUSES (Fillers and Hesitations) ===
    filler_words = ['um', 'uh', 'like', 'you know', 'so', 'actually', 'basically', 
                    'er', 'hmm', 'well', 'kind of', 'sort of', 'i mean']
    
    # Count filler occurrences
    text_lower = transcript.lower()
    filler_count = sum(text_lower.count(' ' + filler + ' ') for filler in filler_words)
    
    # Calculate filler ratio
    filler_ratio = filler_count / word_count if word_count > 0 else 0
    
    # Score verbal pauses (lower filler ratio = better score)
    if filler_ratio <= 0.05:  # Less than 5% fillers
        pause_score = 1.0
    elif filler_ratio <= 0.10:  # 5-10% fillers
        pause_score = 0.75
    elif filler_ratio <= 0.15:  # 10-15% fillers
        pause_score = 0.5
    else:  # More than 15% fillers
        pause_score = 0.25
    
    # === TOTAL FLUENCY SCORE ===
    total_score = rate_score + pronunciation_score + pause_score
    
    # Ensure score is between 0.5 and 5.0
    final_score = max(0.5, min(5.0, total_score))
    
    return round(final_score, 1)

def calculate_intonation_score(result):
    """
    Calculate intonation based on:
    1. Pitch variation (estimated from punctuation and sentence structure)
    2. Stress patterns (emphasized words, varied sentence types)
    3. Volume dynamics (approximated from text features)
    """
    text = result.get("text", "")
    
    if not text or len(text.strip()) < 10:
        return 1.0
    
    # === 1. PITCH VARIATION ===
    # Indicated by questions, exclamations, and varied sentence types
    has_question = "?" in text
    has_exclamation = "!" in text
    has_period = "." in text
    
    question_count = text.count("?")
    exclamation_count = text.count("!")
    
    # Score pitch variation
    pitch_score = 1.0  # Base
    if has_question:
        pitch_score += 0.5
    if has_exclamation:
        pitch_score += 0.4
    if question_count + exclamation_count >= 2:
        pitch_score += 0.3  # Multiple varied sentences
    
    pitch_score = min(pitch_score, 2.0)
    
    # === 2. STRESS PATTERNS ===
    # Estimated from sentence length variety and comma usage
    sentences = re.split(r'[.!?]+', text)
    sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
    
    has_comma = "," in text
    comma_count = text.count(",")
    
    # Check for length variation
    if len(sentence_lengths) >= 2:
        length_variance = len(set(sentence_lengths)) > 1
    else:
        length_variance = False
    
    stress_score = 1.0  # Base
    
    if has_comma:
        stress_score += 0.3
    if comma_count >= 2:
        stress_score += 0.2
    if length_variance:
        stress_score += 0.5
    
    # Check for capitalized words (potential emphasis)
    words = text.split()
    mid_sentence_caps = sum(1 for w in words[1:] if w and w[0].isupper() and w not in ['I'])
    if mid_sentence_caps > 0:
        stress_score += 0.3
    
    stress_score = min(stress_score, 2.0)
    
    # === 3. VOLUME DYNAMICS ===
    # Approximated by exclamations and emphasis markers
    all_caps_words = sum(1 for w in words if w.isupper() and len(w) > 1)
    has_repetition = len(words) != len(set(words))
    
    volume_score = 0.5  # Base
    
    if has_exclamation:
        volume_score += 0.3
    if all_caps_words > 0:
        volume_score += 0.2
    if has_repetition:
        volume_score += 0.2
    
    volume_score = min(volume_score, 1.0)
    
    # === TOTAL INTONATION SCORE ===
    total_score = pitch_score + stress_score + volume_score
    
    # Ensure variation between 1.0 and 5.0
    final_score = max(1.0, min(5.0, total_score))
    
    return round(final_score, 1)

def calculate_vocabulary_score(transcript):
    """Calculate vocabulary richness and variety"""
    if not transcript or len(transcript.strip()) < 5:
        return 0.5
    
    words = transcript.lower().split()
    unique_words = set(words)
    
    if len(words) == 0:
        return 0.5
    
    # Vocabulary diversity ratio
    diversity = len(unique_words) / len(words)
    
    # Advanced word count (words longer than 6 letters)
    advanced_words = [w for w in words if len(w) > 6 and w.isalpha()]
    advanced_ratio = len(advanced_words) / len(words) if words else 0
    
    # Academic/professional vocabulary
    academic_indicators = ['assessment', 'evaluation', 'analyze', 'demonstrate', 
                          'implement', 'objective', 'criteria', 'performance',
                          'develop', 'instruction', 'comprehension', 'formative',
                          'summative', 'differentiate', 'pedagogy']
    academic_count = sum(1 for word in words if word in academic_indicators)
    academic_ratio = academic_count / len(words) if words else 0
    
    # Base score on diversity (0-3 points)
    base_score = min(diversity * 3, 3.0)
    
    # Bonus for advanced vocabulary (0-1.5 points)
    advanced_bonus = min(advanced_ratio * 1.5, 1.5)
    
    # Bonus for academic vocabulary (0-0.5 points)
    academic_bonus = min(academic_ratio * 20, 0.5)
    
    final_score = min(base_score + advanced_bonus + academic_bonus, 5.0)
    
    return max(0.5, round(final_score, 1))

def calculate_grammar_score(transcript):
    """
    Comprehensive grammar assessment based on:
    1. Sentence structure and completeness
    2. Subject-verb agreement patterns
    3. Proper use of articles, prepositions, and conjunctions
    4. Sentence variety and complexity
    """
    if not transcript or len(transcript.strip()) < 5:
        return 0.5
    
    words = transcript.split()
    text_lower = transcript.lower()
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', transcript)
    complete_sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) >= 3]
    
    if len(complete_sentences) == 0:
        return 1.0
    
    # === 1. SENTENCE STRUCTURE (2.0 points) ===
    structure_score = 0.5  # Base
    
    # Check for proper capitalization
    proper_caps = sum(1 for s in complete_sentences if s and s[0].isupper())
    if proper_caps > 0:
        structure_score += 0.5
    
    # Check for complete sentences
    sentence_count = len(complete_sentences)
    if sentence_count >= 2:
        structure_score += 0.5
    if sentence_count >= 3:
        structure_score += 0.5
    
    structure_score = min(structure_score, 2.0)
    
    # === 2. VERB USAGE (1.5 points) ===
    verb_score = 0
    
    common_verbs = ['is', 'are', 'am', 'was', 'were', 'be', 'been', 'being',
                   'have', 'has', 'had', 'do', 'does', 'did',
                   'will', 'would', 'can', 'could', 'should', 'shall', 'may', 'might', 'must']
    
    verb_count = sum(1 for word in text_lower.split() if word in common_verbs)
    
    if verb_count >= 1:
        verb_score += 0.5
    if verb_count >= 2:
        verb_score += 0.5
    if verb_count >= 3:
        verb_score += 0.5
    
    verb_score = min(verb_score, 1.5)
    
    # === 3. ARTICLES, PREPOSITIONS, CONJUNCTIONS (1.0 point) ===
    function_score = 0
    
    articles = ['a', 'an', 'the']
    prepositions = ['in', 'on', 'at', 'to', 'for', 'with', 'by', 'from', 'of', 'about']
    conjunctions = ['and', 'but', 'or', 'so', 'because', 'if', 'when', 'while', 'although']
    
    has_articles = any(article in text_lower.split() for article in articles)
    has_prepositions = any(prep in text_lower.split() for prep in prepositions)
    has_conjunctions = any(conj in text_lower.split() for conj in conjunctions)
    
    if has_articles:
        function_score += 0.3
    if has_prepositions:
        function_score += 0.4
    if has_conjunctions:
        function_score += 0.3
    
    function_score = min(function_score, 1.0)
    
    # === 4. SENTENCE VARIETY & COMPLEXITY (0.5 points) ===
    variety_score = 0
    
    # Check sentence length variety
    sentence_lengths = [len(s.split()) for s in complete_sentences]
    if len(set(sentence_lengths)) > 1:
        variety_score += 0.25
    
    # Check for complex sentences
    subordinate_markers = ['because', 'since', 'although', 'while', 'if', 'when', 'that', 'which', 'who']
    has_complexity = any(marker in text_lower.split() for marker in subordinate_markers)
    if has_complexity:
        variety_score += 0.25
    
    variety_score = min(variety_score, 0.5)
    
    # === TOTAL GRAMMAR SCORE ===
    total_score = structure_score + verb_score + function_score + variety_score
    
    # Ensure variation between 0.5 and 5.0
    final_score = max(0.5, min(5.0, total_score))
    
    return round(final_score, 1)

# Initialize session state
if 'part1_recordings' not in st.session_state:
    st.session_state.part1_recordings = {}
if 'part2_recordings' not in st.session_state:
    st.session_state.part2_recordings = {}
if 'part3_recording' not in st.session_state:
    st.session_state.part3_recording = None
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Calculate progress
def calculate_progress():
    """Calculate overall test completion progress"""
    sentences = 5
    prompts = 3
    total = sentences + prompts + 1
    
    completed = len(st.session_state.part1_recordings) + \
                len(st.session_state.part2_recordings) + \
                (1 if st.session_state.part3_recording else 0)
    
    return completed, total

completed, total = calculate_progress()
progress_percentage = completed / total

# Display progress bar
st.markdown("### 📊 Test Progress")
st.progress(progress_percentage)
st.write(f"**{completed}/{total} recordings completed** ({int(progress_percentage * 100)}%)")
st.markdown("---")

# Part 1: Repeat the Sentence
st.header("📝 Part 1: Repeat the Sentence")
st.write("*Listen to each sentence and repeat it exactly as you hear it.*")
st.write("*Rubric: Accuracy, Fluency, Intonation (each out of 5 stars)*")

sentences = [
    "Please open your books to page ten.",
    "Work in pairs and discuss the question.",
    "You have five minutes to complete this task.",
    "Did everyone understand the instructions?",
    "First, read the passage carefully, then answer the questions."
]

for i, sentence in enumerate(sentences):
    with st.expander(f"Sentence {i+1}: {sentence}", expanded=True):
        st.write(f"**📢 Sentence:** {sentence}")
        
        # Display previous result if exists
        if f"sentence_{i}" in st.session_state.part1_recordings:
            rec = st.session_state.part1_recordings[f"sentence_{i}"]
            st.success("✅ Recorded")
            st.write(f"*Your response: {rec['transcript']}*")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                display_star_rating(rec["accuracy"], "Accuracy")
            with col2:
                display_star_rating(rec["fluency"], "Fluency")
            with col3:
                display_star_rating(rec["intonation"], "Intonation")
        
        audio = st.audio_input(f"🎤 Record your response", key=f"p1_{i}")
        
        if audio:
            audio_hash = get_audio_hash(audio)
            
            # Check if this is a new recording
            if f"sentence_{i}" not in st.session_state.part1_recordings or \
               st.session_state.part1_recordings[f"sentence_{i}"].get("audio_hash") != audio_hash:
                
                with st.spinner("🔄 Transcribing and analyzing your response..."):
                    result, error = transcribe_audio_assemblyai(audio)
                
                if error:
                    st.error(f"⚠️ {error}")
                    st.info("💡 **Troubleshooting tips:**\n- Check your internet connection\n- Ensure you spoke clearly\n- Try recording again")
                elif result:
                    transcript = result.get("text", "")
                    audio_duration = result.get("audio_duration", None)
                    
                    if transcript and transcript.strip() and transcript != "No speech detected":
                        st.write(f"*📝 Transcript: {transcript}*")
                        
                        # Calculate scores
                        accuracy = calculate_accuracy_score(transcript, sentence)
                        fluency = calculate_fluency_score(transcript, audio_duration)
                        intonation = calculate_intonation_score(result)
                        
                        # Store results
                        st.session_state.part1_recordings[f"sentence_{i}"] = {
                            "audio_hash": audio_hash,
                            "transcript": transcript,
                            "accuracy": accuracy,
                            "fluency": fluency,
                            "intonation": intonation,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        st.rerun()
                    else:
                        st.warning("⚠️ No clear speech detected. Please try recording again and speak more clearly.")

st.markdown("---")

# Part 2: Respond to Student Questions
st.header("💬 Part 2: Respond to Student Questions")
st.write("*A student asks you a question. Respond naturally in 1-2 sentences.*")
st.write("*Rubric: Vocabulary, Grammar, Fluency, Intonation (each out of 5 stars)*")

prompts = [
    "When will attendance be uploaded?",
    "Can we submit the assignment late?",
    "How do you differentiate between formative and summative assessment?"
]

for i, prompt in enumerate(prompts):
    with st.expander(f"Question {i+1}: {prompt}", expanded=True):
        st.write(f"**🎓 Student asks:** *'{prompt}'*")
        
        # Display previous result if exists
        if f"prompt_{i}" in st.session_state.part2_recordings:
            rec = st.session_state.part2_recordings[f"prompt_{i}"]
            st.success("✅ Recorded")
            st.write(f"*Your response: {rec['transcript']}*")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                display_star_rating(rec["vocabulary"], "Vocabulary")
            with col2:
                display_star_rating(rec["grammar"], "Grammar")
            with col3:
                display_star_rating(rec["fluency"], "Fluency")
            with col4:
                display_star_rating(rec["intonation"], "Intonation")
        
        audio = st.audio_input("🎤 Record your response", key=f"p2_{i}")
        
        if audio:
            audio_hash = get_audio_hash(audio)
            
            if f"prompt_{i}" not in st.session_state.part2_recordings or \
               st.session_state.part2_recordings[f"prompt_{i}"].get("audio_hash") != audio_hash:
                
                with st.spinner("🔄 Transcribing and analyzing your response..."):
                    result, error = transcribe_audio_assemblyai(audio)
                
                if error:
                    st.error(f"⚠️ {error}")
                    st.info("💡 **Troubleshooting tips:**\n- Check your internet connection\n- Ensure you spoke clearly\n- Try recording again")
                elif result:
                    transcript = result.get("text", "")
                    audio_duration = result.get("audio_duration", None)
                    
                    if transcript and transcript.strip() and transcript != "No speech detected":
                        st.write(f"*📝 Transcript: {transcript}*")
                        
                        # Calculate scores
                        vocabulary = calculate_vocabulary_score(transcript)
                        grammar = calculate_grammar_score(transcript)
                        fluency = calculate_fluency_score(transcript, audio_duration)
                        intonation = calculate_intonation_score(result)
                        
                        # Store results
                        st.session_state.part2_recordings[f"prompt_{i}"] = {
                            "audio_hash": audio_hash,
                            "transcript": transcript,
                            "vocabulary": vocabulary,
                            "grammar": grammar,
                            "fluency": fluency,
                            "intonation": intonation,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        st.rerun()
                    else:
                        st.warning("⚠️ No clear speech detected. Please try recording again and speak more clearly.")

st.markdown("---")

# Part 3: Free Explanation
st.header("🗣️ Part 3: Free Explanation")
st.write("*Explain a teaching concept in your own words (aim for 30-60 seconds).*")
st.write("*Rubric: Vocabulary, Grammar, Fluency, Intonation (each out of 5 stars)*")

with st.expander("Question: Explain how to write a good paragraph", expanded=True):
    st.write("**📚 Topic:** Explain how to write a good paragraph")
    st.info("💡 **Tip:** Include key elements like topic sentences, supporting details, and transitions.")
    
    # Display previous result if exists
    if st.session_state.part3_recording:
        rec = st.session_state.part3_recording
        st.success("✅ Recorded")
        st.write(f"*Your response: {rec['transcript']}*")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            display_star_rating(rec["vocabulary"], "Vocabulary")
        with col2:
            display_star_rating(rec["grammar"], "Grammar")
        with col3:
            display_star_rating(rec["fluency"], "Fluency")
        with col4:
            display_star_rating(rec["intonation"], "Intonation")
    
    audio3 = st.audio_input("🎤 Record your explanation", key="p3")
    
    if audio3:
        audio_hash = get_audio_hash(audio3)
        
        if st.session_state.part3_recording is None or \
           st.session_state.part3_recording.get("audio_hash") != audio_hash:
            
            with st.spinner("🔄 Transcribing and analyzing your response..."):
                result, error = transcribe_audio_assemblyai(audio3)
            
            if error:
                st.error(f"⚠️ {error}")
                st.info("💡 **Troubleshooting tips:**\n- Check your internet connection\n- Ensure you spoke clearly\n- Try recording again")
            elif result:
                transcript = result.get("text", "")
                audio_duration = result.get("audio_duration", None)
                
                if transcript and transcript.strip() and transcript != "No speech detected":
                    st.write(f"*📝 Transcript: {transcript}*")
                    
                    # Calculate scores
                    vocabulary = calculate_vocabulary_score(transcript)
                    grammar = calculate_grammar_score(transcript)
                    fluency = calculate_fluency_score(transcript, audio_duration)
                    intonation = calculate_intonation_score(result)
                    
                    # Store results
                    st.session_state.part3_recording = {
                        "audio_hash": audio_hash,
                        "transcript": transcript,
                        "vocabulary": vocabulary,
                        "grammar": grammar,
                        "fluency": fluency,
                        "intonation": intonation,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    st.rerun()
                else:
                    st.warning("⚠️ No clear speech detected. Please try recording again and speak more clearly.")

st.markdown("---")

# Submit button and results
col1, col2, col3 = st.columns([2, 1, 2])

with col2:
    submit_button = st.button(
        "📤 Submit Test & View Results",
        type="primary",
        disabled=st.session_state.submitted,
        use_container_width=True
    )

if submit_button:
    # Validation
    if not name or not institution:
        st.error("⚠️ Please enter your name and institution before submitting.")
    elif not email:
        st.error("⚠️ Please enter your email address to receive your report.")
    elif not validate_email(email):
        st.error("⚠️ Please enter a valid email address.")
    elif not st.session_state.part1_recordings and \
         not st.session_state.part2_recordings and \
         not st.session_state.part3_recording:
        st.error("⚠️ Please complete at least one section before submitting.")
    else:
        st.session_state.submitted = True
        st.success("✅ Test Submitted Successfully!")
        st.balloons()
        
        st.markdown("---")
        st.markdown("# 📊 Your Speaking Proficiency Results")
        st.markdown("---")
        
        # Display Part 1 Results
        if st.session_state.part1_recordings:
            st.subheader("📝 Part 1: Sentence Repetition Results")
            
            for i in range(len(sentences)):
                if f"sentence_{i}" in st.session_state.part1_recordings:
                    rec = st.session_state.part1_recordings[f"sentence_{i}"]
                    
                    with st.container():
                        st.write(f"**Sentence {i+1}:** *{sentences[i]}*")
                        st.write(f"*Your response: {rec['transcript']}*")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            display_star_rating(rec["accuracy"], "Accuracy")
                        with col2:
                            display_star_rating(rec["fluency"], "Fluency")
                        with col3:
                            display_star_rating(rec["intonation"], "Intonation")
                        
                        avg = (rec["accuracy"] + rec["fluency"] + rec["intonation"]) / 3
                        st.metric("Average Score", f"{avg:.1f}/5")
                        st.markdown("---")
        
        # Display Part 2 Results
        if st.session_state.part2_recordings:
            st.subheader("💬 Part 2: Student Question Responses")
            
            for i in range(len(prompts)):
                if f"prompt_{i}" in st.session_state.part2_recordings:
                    rec = st.session_state.part2_recordings[f"prompt_{i}"]
                    
                    with st.container():
                        st.write(f"**Question {i+1}:** *{prompts[i]}*")
                        st.write(f"*Your response: {rec['transcript']}*")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            display_star_rating(rec["vocabulary"], "Vocabulary")
                        with col2:
                            display_star_rating(rec["grammar"], "Grammar")
                        with col3:
                            display_star_rating(rec["fluency"], "Fluency")
                        with col4:
                            display_star_rating(rec["intonation"], "Intonation")
                        
                        avg = (rec["vocabulary"] + rec["grammar"] + rec["fluency"] + rec["intonation"]) / 4
                        st.metric("Average Score", f"{avg:.1f}/5")
                        st.markdown("---")
        
        # Display Part 3 Results
        if st.session_state.part3_recording:
            st.subheader("🗣️ Part 3: Free Explanation")
            rec = st.session_state.part3_recording
            
            with st.container():
                st.write(f"*Your explanation: {rec['transcript']}*")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    display_star_rating(rec["vocabulary"], "Vocabulary")
                with col2:
                    display_star_rating(rec["grammar"], "Grammar")
                with col3:
                    display_star_rating(rec["fluency"], "Fluency")
                with col4:
                    display_star_rating(rec["intonation"], "Intonation")
                
                avg = (rec["vocabulary"] + rec["grammar"] + rec["fluency"] + rec["intonation"]) / 4
                st.metric("Average Score", f"{avg:.1f}/5")
        
        st.markdown("---")
        
        # Calculate overall score
        part1_scores = [
            (rec["accuracy"] + rec["fluency"] + rec["intonation"]) / 3
            for rec in st.session_state.part1_recordings.values()
        ] if st.session_state.part1_recordings else []
        
        part2_scores = [
            (rec["vocabulary"] + rec["grammar"] + rec["fluency"] + rec["intonation"]) / 4
            for rec in st.session_state.part2_recordings.values()
        ] if st.session_state.part2_recordings else []
        
        part3_score = (
            (st.session_state.part3_recording["vocabulary"] + 
             st.session_state.part3_recording["grammar"] + 
             st.session_state.part3_recording["fluency"] + 
             st.session_state.part3_recording["intonation"]) / 4
        ) if st.session_state.part3_recording else 0
        
        total_score = sum(part1_scores) + sum(part2_scores) + part3_score
        max_score = len(part1_scores) * 5 + len(part2_scores) * 5 + (5 if part3_score else 0)
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        # Final Summary Section
        st.markdown("# 🎯 Final Summary")
        
        # Score metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Score", f"{total_score:.1f}/{max_score:.0f}")
        with col2:
            st.metric("📈 Percentage", f"{percentage:.1f}%")
        with col3:
            # Determine proficiency level
            if percentage >= 90:
                proficiency_level = "Expert"
                emoji = "🌟"
            elif percentage >= 75:
                proficiency_level = "Advanced"
                emoji = "🎯"
            elif percentage >= 60:
                proficiency_level = "Intermediate"
                emoji = "📈"
            elif percentage >= 45:
                proficiency_level = "Developing"
                emoji = "🌱"
            else:
                proficiency_level = "Emerging"
                emoji = "🔰"
            
            st.metric("🏆 Level", f"{emoji} {proficiency_level}")
        
        # Visual proficiency bar
        if percentage >= 90:
            color = "#00C851"  # Green
        elif percentage >= 75:
            color = "#33B5E5"  # Blue
        elif percentage >= 60:
            color = "#FFB733"  # Orange
        elif percentage >= 45:
            color = "#FF8800"  # Dark Orange
        else:
            color = "#FF4444"  # Red
        
        st.markdown(f"""
        <div style="background-color: #e0e0e0; border-radius: 10px; padding: 5px; margin: 20px 0;">
            <div style="background-color: {color}; width: {percentage}%; height: 40px; border-radius: 8px; 
                        display: flex; align-items: center; justify-content: center; color: white; 
                        font-weight: bold; font-size: 18px;">
                {percentage:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Component breakdown
        st.markdown("### 📊 Detailed Component Analysis")
        
        # Collect all component scores
        component_scores = {
            "Accuracy": [],
            "Fluency": [],
            "Intonation": [],
            "Vocabulary": [],
            "Grammar": []
        }
        
        # Gather Part 1 scores
        for rec in st.session_state.part1_recordings.values():
            component_scores["Accuracy"].append(rec["accuracy"])
            component_scores["Fluency"].append(rec["fluency"])
            component_scores["Intonation"].append(rec["intonation"])
        
        # Gather Part 2 scores
        for rec in st.session_state.part2_recordings.values():
            component_scores["Vocabulary"].append(rec["vocabulary"])
            component_scores["Grammar"].append(rec["grammar"])
            component_scores["Fluency"].append(rec["fluency"])
            component_scores["Intonation"].append(rec["intonation"])
        
        # Gather Part 3 scores
        if st.session_state.part3_recording:
            rec = st.session_state.part3_recording
            component_scores["Vocabulary"].append(rec["vocabulary"])
            component_scores["Grammar"].append(rec["grammar"])
            component_scores["Fluency"].append(rec["fluency"])
            component_scores["Intonation"].append(rec["intonation"])
        
        # Calculate and display averages
        avg_scores = {}
        for component, scores in component_scores.items():
            if scores:
                avg_scores[component] = sum(scores) / len(scores)
        
        for component, avg in avg_scores.items():
            percentage_comp = (avg / 5) * 100
            
            if avg >= 4.5:
                bar_color = "#00C851"
            elif avg >= 3.5:
                bar_color = "#33B5E5"
            elif avg >= 2.5:
                bar_color = "#FFB733"
            else:
                bar_color = "#FF8800"
            
            st.markdown(f"""
            <div style="margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <strong style="font-size: 16px;">{component}</strong>
                    <strong style="font-size: 16px;">{avg:.1f}/5</strong>
                </div>
                <div style="background-color: #e0e0e0; border-radius: 5px; padding: 2px;">
                    <div style="background-color: {bar_color}; width: {percentage_comp}%; height: 25px; 
                                border-radius: 4px; transition: width 0.3s ease;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Feedback section
        st.markdown("---")
        st.markdown("### 💬 Personalized Feedback & Growth Plan")
        
        # Identify strengths and improvements
        strengths = []
        improvements = []
        
        for component, avg in avg_scores.items():
            if avg >= 4.0:
                strengths.append(component)
            elif avg < 3.0:
                improvements.append(component)
        
        # Encouraging message based on proficiency
        if percentage >= 90:
            st.success("🌟 **Outstanding Performance!** Your speaking proficiency demonstrates excellence across all areas. You're setting a wonderful example for effective classroom communication!")
        elif percentage >= 75:
            st.info("🎯 **Great Work!** You show strong speaking skills with clear communication. Keep refining your techniques to reach expert level!")
        elif percentage >= 60:
            st.info("📈 **Good Progress!** You're building solid speaking foundations. With continued practice, you'll see significant improvement!")
        elif percentage >= 45:
            st.warning("🌱 **Keep Growing!** You're developing important skills. Focus on the improvement areas below to accelerate your progress!")
        else:
            st.warning("🔰 **Building Foundations!** Every expert was once a beginner. Consistent practice in your focus areas will lead to significant improvement!")
        
        # Display strengths
        if strengths:
            st.markdown(f"**✅ Your Strengths:** {', '.join(strengths)}")
            st.write("These areas showcase your natural abilities. Continue to leverage these skills in your teaching!")
        
        # Display improvement areas with specific tips
        if improvements:
            st.markdown(f"**🎯 Priority Focus Areas:** {', '.join(improvements)}")
            st.markdown("**Personalized Development Tips:**")
            
            for area in improvements:
                if area == "Accuracy":
                    st.markdown("""
                    • **Accuracy** 
                      - Listen carefully to the complete sentence before speaking
                      - Practice repeating slowly and clearly rather than rushing
                      - Record yourself and compare with the original
                      - Focus on pronouncing each word distinctly
                    """)
                elif area == "Fluency":
                    st.markdown("""
                    • **Fluency**
                      - Aim for 120-160 words per minute (natural conversational pace)
                      - Reduce filler words ('um', 'uh', 'like') through awareness
                      - Practice speaking on topics for 60 seconds without stopping
                      - Record yourself daily to track improvement
                    """)
                elif area == "Intonation":
                    st.markdown("""
                    • **Intonation**
                      - Vary your pitch for questions (rising) and statements (falling)
                      - Emphasize key words in sentences
                      - Read children's stories aloud with expression to practice
                      - Listen to skilled speakers and mimic their patterns
                    """)
                elif area == "Vocabulary":
                    st.markdown("""
                    • **Vocabulary**
                      - Learn 3-5 new academic/professional words weekly
                      - Use synonyms when explaining familiar concepts
                      - Read educational articles and note useful phrases
                      - Practice using varied vocabulary in daily conversations
                    """)
                elif area == "Grammar":
                    st.markdown("""
                    • **Grammar**
                      - Speak in complete sentences with clear subjects and verbs
                      - Practice organizing your thoughts before speaking
                      - Review basic sentence structure patterns
                      - Listen to your recordings to identify grammar patterns
                    """)
        
        # General practice tips
        st.markdown("---")
        st.markdown("### 🎓 Daily Practice Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📅 Daily Routines (10-15 minutes)**
            - Record 2-minute explanations of simple topics
            - Practice classroom instructions aloud
            - Read educational content aloud
            - Shadow native speakers from videos
            - Review and compare your recordings
            """)
        
        with col2:
            st.markdown("""
            **📚 Weekly Goals**
            - Join a speaking practice group
            - Record a 5-minute lesson segment
            - Practice with a colleague and give feedback
            - Watch teaching videos and analyze speech
            - Set specific improvement targets
            """)
        
        # Additional resources
        with st.expander("📖 Additional Resources & Tips"):
            st.markdown("""
            **Preparation Tips:**
            - Warm up your voice before teaching (humming, scales)
            - Practice pronunciation of new vocabulary
            - Rehearse key instructions you'll give
            - Stay hydrated throughout the day
            
            **Classroom Speaking Tips:**
            - Pause between instructions for clarity
            - Vary your tone to maintain student engagement
            - Speak at a moderate pace - not too fast
            - Use gestures to support your words
            - Check for understanding regularly
            
            **Self-Improvement Tools:**
            - Voice recording apps for daily practice
            - Language learning apps (Elsa Speak, Speechling)
            - Educational podcasts for listening practice
            - Online speaking clubs or practice groups
            - Peer feedback sessions with colleagues
            """)
        
        st.markdown("---")
        
        # Save results to CSV
        try:
            results_data = {
                "Name": name,
                "Institution": institution,
                "Part1_Count": len(part1_scores),
                "Part1_Avg": round(sum(part1_scores) / len(part1_scores), 2) if part1_scores else 0,
                "Part2_Count": len(part2_scores),
                "Part2_Avg": round(sum(part2_scores) / len(part2_scores), 2) if part2_scores else 0,
                "Part3_Score": round(part3_score, 2),
                "Total_Score": round(total_score, 2),
                "Max_Score": round(max_score, 2),
                "Percentage": round(percentage, 2),
                "Proficiency_Level": proficiency_level,
                "Accuracy_Avg": round(avg_scores.get("Accuracy", 0), 2),
                "Fluency_Avg": round(avg_scores.get("Fluency", 0), 2),
                "Intonation_Avg": round(avg_scores.get("Intonation", 0), 2),
                "Vocabulary_Avg": round(avg_scores.get("Vocabulary", 0), 2),
                "Grammar_Avg": round(avg_scores.get("Grammar", 0), 2),
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            df = pd.DataFrame([results_data])
            
            # Save to temp directory or current directory
            try:
                results_path = os.path.join(tempfile.gettempdir(), "speaking_test_results.csv")
            except:
                results_path = "speaking_test_results.csv"
            
            file_exists = os.path.isfile(results_path)
            df.to_csv(results_path, mode="a", header=not file_exists, index=False)
            
            st.success(f"✅ Results saved successfully!")
            
        except Exception as e:
            st.warning(f"⚠️ Could not save results to file: {str(e)}")
        
        # Closing message
        st.markdown("---")
        st.markdown("""
        ### 🎉 Thank you for completing the Speaking Proficiency Test!
        
        **Remember:** Effective communication is a journey, not a destination. Every practice session 
        brings you closer to becoming a more confident and effective educator. Your dedication to 
        improving your speaking skills will directly benefit your students' learning experience.
        
        **Next Steps:**
        1. Review your component scores and focus areas
        2. Implement the personalized tips in your daily practice
        3. Track your progress by retaking the test in 4-6 weeks
        4. Share your goals with a colleague for accountability
        
        Keep practicing, stay confident, and celebrate every improvement! 🌟
        """)
        
        # Send email reports
        st.markdown("---")
        st.markdown("### 📧 Email Reports")
        
        with st.spinner("📤 Preparing and sending email reports..."):
            # Generate teacher report
            teacher_html = generate_html_report(
                name, institution, email, component_scores, avg_scores,
                part1_scores, part2_scores, part3_score, total_score,
                max_score, percentage, proficiency_level, strengths, improvements
            )
            
            # Send to teacher
            teacher_success, teacher_message = send_email_report(email, name, teacher_html)
            
            if teacher_success:
                st.success(f"✅ Report sent successfully to {email}")
            else:
                st.warning(f"⚠️ Could not send report to teacher: {teacher_message}")
                st.info("💡 You can still view your results above. Please contact your administrator if you need the report emailed.")
            
            # Send to head teacher if email provided
            if head_teacher_email and head_teacher_email.strip():
                if validate_email(head_teacher_email):
                    # Generate head teacher report
                    head_teacher_html = generate_head_teacher_report(
                        name, institution, email, component_scores, avg_scores,
                        part1_scores, part2_scores, part3_score, total_score,
                        max_score, percentage, proficiency_level, strengths, improvements
                    )
                    
                    # Send to head teacher
                    head_success, head_message = send_head_teacher_email(
                        head_teacher_email, name, head_teacher_html
                    )
                    
                    if head_success:
                        st.success(f"✅ Administrative report sent to head teacher ({head_teacher_email})")
                    else:
                        st.warning(f"⚠️ Could not send report to head teacher: {head_message}")
                else:
                    st.warning(f"⚠️ Invalid head teacher email address: {head_teacher_email}")

        
        # Option to retake test
        st.markdown("---")
        if st.button("🔄 Retake Test", type="secondary"):
            # Clear all session state
            st.session_state.part1_recordings = {}
            st.session_state.part2_recordings = {}
            st.session_state.part3_recording = None
            st.session_state.submitted = False
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>📧 Questions or feedback? Contact your administrator</p>
    <p style='font-size: 12px;'>Speaking Proficiency Assessment System v2.0</p>
</div>
""", unsafe_allow_html=True)
