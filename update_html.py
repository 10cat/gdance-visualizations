import os, time
import subprocess
from datetime import datetime
from collections import defaultdict

def create_visualization_index(experiment_list, output_file="index.html"):
    """创建包含多个可视化链接的索引页面，按日期分组并支持折叠"""
    
    # 按日期分组实验
    experiments_by_date = defaultdict(list)
    
    for exp in experiment_list:
        # 解析时间戳
        timestamp = os.path.getctime(exp['file'])
        date_obj = datetime.fromtimestamp(timestamp)
        date_key = date_obj.strftime('%Y-%m-%d')  # YYYY-MM-DD format
        
        # 添加详细时间信息到实验数据
        exp['datetime'] = date_obj
        exp['date_key'] = date_key
        exp['time_display'] = date_obj.strftime('%H:%M:%S')
        
        experiments_by_date[date_key].append(exp)
    
    # 对每个日期下的实验按时间排序（最新的在前）
    for date_key in experiments_by_date:
        experiments_by_date[date_key].sort(key=lambda x: x['datetime'], reverse=True)
    
    # 获取排序后的日期列表（最新的在前）
    sorted_dates = sorted(experiments_by_date.keys(), reverse=True)
    
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
                            <span class="exp-time">Added at {exp['time_display']}</span>
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
            meta['name'] = file.split('.')[0]
            meta['file'] = os.path.join(root, file)
            
            # 使用文件的修改时间作为创建时间
            if os.path.exists(meta['file']):
                meta['date'] = time.ctime(os.path.getctime(meta['file']))
                experiments.append(meta)
                print(f"  📄 找到: {file}")
    
    if not experiments:
        print("❌ 在results目录中没有找到HTML文件")
        return
    
    print(f"📝 生成索引页面...")
    create_visualization_index(experiments, "index.html")
    
    # 推送到GitHub
    print(f"🚀 推送到GitHub...")
    push_to_github('./', message="更新可视化索引页面 - 改进日期分组布局")

if __name__ == "__main__":
    main()