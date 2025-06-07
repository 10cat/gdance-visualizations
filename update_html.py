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
        
        # 模式1: 匹配新版本的格式 (折叠式布局) - 包含 Added: 和 Updated:
        # <div class="exp-name">filename</div> ... <span class="exp-time">Added: date</span>
        # <div class="exp-name">filename</div> ... <span class="exp-time">🔄 Updated: date</span>
        pattern1 = r'<div class="exp-name">([^<]+)</div>.*?<span class="exp-time[^"]*">(?:🔄 Updated:|Added:)\s*([^<]+)</span>'
        matches1 = re.findall(pattern1, content, re.DOTALL | re.IGNORECASE)
        
        # 模式2: 更宽松的匹配，处理可能的emoji和特殊字符
        # 匹配任何形式的时间前缀
        pattern2 = r'<div class="exp-name">([^<]+)</div>.*?<span[^>]*class="exp-time[^"]*"[^>]*>(?:[^:]*:)?\s*([A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\d{4})</span>'
        matches2 = re.findall(pattern2, content, re.DOTALL | re.IGNORECASE)
        
        # 模式3: 匹配旧版本的格式
        # <h3>filename</h3> ... <p><strong>Time added:</strong> date</p>
        pattern3 = r'<h3>([^<]+)</h3>.*?<p><strong>Time added:</strong>\s*([^<]+)</p>'
        matches3 = re.findall(pattern3, content, re.DOTALL | re.IGNORECASE)
        
        # 模式4: 更通用的时间匹配，直接查找标准时间格式
        # 在exp-name附近查找标准时间格式
        pattern4 = r'<div class="exp-name">([^<]+)</div>.*?([A-Z][a-z]{2}\s+[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\d{4})'
        matches4 = re.findall(pattern4, content, re.DOTALL | re.IGNORECASE)
        
        all_matches = matches1 + matches2 + matches3 + matches4
        
        print(f"  🔍 找到 {len(matches1)} 个新格式匹配 (Added/Updated)")
        print(f"  🔍 找到 {len(matches2)} 个宽松格式匹配")
        print(f"  🔍 找到 {len(matches3)} 个旧格式匹配") 
        print(f"  🔍 找到 {len(matches4)} 个通用时间匹配")
        
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
            # 查找所有exp-name和exp-time的样例
            exp_name_samples = re.findall(r'<div class="exp-name">([^<]+)</div>', content)[:5]
            exp_time_samples = re.findall(r'<span[^>]*class="exp-time[^"]*"[^>]*>([^<]+)</span>', content)[:5]
            
            print(f"实验名称样例: {exp_name_samples}")
            print(f"时间信息样例: {exp_time_samples}")
        
    except Exception as e:
        print(f"❌ 解析现有索引文件时出错: {e}")
    
    return existing_times

def create_visualization_index(experiment_list, output_file="index.html"):
    """创建包含多个可视化链接的索引页面，按日期分组并支持折叠"""
    
def create_visualization_index(experiment_list, output_file="index.html"):
    """创建包含多个可视化链接的索引页面，按日期分组并支持折叠"""
    
    # 首先解析现有的index.html文件获取准确的时间信息
    existing_times = parse_existing_index(output_file)
    
    # 获取今天的日期
    today = datetime.now().date()
    
    # 按日期分组实验
    experiments_by_date = defaultdict(list)
    
    print(f"🔍 处理文件时间信息...")
    existing_count = 0
    new_count = 0
    updated_today_count = 0
    
    for exp in experiment_list:
        filename = exp['name']  # 不带扩展名的文件名
        
        # 获取文件的系统时间信息
        try:
            mtime = os.path.getmtime(exp['file'])  # 文件修改时间
            ctime = os.path.getctime(exp['file'])  # 文件创建时间
            atime = os.path.getatime(exp['file'])  # 文件访问时间
            
            system_datetime = datetime.fromtimestamp(mtime)
            system_date = system_datetime.date()
            
            # 详细调试信息：显示所有时间戳
            print(f"    📁 {filename}:")
            print(f"      🕐 修改时间 (mtime) = {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"      🕑 创建时间 (ctime) = {datetime.fromtimestamp(ctime).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"      🕒 访问时间 (atime) = {datetime.fromtimestamp(atime).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"      📅 使用修改时间作为判断基准")
            
        except Exception as e:
            print(f"  ❌ 无法获取 {filename} 的系统时间: {e}")
            system_datetime = datetime.now()
            system_date = today
        
        # 决定使用哪个时间
        if filename in existing_times:
            original_datetime = existing_times[filename]
            
            print(f"      📋 原始记录时间 = {original_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"      🌅 今天日期 = {today}")
            print(f"      📊 文件修改日期 = {system_date}")
            
            # 时间比较
            time_diff_seconds = (system_datetime - original_datetime).total_seconds()
            print(f"      ⏰ 时间差 = {time_diff_seconds:.1f} 秒 ({system_datetime.strftime('%H:%M:%S')} vs {original_datetime.strftime('%H:%M:%S')})")
            
            # 设置最小更新阈值（1秒），避免微小时间差的误判
            MIN_UPDATE_THRESHOLD_SECONDS = 1.0
            
            # 检查文件是否在今天被修改过，且修改时间明显大于原始记录时间
            if system_date == today and time_diff_seconds > MIN_UPDATE_THRESHOLD_SECONDS:
                # 文件在今天被修改过，且时间明显更新：使用今天的修改时间
                date_obj = system_datetime
                time_diff = system_datetime - original_datetime
                source = f"今天修改 (修改时间: {system_datetime.strftime('%H:%M:%S')}, 比原始时间晚 {time_diff})"
                updated_today_count += 1
                print(f"  🔄 {filename[:45]:<45} -> {date_obj.strftime('%Y-%m-%d %H:%M:%S')} ({source})")
            elif system_date == today and 0 < time_diff_seconds <= MIN_UPDATE_THRESHOLD_SECONDS:
                # 文件是今天修改的，但时间差太小，认为是微小差异，不更新
                date_obj = original_datetime
                source = f"今天修改但时间差太小 ({time_diff_seconds:.1f}秒 ≤ {MIN_UPDATE_THRESHOLD_SECONDS}秒阈值)"
                existing_count += 1
                print(f"  ⏭️  {filename[:45]:<45} -> {date_obj.strftime('%Y-%m-%d %H:%M:%S')} ({source})")
            elif system_date == today and time_diff_seconds <= 0:
                # 文件虽然是今天修改的，但时间没有比原始记录更新
                date_obj = original_datetime
                source = f"今天修改但时间未更新 (修改:{system_datetime.strftime('%H:%M:%S')} <= 原始:{original_datetime.strftime('%H:%M:%S')})"
                existing_count += 1
                print(f"  ⏭️  {filename[:45]:<45} -> {date_obj.strftime('%Y-%m-%d %H:%M:%S')} ({source})")
                print(f"      ⚠️  可能原因: 1)时钟不准确 2)文件时间戳没有正确更新 3)原始记录时间有误")
            else:
                # 文件不是今天修改的：保持原有记录时间
                date_obj = original_datetime
                days_diff = (today - system_date).days
                source = f"保持原始记录时间 (文件最后修改: {days_diff}天前)"
                existing_count += 1
                print(f"  📅 {filename[:45]:<45} -> {date_obj.strftime('%Y-%m-%d %H:%M:%S')} ({source})")
        else:
            # 新文件：使用文件的修改时间
            date_obj = system_datetime
            source = "新文件 (文件修改时间)"
            new_count += 1
            print(f"  🆕 {filename[:45]:<45} -> {date_obj.strftime('%Y-%m-%d %H:%M:%S')} ({source})")
        
        print(f"      ✅ 最终使用时间: {date_obj.strftime('%Y-%m-%d %H:%M:%S')}")
        print()  # 空行分隔
    
    print(f"\n📊 文件处理统计:")
    print(f"  ✅ 现有文件 (保持原始时间): {existing_count}")
    print(f"  🔄 今天更新的文件 (刷新时间): {updated_today_count}")
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
            .exp-time.updated-today {{
                color: #e74c3c;
                font-weight: 600;
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
            # 为今天更新的文件添加特殊标识
            time_class = "exp-time"
            # if exp.get('is_updated_today', False):
            #     time_class += " updated-today"
            #     time_prefix = "🔄 Updated: "
            # else:
            time_prefix = "Added: "
            
            html_content += f"""
                    <div class="exp-item">
                        <div class="exp-name">{exp['name']}</div>
                        <div class="exp-details">
                            <span class="{time_class}">{time_prefix}{exp['original_date_str']}</span>
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
    
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"\n📝 生成改进的索引页面 (今天: {today})...")
    create_visualization_index(experiments, "index.html")
    
    print(f"\n🚀 推送到GitHub...")
    push_to_github('./', message=f"更新可视化索引页面 - 刷新今天更新的文件时间戳 ({today})")

if __name__ == "__main__":
    main()