from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import os
import json
from werkzeug.utils import secure_filename
import tempfile
import uuid
import mimetypes

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'mp3', 'wav', 'jpg', 'jpeg', 'png', 'gif'}

# 确保文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """提供前端页面"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """<!DOCTYPE html>
<html>
<head>
    <title>视频编辑器</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>视频编辑器后端服务正在运行</h1>
    <p>请确保 index.html 文件存在于当前目录中。</p>
    <p>API 端点:</p>
    <ul>
        <li>POST /api/upload - 上传文件</li>
        <li>POST /api/export - 导出视频</li>
        <li>POST /api/project/save - 保存项目</li>
        <li>GET /api/project/load/&lt;filename&gt; - 加载项目</li>
    </ul>
</body>
</html>"""

@app.route('/style.css')
def serve_css():
    """提供CSS文件"""
    try:
        with open('style.css', 'r', encoding='utf-8') as f:
            response = app.response_class(
                f.read(),
                mimetype='text/css'
            )
            return response
    except FileNotFoundError:
        return "/* CSS file not found */", 404

@app.route('/script.js')
def serve_js():
    """提供JavaScript文件"""
    try:
        with open('script.js', 'r', encoding='utf-8') as f:
            response = app.response_class(
                f.read(),
                mimetype='application/javascript'
            )
            return response
    except FileNotFoundError:
        return "// JavaScript file not found", 404

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传媒体文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 添加唯一标识符避免文件名冲突
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(filepath)
            
            # 获取文件信息
            file_info = get_file_info(filepath)
            file_info['filename'] = unique_filename
            file_info['original_name'] = filename
            
            return jsonify({
                'success': True,
                'file_info': file_info
            })
        else:
            return jsonify({'error': '不支持的文件格式'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_file_info(filepath):
    """获取媒体文件信息"""
    try:
        file_ext = os.path.splitext(filepath)[1].lower()
        file_size = os.path.getsize(filepath)
        
        if file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
            # 视频文件
            return {
                'type': 'video',
                'duration': 10,  # 默认时长，实际应用中需要用ffprobe获取
                'width': 1920,   # 默认分辨率
                'height': 1080,
                'fps': 30,
                'size': file_size
            }
        elif file_ext in ['.mp3', '.wav', '.aac', '.flac']:
            # 音频文件
            return {
                'type': 'audio',
                'duration': 180,  # 默认时长
                'size': file_size
            }
        elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            # 图片文件
            try:
                from PIL import Image
                img = Image.open(filepath)
                return {
                    'type': 'image',
                    'width': img.width,
                    'height': img.height,
                    'duration': 5,  # 默认图片显示5秒
                    'size': file_size
                }
            except ImportError:
                return {
                    'type': 'image',
                    'width': 1920,
                    'height': 1080,
                    'duration': 5,
                    'size': file_size
                }
        else:
            return {'type': 'unknown', 'size': file_size}
            
    except Exception as e:
        print(f"获取文件信息错误: {e}")
        return {'type': 'unknown', 'error': str(e)}

@app.route('/api/export', methods=['POST'])
def export_video():
    """导出视频"""
    try:
        data = request.get_json()
        timeline_data = data.get('timeline', [])
        export_settings = data.get('settings', {})
        
        if not timeline_data:
            return jsonify({'error': '时间轴为空'}), 400
        
        # 创建输出文件名
        output_filename = f"export_{uuid.uuid4()}.mp4"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # 处理时间轴数据并创建视频
        success = process_timeline(timeline_data, output_path, export_settings)
        
        if success:
            return jsonify({
                'success': True,
                'download_url': f'/api/download/{output_filename}'
            })
        else:
            return jsonify({'error': '视频导出失败'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_timeline(timeline_data, output_path, settings):
    """处理时间轴数据并生成视频（模拟功能）"""
    try:
        # 模拟视频处理过程
        import time
        time.sleep(2)  # 模拟处理时间
        
        # 创建一个简单的文本文件作为演示
        with open(output_path.replace('.mp4', '.txt'), 'w', encoding='utf-8') as f:
            f.write("视频导出信息\n")
            f.write(f"导出时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"时间轴剪辑数量: {len(timeline_data)}\n")
            f.write("\n剪辑详情:\n")
            
            for i, clip in enumerate(timeline_data):
                f.write(f"剪辑 {i+1}:\n")
                f.write(f"  名称: {clip.get('name', '未知')}\n")
                f.write(f"  类型: {clip.get('type', '未知')}\n")
                f.write(f"  开始时间: {clip.get('startTime', 0)}秒\n")
                f.write(f"  时长: {clip.get('duration', 0)}秒\n")
                f.write(f"  轨道: {clip.get('trackIndex', 0)}\n\n")
            
            f.write("\n导出设置:\n")
            for key, value in settings.items():
                f.write(f"  {key}: {value}\n")
        
        print(f"模拟导出完成: {output_path}")
        return True
        
    except Exception as e:
        print(f"处理时间轴错误: {e}")
        return False

# create_clip_from_data函数已移除，因为当前版本不使用moviepy

@app.route('/api/download/<filename>')
def download_file(filename):
    """下载导出的视频文件"""
    try:
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preview/<filename>')
def preview_file(filename):
    """预览上传的媒体文件"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath)
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/project/save', methods=['POST'])
def save_project():
    """保存项目"""
    try:
        data = request.get_json()
        project_name = data.get('name', f'project_{uuid.uuid4()}')
        project_data = data.get('data', {})
        
        # 保存项目文件
        project_filename = f"{project_name}.json"
        project_path = os.path.join('projects', project_filename)
        
        os.makedirs('projects', exist_ok=True)
        
        with open(project_path, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'project_file': project_filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/project/load/<filename>')
def load_project(filename):
    """加载项目"""
    try:
        project_path = os.path.join('projects', filename)
        
        if os.path.exists(project_path):
            with open(project_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            return jsonify({
                'success': True,
                'data': project_data
            })
        else:
            return jsonify({'error': '项目文件不存在'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("启动视频编辑器后端服务...")
    print("前端页面: http://localhost:5000")
    print("API文档: http://localhost:5000/api")
    app.run(debug=True, host='0.0.0.0', port=5000)