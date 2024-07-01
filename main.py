from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
import os
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 必須設置 secret_key 來啟用 flash 訊息

app.config['UPLOAD_FOLDER'] = './uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mkv'}

# 檢查文件名是否具有允許的擴展名
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# 首頁路由
@app.route('/')
def index():
    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
    except Exception as e:
        files = []
        print(f"Error listing files: {e}")
    return render_template('index.html', files=files)

# 文件上傳路由
@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('未選擇文件，請重新上傳', 'error')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('未選擇文件，請重新上傳', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = f"{uuid.uuid4().hex}_{file.filename}"
            try:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('文件上傳成功', 'success')
            except Exception as e:
                print(f"Error saving file: {e}")
                flash('文件上傳失敗，請重試', 'error')
            return redirect(url_for('index'))

        flash('不允許的文件類型', 'error')
        return redirect(request.url)

    flash('方法不允許', 'error')
    return redirect(url_for('index'))

# 文件下載路由
@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print(f"Error downloading file: {e}")
        flash('下載文件時出錯', 'error')
        return redirect(url_for('index'))

# 文件刪除路由
@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash(f'{filename} 刪除成功', 'success')
        return jsonify({'message': f'{filename} 刪除成功'})
    except Exception as e:
        flash(f'刪除 {filename} 時出錯: {str(e)}', 'error')
        return jsonify({'message': f'刪除 {filename} 時出錯: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0')
