import os, time
import subprocess
from datetime import datetime
from collections import defaultdict
import re

def parse_existing_index(index_file="index.html"):
    """解析现有的index.html文件，提取文件名和对应的Time added信息"""
    existing_times = {}
    
    if not os.path.exists(index_file):
        print(f"⚠️  现有的 {index_file} 不存在，将使用文件系统时间")
        return existing_times
    
    print(f"📖 解析现有的 {index_file} 文件...")
    
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 多种解析模式，确保能够正确提取时间信息
        
        # 模式1: 匹配新版本的格式 (折叠式布局)
        # <div class="exp-name">filename</div> ... <span class="exp-time">Added: date</span>
        pattern1 = r'<div class="exp-name">([^<]+)</div>.*?<span class="exp-time">Added:\s*([^<]+)</span>'
        matches1 = re.findall(pattern1, content, re.DOTALL | re.IGNORECASE)
        
        # 模式2: 匹配旧版本的格式
        # <h3>filename</h3> ... <p><strong>Time added:</strong> date</p>
        pattern2 = r'<h3>([^<]+)</h3>.*?<p><strong>Time added:</strong>\s*([^<]+)</p>'
        matches2 = re.findall(pattern2, content, re.DOTALL | re.IGNORECASE)
        
        # 模式3: 匹配其他可能的格式
        # <div class="exp-name">filename</div> ... Added: date
        pattern3 = r'<div[^>]*class="exp-name"[^>]*>([^<]+)</div>.*?Added:\s*([^<\n]+)'
        matches3 = re.findall(pattern3, content, re.DOTALL | re.IGNORECASE)
        
        all_matches = matches1 + matches2 + matches3
        
        print(f"  🔍 找到 {len(matches1)} 个新格式匹配")
        print(f"  🔍 找到 {len(matches2)} 个旧格式匹配") 
        print(f"  🔍 找到 {len(matches3)} 个其他格式匹配")
        
        processed_count = 0
        for filename, time_str in all_matches:
            # 清理文件名和时间字符串
            filename = filename.strip()
            time_str = time_str.strip()
            
            # 跳过已经处理过的文件（避免重复）
            if filename in existing_times:
                continue
                
            try:
                # 解析时间字符串，例如: "Fri Mar 21 12:59:18 2025"
                time_obj = time.strptime(time_str, "%a %b %d %H:%M:%S %Y")
                datetime_obj = datetime(*time_obj[:6])
                existing_times[filename] = datetime_obj
                processed_count += 1
                print(f"  ✅ {filename}: {time_str}")
            except ValueError as e:
                print(f"  ⚠️  无法解析时间 '{time_str}' for {filename}: {e}")
                # 尝试其他时间格式
                try:
                    # 尝试解析 ISO 格式或其他格式
                    datetime_obj = datetime.fromisoformat(time_str.replace('T', ' ').replace('Z', ''))
                    existing_times[filename] = datetime_obj
                    processed_count += 1
                    print(f"  ✅ {filename}: {time_str} (备用格式)")
                except:
                    print(f"  ❌ 完全无法解析时间 '{time_str}' for {filename}")
        
        print(f"📊 成功解析 {processed_count} 个文件的时间信息")
        
        # 如果解析结果很少，提供调试信息
        if processed_count < 10:
            print(f"⚠️  解析结果较少，请检查HTML格式")
            print(f"HTML文件前500字符:")
            print(content[:500])
            print("...")
            print(f"HTML文件后500字符:")
            print(content[-500:])
        
    except Exception as e:
        print(f"❌ 解析现有索引文件时出错: {e}")
    
    return existing_times

def create_visualization_index(experiment_list, output_file="index.html"):
    """创建包含多个可视化链接的索引页面，按日期分组并支持折叠"""
    
def create_visualization_index(experiment_list, output_file="index.html"):
    """创建包含多个可视化链接的索引页面，按日期分组并支持折叠"""
    
    # 首先解析现有的index.html文件获取准确的时间信息
    existing_times = parse_existing_index(output_file)
    
    # 按日期分组实验
    experiments_by_date = defaultdict(list)
    
    print(f"🔍 处理文件时间信息...")
    existing_count = 0
    new_count = 0
    
    for exp in experiment_list:
        filename = exp['name']  # 不带扩展名的文件名
        
        # 检查是否在现有索引中
        if filename in existing_times:
            # 对于已存在的文件，始终使用现有索引中的时间
            date_obj = existing_times[filename]
            source = "现有索引 (保持原始时间)"
            existing_count += 1
        else:
            # 只有新文件才使用文件系统时间
            try:
                # 使用文件修改时间作为新文件的创建时间
                mtime = os.path.getmtime(exp['file'])
                ctime = os.path.getctime(exp['file'])
                timestamp = min(mtime, ctime)
                date_obj = datetime.fromtimestamp(timestamp)
                source = "新文件 (文件系统时间)"
                new_count += 1
            except Exception as e:
                print(f"  ❌ 无法获取新文件 {filename} 的时间信息: {e}")
                # 备选方案：使用当前时间
                date_obj = datetime.now()
                source = "新文件 (当前时间 - fallback)"
                new_count += 1
        
        date_key = date_obj.strftime('%Y-%m-%d')  # YYYY-MM-DD format
        
        # 添加详细时间信息到实验数据
        exp['datetime'] = date_obj
        exp['date_key'] = date_key
        exp['time_display'] = date_obj.strftime('%H:%M:%S')
        exp['date_display'] = date_obj.strftime('%Y-%m-%d %H:%M:%S')
        exp['original_date_str'] = date_obj.strftime('%a %b %d %H:%M:%S %Y')  # 保持原格式
        
        print(f"  📅 {filename[:45]:<45} -> {exp['date_display']} ({source})")
        
        experiments_by_date[date_key].append(exp)
    
    print(f"\n📊 文件处理统计:")
    print(f"  ✅ 现有文件 (保持原始时间): {existing_count}")
    print(f"  🆕 新增文件 (使用系统时间): {new_count}")
    print(f"  📋 总计: {len(experiment_list)} 个文件")
    
    # 对每个日期下的实验按时间排序（最新的在前）
    for date_key in experiments_by_date:
        experiments_by_date[date_key].sort(key=lambda x: x['datetime'], reverse=True)
    
    # 获取排序后的日期列表（最新的在前）
    sorted_dates = sorted(experiments_by_date.keys(), reverse=True)
    
    print(f"📊 日期分布统计:")
    for date_key in sorted_dates:
        count = len(experiments_by_date[date_key])
        print(f"  📅 {date_key}: {count} 个实验")
    
    print(f"📈 总计: {len(experiment_list)} 个实验分布在 {len(sorted_dates)} 天")
    
    # 创建HTML内容
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Group Dance 3D Plot - Experiment Records</title>
        <meta charset="UTF-8">
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 20px; 
                background-color: #f5f5f5;
                line-height: 1.6;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{ 
                color: #2c3e50; 
                text-align: center;
                margin-bottom: 10px;
                font-size: 2.5em;
            }}
            .subtitle {{
                text-align: center;
                color: #7f8c8d;
                font-size: 1.2em;
                margin-bottom: 30px;
            }}
            .date-toggle {{
                margin: 15px 0;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }}
            .date-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 20px;
                cursor: pointer;
                font-weight: 600;
                font-size: 1.1em;
                transition: all 0.3s ease;
                user-select: none;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .date-header:hover {{
                background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
            }}
            .toggle-icon {{
                transition: transform 0.3s ease;
                font-size: 1.2em;
            }}
            .date-content {{
                display: none;
                background: #fafafa;
                border-top: 1px solid #e0e0e0;
            }}
            .date-content.active {{
                display: block;
            }}
            .exp-item {{ 
                margin: 0;
                padding: 15px 20px; 
                border-bottom: 1px solid #eeeeee;
                background: white;
                transition: background-color 0.2s ease;
            }}
            .exp-item:last-child {{
                border-bottom: none;
            }}
            .exp-item:hover {{
                background-color: #f8f9ff;
            }}
            .exp-name {{ 
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 8px;
                font-size: 1.05em;
            }}
            .exp-details {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 10px;
            }}
            .exp-time {{
                color: #7f8c8d;
                font-size: 0.9em;
            }}
            .exp-link {{
                display: inline-block;
                padding: 8px 16px;
                background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-size: 0.9em;
                transition: all 0.3s ease;
                font-weight: 500;
            }}
            .exp-link:hover {{
                background: linear-gradient(135deg, #0984e3 0%, #74b9ff 100%);
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(116, 185, 255, 0.3);
            }}
            .stats {{
                background: #ecf0f1;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                text-align: center;
                color: #2c3e50;
            }}
            .stats strong {{
                color: #e74c3c;
                font-size: 1.2em;
            }}
            @media (max-width: 768px) {{
                .container {{ margin: 10px; padding: 15px; }}
                h1 {{ font-size: 2em; }}
                .exp-details {{ flex-direction: column; align-items: flex-start; }}
                .date-header {{ padding: 12px 15px; }}
                .exp-item {{ padding: 12px 15px; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Group Dance 3D Plot</h1>
            <p class="subtitle">Experiment Records</p>
            
            <div class="stats">
                <strong>{total_experiments}</strong> experiments across <strong>{total_dates}</strong> days
            </div>
    """
    
    html_content = html_template.format(
        total_experiments=len(experiment_list),
        total_dates=len(sorted_dates)
    )
    
    # 为每个日期创建一个折叠区域
    for i, date_key in enumerate(sorted_dates):
        experiments = experiments_by_date[date_key]
        date_obj = datetime.strptime(date_key, '%Y-%m-%d')
        date_display = date_obj.strftime('%B %d, %Y')  # e.g., "May 29, 2025"
        weekday = date_obj.strftime('%A')  # e.g., "Thursday"
        
        # 第一个日期默认展开
        is_first = i == 0
        content_class = "date-content active" if is_first else "date-content"
        icon_rotation = "rotate(90deg)" if is_first else "rotate(0deg)"
        
        html_content += f"""
            <div class="date-toggle">
                <div class="date-header" onclick="toggleDate(this)">
                    <span>{weekday}, {date_display} ({len(experiments)} experiments)</span>
                    <span class="toggle-icon" style="transform: {icon_rotation};">▶</span>
                </div>
                <div class="{content_class}">
        """
        
        # 添加该日期下的所有实验
        for exp in experiments:
            html_content += f"""
                    <div class="exp-item">
                        <div class="exp-name">{exp['name']}</div>
                        <div class="exp-details">
                            <span class="exp-time">Added: {exp['original_date_str']}</span>
                            <a href="{exp['file']}" target="_blank" class="exp-link">
                                🎮 Interact with 3D plot
                            </a>
                        </div>
                    </div>
            """
        
        html_content += """
                </div>
            </div>
        """
    
    html_content += """
        </div>

        <script>
            function toggleDate(header) {
                const content = header.nextElementSibling;
                const icon = header.querySelector('.toggle-icon');
                
                if (content.classList.contains('active')) {
                    content.classList.remove('active');
                    icon.style.transform = 'rotate(0deg)';
                } else {
                    content.classList.add('active');
                    icon.style.transform = 'rotate(90deg)';
                }
            }

            // Add keyboard support
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    // Close all toggles
                    document.querySelectorAll('.date-content.active').forEach(content => {
                        content.classList.remove('active');
                        const icon = content.previousElementSibling.querySelector('.toggle-icon');
                        icon.style.transform = 'rotate(0deg)';
                    });
                }
            });

            // Auto-scroll to top on page load
            window.addEventListener('load', function() {
                window.scrollTo(0, 0);
            });
        </script>
    </body>
    </html>
    """
    
    with open(output_file, "w", encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Updated the index.html: {output_file}")
    print(f"📊 Total: {len(experiment_list)} experiments across {len(sorted_dates)} days")
    return output_file

def push_to_github(repo_dir, message="更新可视化索引页面"):
    """将更改推送到GitHub仓库"""
    try:
        # 切换到仓库目录
        os.chdir(repo_dir)
        
        # 添加所有更改
        subprocess.run(["git", "add", "."], check=True)
        
        # 提交更改
        subprocess.run(["git", "commit", "-m", message], check=True)
        
        # 推送到GitHub
        subprocess.run(["git", "push"], check=True)
        
        print("✅ 已成功推送更改到GitHub")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 推送到GitHub时出错: {e}")
        return False

def main():
    root = 'results'
    experiments = []

    if not os.path.exists(root):
        print(f"❌ 目录 '{root}' 不存在")
        return

    print(f"🔍 扫描目录: {root}")
    
    for file in os.listdir(root):
        if file.endswith('.html'):
            meta = {}
            meta['name'] = file.split('.')[0]  # 文件名（不含扩展名）
            meta['file'] = os.path.join(root, file)
            
            if os.path.exists(meta['file']):
                experiments.append(meta)
                print(f"  📄 发现: {file}")
    
    if not experiments:
        print("❌ 在results目录中没有找到HTML文件")
        return
    
    print(f"\n📝 生成改进的索引页面...")
    create_visualization_index(experiments, "index.html")
    
    print(f"\n🚀 推送到GitHub...")
    push_to_github('./', message="更新可视化索引页面 - 保持现有文件原始时间戳")

if __name__ == "__main__":
    main()