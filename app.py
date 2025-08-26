# app.py - Production-Ready QR Scanner Flask App
import os
from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime

app = Flask(__name__)

# Simple in-memory storage for scan history
scan_history = []

@app.route('/')
def index():
    return render_template('qr_scanner.html')

@app.route('/api/save_scan', methods=['POST'])
def save_scan():
    """Save scan result to history"""
    try:
        data = request.get_json()
        scan_data = {
            'content': data.get('content', ''),
            'type': data.get('type', 'unknown'),
            'timestamp': datetime.now().isoformat()
        }
        
        scan_history.insert(0, scan_data)
        
        # Keep only last 100 scans
        if len(scan_history) > 100:
            scan_history.pop()
            
        return jsonify({'success': True, 'message': 'Scan saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def get_history():
    """Get scan history"""
    return jsonify({
        'history': scan_history[:50],  # Return last 50 scans
        'total': len(scan_history)
    })

@app.route('/api/history/clear', methods=['DELETE'])
def clear_history():
    """Clear scan history"""
    global scan_history
    scan_history.clear()
    return jsonify({'success': True, 'message': 'History cleared'})

@app.route('/api/export_history')
def export_history():
    """Export history as JSON"""
    return jsonify({
        'export_data': scan_history,
        'export_time': datetime.now().isoformat(),
        'total_scans': len(scan_history)
    })

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Create templates directory and HTML file when app starts
def create_template():
    os.makedirs('templates', exist_ok=True)
    
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
    <title>QR Scanner Pro - Live Demo</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qr-scanner/1.4.2/qr-scanner.umd.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        h1 {
            color: white;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
            font-weight: 300;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }

        .subtitle {
            color: rgba(255, 255, 255, 0.8);
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.1em;
        }

        .scanner-container {
            position: relative;
            margin-bottom: 20px;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }

        #video {
            width: 100%;
            height: 300px;
            object-fit: cover;
            background: #000;
        }

        .scanner-overlay {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 200px;
            height: 200px;
            border: 3px solid #00ff88;
            border-radius: 20px;
            box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.3);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { border-color: #00ff88; }
            50% { border-color: #ff6b6b; }
        }

        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            justify-content: center;
            flex-wrap: wrap;
        }

        button {
            background: linear-gradient(45deg, #00ff88, #00cc6a);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3);
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 255, 136, 0.4);
        }

        button:disabled {
            background: #666;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .result-container {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .result-container h3 {
            color: white;
            margin-bottom: 15px;
            font-size: 1.2em;
        }

        .result-text {
            background: rgba(0, 0, 0, 0.2);
            color: white;
            padding: 15px;
            border-radius: 10px;
            word-break: break-all;
            font-family: 'Courier New', monospace;
            border: 1px solid rgba(255, 255, 255, 0.1);
            max-height: 100px;
            overflow-y: auto;
        }

        .history {
            max-height: 300px;
            overflow-y: auto;
            margin-top: 20px;
        }

        .history-item {
            background: rgba(255, 255, 255, 0.05);
            margin: 10px 0;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #00ff88;
            text-align: left;
        }

        .history-item .timestamp {
            color: #ccc;
            font-size: 12px;
            margin-bottom: 8px;
        }

        .history-item .content {
            color: white;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            word-break: break-all;
        }

        .history-item .type {
            display: inline-block;
            background: #00ff88;
            color: black;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: bold;
            margin-bottom: 8px;
        }

        .status {
            color: white;
            text-align: center;
            margin: 15px 0;
            font-weight: 500;
            padding: 10px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
        }

        .error {
            background: rgba(255, 107, 107, 0.2);
            color: #ff6b6b;
        }

        .success {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
        }

        .stats {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            color: white;
        }

        .stat {
            text-align: center;
        }

        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #00ff88;
        }

        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 255, 136, 0.9);
            color: black;
            padding: 15px 20px;
            border-radius: 10px;
            font-weight: bold;
            transform: translateX(400px);
            transition: transform 0.3s ease;
            z-index: 1000;
        }

        .notification.show {
            transform: translateX(0);
        }

        .footer {
            text-align: center;
            color: rgba(255, 255, 255, 0.7);
            margin-top: 30px;
            padding: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .demo-badge {
            display: inline-block;
            background: rgba(255, 215, 0, 0.2);
            color: #ffd700;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 215, 0, 0.3);
        }

        @media (max-width: 600px) {
            .container {
                padding: 20px;
                margin: 10px;
            }
            
            h1 {
                font-size: 2em;
            }
            
            #video {
                height: 250px;
            }
            
            .controls button {
                padding: 10px 15px;
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="demo-badge">🚀 LIVE DEMO</div>
        <h1>🔍 QR Scanner Pro</h1>
        <div class="subtitle">Real-time QR code scanning with Flask backend</div>
        
        <div class="scanner-container">
            <video id="video"></video>
            <div class="scanner-overlay"></div>
        </div>

        <div class="controls">
            <button id="startBtn">🎥 Start Scanner</button>
            <button id="stopBtn" disabled>⏹️ Stop Scanner</button>
            <button id="copyBtn" disabled>📋 Copy Result</button>
            <button id="refreshHistory">🔄 Refresh History</button>
            <button id="clearHistory">🗑️ Clear History</button>
            <button id="exportData">📥 Export Data</button>
        </div>

        <div id="status" class="status">Ready to scan QR codes</div>

        <div id="result" class="result-container" style="display: none;">
            <h3>Latest Scan:</h3>
            <div id="resultText" class="result-text"></div>
        </div>

        <div class="stats">
            <div class="stat">
                <div id="scanCount" class="stat-number">0</div>
                <div>Total Scans</div>
            </div>
            <div class="stat">
                <div id="sessionScans" class="stat-number">0</div>
                <div>This Session</div>
            </div>
        </div>

        <div class="result-container">
            <h3>📜 Scan History</h3>
            <div id="history" class="history">
                <div style="color: #ccc; text-align: center; padding: 20px;">
                    No scans yet. Start scanning to see history here!
                </div>
            </div>
        </div>

        <div class="footer">
            <p>🎓 <strong>QR Scanner Pro</strong> - Built with Flask & JavaScript</p>
            <p>✨ Features: Real-time scanning, History tracking, Export functionality</p>
        </div>
    </div>

    <div id="notification" class="notification"></div>

    <script>
        let qrScanner = null;
        let sessionScans = 0;
        let currentResult = '';

        const video = document.getElementById('video');
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const copyBtn = document.getElementById('copyBtn');
        const refreshHistoryBtn = document.getElementById('refreshHistory');
        const clearHistoryBtn = document.getElementById('clearHistory');
        const exportDataBtn = document.getElementById('exportData');
        const status = document.getElementById('status');
        const result = document.getElementById('result');
        const resultText = document.getElementById('resultText');
        const history = document.getElementById('history');
        const scanCount = document.getElementById('scanCount');
        const sessionScansEl = document.getElementById('sessionScans');
        const notification = document.getElementById('notification');

        // Initialize QR Scanner
        async function initScanner() {
            try {
                qrScanner = new QrScanner(
                    video,
                    result => handleScanResult(result),
                    {
                        onDecodeError: err => {
                            // Silently handle decode errors
                        },
                        highlightScanRegion: true,
                        highlightCodeOutline: true,
                        maxScansPerSecond: 3,
                    }
                );

                updateStatus('✅ Scanner initialized. Click "Start Scanner" to begin.', 'success');
                loadHistory();
            } catch (err) {
                updateStatus(`❌ Error initializing scanner: ${err.message}`, 'error');
            }
        }

        async function handleScanResult(result) {
            const scanData = {
                content: result.data,
                type: detectContentType(result.data),
                timestamp: new Date().toISOString()
            };

            try {
                const response = await fetch('/api/save_scan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(scanData)
                });

                if (response.ok) {
                    sessionScans++;
                    currentResult = result.data;
                    updateUI(scanData);
                    loadHistory();
                    showNotification('🎉 QR Code scanned and saved!');
                    
                    // Vibrate if supported
                    if ('vibrate' in navigator) {
                        navigator.vibrate(200);
                    }
                }
            } catch (error) {
                console.error('Error saving scan:', error);
                showNotification('⚠️ Scan detected but failed to save', 'error');
            }
        }

        function detectContentType(content) {
            if (content.startsWith('http://') || content.startsWith('https://')) {
                return 'URL';
            } else if (content.startsWith('mailto:')) {
                return 'Email';
            } else if (content.startsWith('tel:')) {
                return 'Phone';
            } else if (content.startsWith('WIFI:')) {
                return 'WiFi';
            } else if (content.includes('@') && content.includes('.')) {
                return 'Email';
            } else {
                return 'Text';
            }
        }

        function updateUI(scanData) {
            resultText.textContent = scanData.content;
            result.style.display = 'block';
            copyBtn.disabled = false;
            
            sessionScansEl.textContent = sessionScans;
            updateStatus('✅ QR Code scanned successfully!', 'success');
        }

        async function loadHistory() {
            try {
                const response = await fetch('/api/history');
                const data = await response.json();
                
                scanCount.textContent = data.total;
                
                if (data.history.length === 0) {
                    history.innerHTML = `
                        <div style="color: #ccc; text-align: center; padding: 20px;">
                            📱 No scans yet. Start scanning to see history here!
                        </div>
                    `;
                    return;
                }
                
                history.innerHTML = data.history.map(item => `
                    <div class="history-item">
                        <div class="type">${item.type}</div>
                        <div class="timestamp">⏰ ${new Date(item.timestamp).toLocaleString()}</div>
                        <div class="content">${escapeHtml(item.content)}</div>
                    </div>
                `).join('');
                
            } catch (error) {
                console.error('Error loading history:', error);
                showNotification('❌ Failed to load history', 'error');
            }
        }

        function updateStatus(message, type = '') {
            status.textContent = message;
            status.className = `status ${type}`;
        }

        function showNotification(message, type = 'success') {
            notification.textContent = message;
            notification.className = `notification ${type}`;
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Event Listeners
        startBtn.addEventListener('click', async () => {
            try {
                await qrScanner.start();
                startBtn.disabled = true;
                stopBtn.disabled = false;
                updateStatus('🎥 Scanner active. Point camera at QR code.', 'success');
            } catch (err) {
                updateStatus(`❌ Error starting scanner: ${err.message}`, 'error');
            }
        });

        stopBtn.addEventListener('click', () => {
            qrScanner.stop();
            startBtn.disabled = false;
            stopBtn.disabled = true;
            updateStatus('⏹️ Scanner stopped.', '');
        });

        copyBtn.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(currentResult);
                showNotification('📋 Copied to clipboard!');
                copyBtn.textContent = '✅ Copied!';
                setTimeout(() => {
                    copyBtn.textContent = '📋 Copy Result';
                }, 2000);
            } catch (err) {
                showNotification('❌ Failed to copy to clipboard', 'error');
            }
        });

        refreshHistoryBtn.addEventListener('click', () => {
            loadHistory();
            showNotification('🔄 History refreshed!');
        });

        clearHistoryBtn.addEventListener('click', async () => {
            if (!confirm('🗑️ Are you sure you want to clear all scan history?')) {
                return;
            }
            
            try {
                const response = await fetch('/api/history/clear', {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    loadHistory();
                    result.style.display = 'none';
                    copyBtn.disabled = true;
                    showNotification('🗑️ History cleared successfully!');
                }
            } catch (error) {
                showNotification('❌ Failed to clear history', 'error');
            }
        });

        exportDataBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/export_history');
                const data = await response.json();
                
                const dataStr = JSON.stringify(data, null, 2);
                const blob = new Blob([dataStr], { type: 'application/json' });
                const url = window.URL.createObjectURL(blob);
                
                const link = document.createElement('a');
                link.href = url;
                link.download = `qr_scan_history_${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
                
                showNotification('📥 Data exported successfully!');
            } catch (error) {
                showNotification('❌ Failed to export data', 'error');
            }
        });

        // Initialize on page load
        window.addEventListener('load', initScanner);

        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && qrScanner) {
                qrScanner.stop();
                startBtn.disabled = false;
                stopBtn.disabled = true;
                updateStatus('⏸️ Scanner paused (tab hidden).', '');
            }
        });
    </script>
</body>
</html>'''
    
    # Write the HTML template
    with open('templates/qr_scanner.html', 'w', encoding='utf-8') as f:
        f.write(html_template)

# Create template when app starts
create_template()

if __name__ == '__main__':
    # Production configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("🚀 QR Scanner Pro is starting...")
    print(f"📱 Access at: http://localhost:{port}")
    print("🌐 Ready for production deployment!")
    
    app.run(debug=debug, host='0.0.0.0', port=port)