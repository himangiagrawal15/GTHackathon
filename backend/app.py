from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json
from report_generator import ReportGenerator
from data_processor import DataProcessor
import traceback

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and initial data validation"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Only CSV files are supported'}), 400
        
        # Save the file
        filename = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Load and validate data
        df = pd.read_csv(filepath)
        
        # Get data summary
        processor = DataProcessor(df)
        summary = processor.get_data_summary()
        
        return jsonify({
            'success': True,
            'filename': filename,
            'summary': summary,
            'message': 'File uploaded successfully'
        })
    
    except Exception as e:
        print(f"Error in upload: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    """Analyze data and return insights"""
    try:
        data = request.json
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Load data
        df = pd.read_csv(filepath)
        processor = DataProcessor(df)
        
        # Get analysis
        analysis = processor.get_full_analysis()
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    
    except Exception as e:
        print(f"Error in analyze: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Generate PDF report for selected campaigns"""
    try:
        data = request.json
        filename = data.get('filename')
        selected_campaigns = data.get('campaigns', [])
        report_type = data.get('report_type', 'comprehensive')  # comprehensive, campaign, platform
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Load data
        df = pd.read_csv(filepath)
        
        # Filter campaigns if specified
        if selected_campaigns:
            df = df[df['campaign_item_id'].isin(selected_campaigns)]
        
        # Generate report
        generator = ReportGenerator(df, app.config['OUTPUT_FOLDER'])
        report_path = generator.generate_comprehensive_report(report_type)
        
        return jsonify({
            'success': True,
            'report_path': os.path.basename(report_path),
            'message': 'Report generated successfully'
        })
    
    except Exception as e:
        print(f"Error in generate_report: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_report(filename):
    """Download generated report"""
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Report not found'}), 404
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        print(f"Error in download: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaigns', methods=['POST'])
def get_campaigns():
    """Get list of campaigns from uploaded file"""
    try:
        data = request.json
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        df = pd.read_csv(filepath)
        processor = DataProcessor(df)
        campaigns = processor.get_campaign_list()
        
        return jsonify({
            'success': True,
            'campaigns': campaigns
        })
    
    except Exception as e:
        print(f"Error in get_campaigns: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)