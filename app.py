from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static', template_folder='templates')

# 配置
BASE_DIR = os.path.expanduser("/html_files")  # 默认目录
#os.makedirs(BASE_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/list')
def list_files():
    path = request.args.get('path', '')
    full_path = os.path.join(BASE_DIR, path)
    
    # 安全检查
    if not os.path.normpath(full_path).startswith(os.path.normpath(BASE_DIR)):
        return jsonify({"error": "Access denied"}), 403
    
    if not os.path.exists(full_path):
        return jsonify({"error": "Path not found"}), 404
    
    # 如果是文件，返回空列表
    if os.path.isfile(full_path):
        return jsonify({
            "path": path,
            "items": []
        })
    
    # 如果是目录，列出内容
    items = []
    for item in sorted(os.listdir(full_path)):
        item_path = os.path.join(full_path, item)
        is_dir = os.path.isdir(item_path)
        
        # 只显示目录和.html文件
        if is_dir or item.lower().endswith('.html'):
            items.append({
                "name": item,
                "path": os.path.join(path, item),
                "is_dir": is_dir,
                "type": "directory" if is_dir else "file",
                "size": os.path.getsize(item_path) if not is_dir else 0,
                "modified": int(os.path.getmtime(item_path))
            })
    
    return jsonify({
        "path": path,
        "items": items
    })

@app.route('/api/create_group', methods=['POST'])
def create_group():
    data = request.json
    current_path = data.get('path', '')
    group_name = data.get('name', '')
    
    if not group_name:
        return jsonify({"error": "Group name is required"}), 400
    
    # 安全检查
    full_path = os.path.join(BASE_DIR, current_path, group_name)
    if not os.path.normpath(full_path).startswith(os.path.normpath(BASE_DIR)):
        return jsonify({"error": "Access denied"}), 403
    
    try:
        os.makedirs(full_path, exist_ok=False)
        return jsonify({
            "success": True, 
            "path": os.path.join(current_path, group_name)
        })
    except FileExistsError:
        return jsonify({"error": "Directory already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/move_files', methods=['POST'])
def move_files():
    data = request.json
    source_files = data.get('files', [])
    target_dir = data.get('target_dir', '')
    
    results = []
    for file in source_files:
        src = os.path.join(BASE_DIR, file)
        dst = os.path.join(BASE_DIR, target_dir, os.path.basename(file))
        
        # 安全检查
        if not os.path.normpath(src).startswith(os.path.normpath(BASE_DIR)) or \
           not os.path.normpath(dst).startswith(os.path.normpath(BASE_DIR)):
            results.append({"file": file, "success": False, "error": "Access denied"})
            continue
        
        try:
            shutil.move(src, dst)
            results.append({"file": file, "success": True})
        except Exception as e:
            results.append({"file": file, "success": False, "error": str(e)})
    
    return jsonify({"results": results})

@app.route('/api/delete_files', methods=['POST'])
def delete_files():
    data = request.json
    files = data.get('files', [])
    
    results = []
    for file in files:
        path = os.path.join(BASE_DIR, file)
        
        # 安全检查
        if not os.path.normpath(path).startswith(os.path.normpath(BASE_DIR)):
            results.append({"file": file, "success": False, "error": "Access denied"})
            continue
        
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            results.append({"file": file, "success": True})
        except Exception as e:
            results.append({"file": file, "success": False, "error": str(e)})
    
    return jsonify({"results": results})

@app.route('/api/rename', methods=['POST'])
def rename_item():
    data = request.json
    old_path = data.get('old_path', '')
    new_name = data.get('new_name', '')
    
    if not old_path or not new_name:
        return jsonify({"error": "Both old_path and new_name are required"}), 400
    
    # 原始路径安全检查
    full_old_path = os.path.join(BASE_DIR, old_path)
    if not os.path.normpath(full_old_path).startswith(os.path.normpath(BASE_DIR)):
        return jsonify({"error": "Access denied"}), 403
    
    if not os.path.exists(full_old_path):
        return jsonify({"error": "Source path not found"}), 404
    
    # 新路径处理（支持中文）
    parent_dir = os.path.dirname(full_old_path)
    full_new_path = os.path.join(parent_dir, new_name)  # 直接使用原始名称，不进行secure_filename处理
    
    # 新路径安全检查
    if not os.path.normpath(full_new_path).startswith(os.path.normpath(BASE_DIR)):
        return jsonify({"error": "Access denied"}), 403
    
    if os.path.exists(full_new_path):
        return jsonify({"error": "Target name already exists"}), 409
    
    # 检查非法字符
    if any(char in new_name for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']):
        return jsonify({"error": "Name contains invalid characters"}), 400
    
    try:
        os.rename(full_old_path, full_new_path)
        relative_new_path = os.path.join(os.path.dirname(old_path), new_name)
        return jsonify({
            "success": True,
            "new_path": relative_new_path
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/preview')
def preview_file():
    try:
        path = request.args.get('path', '')
        if not path:
            return "Missing path parameter", 400
            
        full_path = os.path.join(BASE_DIR, path)
        
        # 安全检查
        if not os.path.normpath(full_path).startswith(os.path.normpath(BASE_DIR)):
            return "Access denied", 403
        
        if not os.path.exists(full_path):
            return "File not found", 404
        
        if not full_path.lower().endswith('.html'):
            return "Only HTML files can be previewed", 400
        
        # 检查文件大小，防止读取过大文件
        if os.path.getsize(full_path) > 100 * 1024 * 1024:  # 100MB限制
            return "File too large to preview", 413
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 添加基本安全措施
        content = content.replace('<head>', '<head><base href="."><meta http-equiv="Content-Security-Policy" content="default-src \'self\'; script-src \'self\' \'unsafe-inline\'; style-src \'self\' \'unsafe-inline\'; img-src \'self\' data:;">')
        return content
        
    except Exception as e:
        return f"Error previewing file: {str(e)}", 500

@app.before_request
def before_request():
    # 防止目录遍历攻击
    if 'path' in request.args:
        path = request.args['path']
        if '../' in path or path.startswith('/'):
            return jsonify({"error": "Invalid path"}), 400
    
    # 限制请求体大小
    if request.content_length and request.content_length > 10 * 1024 * 1024:  # 10MB
        return jsonify({"error": "Request too large"}), 413

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5001, debug=True)
    app.run(port=5000, debug=True)