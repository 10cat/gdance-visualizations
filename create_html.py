def create_visualization_index(experiment_list, output_file="index.html"):
    """创建包含多个可视化链接的索引页面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>群舞可视化实验索引</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .exp-list { list-style-type: none; }
            .exp-item { margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            h1 { color: #333; }
            a { text-decoration: none; color: #0066cc; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>群舞可视化实验索引</h1>
        <ul class="exp-list">
    """
    
    for exp in experiment_list:
        html_content += f"""
        <li class="exp-item">
            <h3>{exp['name']}</h3>
            <p><strong>Time added:</strong> {exp['date']}</p>
            <p><a href="{exp['file']}" target="_blank">Interact with 3D plot</a></p>
        </li>
        """
    
    html_content += """
        </ul>
    </body>
    </html>
    """
    
    with open(output_file, "w") as f:
        f.write(html_content)
    
    print(f"Update the index.html：{output_file}")
    return output_file


# experiments = [
#     {"name": "实验001", "description": "基准模型", "date": "2023-06-15", "file": "experiment_001_visualization.html"},
#     {"name": "实验002", "description": "改进注意力机制", "date": "2023-06-20", "file": "experiment_002_visualization.html"},
# ]

# create_visualization_index(experiments, "results/index.html")

import os, time
root = 'results'

experiments = []

for file in os.listdir(root):
    if file.endswith('.html'):
        meta = {}
        meta['name'] = file.split('.')[0]
        meta['file'] = os.path.join(root, file)
        # read the date-time of the file being added to this folder
        meta['date'] = time.ctime(os.path.getctime(meta['file']))
        experiments.append(meta)
        
create_visualization_index(experiments, "index.html")
        
        
        