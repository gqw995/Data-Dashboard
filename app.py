"""
Flask主程序
提供文件上传、数据处理和数据看板功能
"""
from flask import Flask, render_template, request, jsonify, send_file, session
import os
import json
import tempfile
from werkzeug.utils import secure_filename
from data_processor import process_all_data
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ads_data_analysis_secret_key_2025'  # 用于session管理

# 使用系统临时目录来存储文件，解决PyInstaller打包后的路径问题
temp_base = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = os.path.join(temp_base, 'huawei_dashboard_uploads')
app.config['CACHE_FOLDER'] = os.path.join(temp_base, 'huawei_dashboard_cache')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 限制上传文件大小为50MB

# 确保目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CACHE_FOLDER'], exist_ok=True)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}


def df_to_json_records(df):
    """
    将DataFrame安全转换为JSON记录，自动处理 NaN/NaT
    返回Python对象列表，可直接用于 jsonify
    """
    if df is None:
        return []
    return json.loads(df.to_json(orient='records', force_ascii=False, date_format='iso'))


def parse_multi_value(raw_value):
    """
    将多选参数转换为列表，支持逗号分隔
    """
    if not raw_value:
        return []
    if isinstance(raw_value, list):
        values = raw_value
    else:
        values = [item.strip() for item in str(raw_value).split(',')]
    return [v for v in values if v and v.lower() != 'all']


def pick_column(df, candidates):
    """
    返回第一个存在的列名
    """
    for col in candidates:
        if col in df.columns:
            return col
    return None


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """首页：文件上传页面"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    """处理文件上传和数据合并"""
    try:
        # 检查文件是否上传
        if 'kiwi_file' not in request.files and 'wabang_file' not in request.files:
            return jsonify({'success': False, 'message': '请至少上传一个代理商数据文件'}), 400
        
        if 'backend_file' not in request.files:
            return jsonify({'success': False, 'message': '请上传后端数据文件'}), 400
        
        kiwi_file = request.files.get('kiwi_file')
        wabang_file = request.files.get('wabang_file')
        backend_file = request.files.get('backend_file')
        
        # 保存文件路径
        kiwi_path = None
        wabang_path = None
        backend_path = None
        
        # 处理奇异果文件
        if kiwi_file and kiwi_file.filename and allowed_file(kiwi_file.filename):
            filename = secure_filename(kiwi_file.filename)
            kiwi_path = os.path.join(app.config['UPLOAD_FOLDER'], f"kiwi_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}")
            kiwi_file.save(kiwi_path)
        
        # 处理哇棒文件
        if wabang_file and wabang_file.filename and allowed_file(wabang_file.filename):
            filename = secure_filename(wabang_file.filename)
            wabang_path = os.path.join(app.config['UPLOAD_FOLDER'], f"wabang_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}")
            wabang_file.save(wabang_path)
        
        # 处理后端文件
        if backend_file and backend_file.filename and allowed_file(backend_file.filename):
            filename = secure_filename(backend_file.filename)
            backend_path = os.path.join(app.config['UPLOAD_FOLDER'], f"backend_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}")
            backend_file.save(backend_path)
        
        # 检查是否至少有一个代理商文件
        if not kiwi_path and not wabang_path:
            return jsonify({'success': False, 'message': '请至少上传一个代理商数据文件（奇异果或哇棒）'}), 400
        
        if not backend_path:
            return jsonify({'success': False, 'message': '请上传后端数据文件'}), 400
        
        # 处理数据
        print("开始处理数据...")
        merged_df = process_all_data(
            kiwi_file_path=kiwi_path,
            wabang_file_path=wabang_path,
            backend_file_path=backend_path
        )
        
        if merged_df is None:
            return jsonify({'success': False, 'message': '数据处理失败，请检查文件格式是否正确'}), 500
        
        # 保存处理后的数据到缓存
        cache_file = os.path.join(app.config['CACHE_FOLDER'], f"merged_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx")
        merged_df.to_excel(cache_file, index=False)
        
        # 将数据转换为JSON格式（用于前端展示）
        # 只转换前1000行用于预览，完整数据通过API获取
        df_preview = merged_df.head(1000)
        data_json = df_to_json_records(df_preview)
        
        # 将缓存文件路径保存到session
        session['data_cache_file'] = cache_file
        
        # 清理上传的临时文件
        try:
            if kiwi_path and os.path.exists(kiwi_path):
                os.remove(kiwi_path)
            if wabang_path and os.path.exists(wabang_path):
                os.remove(wabang_path)
            if backend_path and os.path.exists(backend_path):
                os.remove(backend_path)
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': f'数据处理成功！共 {len(merged_df)} 行数据',
            'row_count': len(merged_df),
            'preview_data': data_json[:100],  # 只返回前100行作为预览
            'columns': list(merged_df.columns)
        })
    
    except Exception as e:
        print(f"处理文件时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'处理失败：{str(e)}'}), 500


@app.route('/dashboard')
def dashboard():
    """数据看板页面"""
    return render_template('dashboard.html')


@app.route('/api/data', methods=['GET'])
def get_data():
    """获取完整数据（支持筛选）"""
    try:
        cache_file = session.get('data_cache_file')
        if not cache_file or not os.path.exists(cache_file):
            return jsonify({'success': False, 'message': '数据不存在，请重新上传文件'}), 404
        
        # 读取数据
        df = pd.read_excel(cache_file)
        
        # 获取筛选参数
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        agent = request.args.get('agent')  # 代理商来源
        bidding_method = request.args.get('bidding_method')  # 出价方式
        targeting_multi = parse_multi_value(request.args.get('targeting'))  # 定向多选
        resource = request.args.get('resource')  # 资源位
        material = request.args.get('material')  # 素材样式
        benefit = request.args.get('benefit')  # 利益点
        
        # 应用筛选
        if date_from and '时间' in df.columns:
            df = df[df['时间'] >= date_from]
        if date_to and '时间' in df.columns:
            df = df[df['时间'] <= date_to]
        if agent and agent != 'all' and '代理商来源' in df.columns:
            df = df[df['代理商来源'] == agent]
        if bidding_method and bidding_method != 'all' and '出价方式' in df.columns:
            df = df[df['出价方式'] == bidding_method]
        if targeting_multi and '定向' in df.columns:
            df = df[df['定向'].isin(targeting_multi)]
        if resource and resource != 'all' and '资源位' in df.columns:
            df = df[df['资源位'] == resource]
        if material and material != 'all' and '素材样式' in df.columns:
            df = df[df['素材样式'] == material]
        if benefit and benefit != 'all' and '利益点' in df.columns:
            df = df[df['利益点'] == benefit]
        
        # 转换为JSON
        data_json = df_to_json_records(df)
        
        return jsonify({
            'success': True,
            'data': data_json,
            'row_count': len(df)
        })
    
    except Exception as e:
        print(f"获取数据时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """获取统计数据（用于图表展示）"""
    try:
        cache_file = session.get('data_cache_file')
        if not cache_file or not os.path.exists(cache_file):
            return jsonify({'success': False, 'message': '数据不存在'}), 404
        
        # 读取数据
        df = pd.read_excel(cache_file)
        
        # 获取筛选参数（同get_data）
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        agent = request.args.get('agent')
        bidding_method = request.args.get('bidding_method')
        targeting_multi = parse_multi_value(request.args.get('targeting'))
        resource = request.args.get('resource')
        material = request.args.get('material')
        benefit = request.args.get('benefit')
        
        # 应用筛选
        if date_from:
            df = df[df['时间'] >= date_from]
        if date_to:
            df = df[df['时间'] <= date_to]
        if agent and agent != 'all':
            df = df[df['代理商来源'] == agent]
        if bidding_method and bidding_method != 'all':
            df = df[df['出价方式'] == bidding_method]
        if targeting_multi and '定向' in df.columns:
            df = df[df['定向'].isin(targeting_multi)]
        if resource and resource != 'all':
            df = df[df['资源位'] == resource]
        if material and material != 'all' and '素材样式' in df.columns:
            df = df[df['素材样式'] == material]
        if benefit and benefit != 'all' and '利益点' in df.columns:
            df = df[df['利益点'] == benefit]
        
        def safe_division(num, denom):
            if denom in [0, None]:
                return 0
            if pd.isna(denom) or pd.isna(num):
                return 0
            return float(num) / float(denom) if denom != 0 else 0

        def safe_ratio(num, denom):
            if denom in [0, None] or pd.isna(denom) or pd.isna(num):
                return None
            return float(num) / float(denom) if denom != 0 else None
        
        # 按日期汇总
        agg_dict = {
            '花费': 'sum',
            '曝光量': 'sum',
            '点击量': 'sum',
            '下载量': 'sum',
            '安装量': 'sum',
        }
        optional_fields = [
            '注册人数', '进件人数', '进件成功人数',
            '授信提交人数', '授信成功人数', '授信人数',
            '支用申请人数', '支用成功人数', '支用人数',
            '支用笔数', '支用金额', '结算花费', '授信金额'
        ]
        for field in optional_fields:
            if field in df.columns:
                agg_dict[field] = 'sum'
        
        daily_stats = df.groupby('时间').agg(agg_dict).reset_index() if '时间' in df.columns else pd.DataFrame()
        
        for col in ['注册人数', '进件人数', '进件成功人数',
                    '授信提交人数', '授信成功人数',
                    '支用申请人数', '支用成功人数',
                    '授信金额', '支用金额', '结算花费']:
            if col not in daily_stats.columns:
                daily_stats[col] = 0
        
        # 按代理商汇总
        agent_stats = pd.DataFrame()
        if '代理商来源' in df.columns:
            agent_stats = df.groupby('代理商来源').agg({
                '花费': 'sum',
                '曝光量': 'sum',
                '点击量': 'sum',
                '下载量': 'sum',
                '安装量': 'sum',
            }).reset_index()
        
        # 按出价方式汇总
        bidding_stats = df.groupby('出价方式').agg({
            '花费': 'sum',
            '曝光量': 'sum',
            '点击量': 'sum',
        }).reset_index() if '出价方式' in df.columns else pd.DataFrame()

        # 代理商出价方式占比
        agent_bidding_mix = []
        if {'代理商来源', '出价方式', '花费'}.issubset(df.columns):
            def classify_bidding(val):
                if pd.isna(val):
                    return 'OTHER'
                text = str(val).upper()
                if 'OCPC' in text:
                    return 'OCPC'
                if 'CPC' in text:
                    return 'CPC'
                return 'OTHER'
            mix_df = df[['代理商来源', '出价方式', '花费']].copy()
            mix_df['出价类别'] = mix_df['出价方式'].apply(classify_bidding)
            mix_group = mix_df.groupby(['代理商来源', '出价类别'])['花费'].sum().reset_index()
            mix_group = mix_group.rename(columns={'出价类别': '出价类别'})
            agent_bidding_mix = df_to_json_records(mix_group)

        # 定向/资源位分布
        targeting_spend = []
        if {'定向', '花费'}.issubset(df.columns):
            targeting_df = df.groupby('定向')['花费'].sum().reset_index().sort_values('花费', ascending=False).head(15)
            targeting_spend = df_to_json_records(targeting_df)

        resource_spend = []
        if {'资源位', '花费'}.issubset(df.columns):
            resource_df = df.groupby('资源位')['花费'].sum().reset_index().sort_values('花费', ascending=False).head(15)
            resource_spend = df_to_json_records(resource_df)
        
        # 计算总量
        total_cost = df['花费'].sum() if '花费' in df.columns else 0
        total_register = df['注册人数'].sum() if '注册人数' in df.columns else 0
        total_entry = df['进件人数'].sum() if '进件人数' in df.columns else 0
        total_entry_success = df['进件成功人数'].sum() if '进件成功人数' in df.columns else 0

        credit_submit_col = pick_column(df, ['授信提交人数', '授信提交人数_后端'])
        total_credit_submit = df[credit_submit_col].sum() if credit_submit_col else 0
        credit_success_col = pick_column(df, ['授信成功人数', '授信人数'])
        total_credit_success = df[credit_success_col].sum() if credit_success_col else 0
        credit_amount_col = pick_column(df, ['授信金额', '授信金额_后端'])
        total_credit_amount = df[credit_amount_col].sum() if credit_amount_col else 0

        loan_apply_col = pick_column(df, ['支用申请人数', '支用申请人数_后端'])
        total_loan_apply = df[loan_apply_col].sum() if loan_apply_col else 0
        loan_success_col = pick_column(df, ['支用成功人数', '支用人数'])
        total_loan_success = df[loan_success_col].sum() if loan_success_col else 0
        disburse_people_col = pick_column(df, ['支用人数'])
        total_disburse_people = df[disburse_people_col].sum() if disburse_people_col else total_loan_success
        loan_orders_col = pick_column(df, ['支用笔数'])
        total_loan_orders = df[loan_orders_col].sum() if loan_orders_col else 0
        loan_amount_col = pick_column(df, ['支用金额', '支用金额_后端'])
        total_loan_amount = df[loan_amount_col].sum() if loan_amount_col else 0

        settlement_col = pick_column(df, ['结算花费'])
        total_settlement = df[settlement_col].sum() if settlement_col else 0
        total_downloads = df['下载量'].sum() if '下载量' in df.columns else 0

        exec_rate_col = pick_column(df, ['平均执行利率', '平均执行利率_后端'])
        weighted_exec_sum = 0
        if exec_rate_col and loan_amount_col:
            weighted_exec_sum = (df[exec_rate_col].fillna(0) * df[loan_amount_col].fillna(0)).sum()
        
        avg_credit_amount = safe_division(total_credit_amount, total_credit_success)
        avg_loan_per_order = safe_division(total_loan_amount, total_loan_orders)
        avg_exec_rate = safe_division(weighted_exec_sum, total_loan_amount)

        cost_metrics = {
            '注册成本': safe_division(total_cost, total_register),
            '进件成本': safe_division(total_cost, total_entry),
            '授信成本': safe_division(total_cost, total_credit_success),
            '支用成本': safe_division(total_cost, total_loan_success),
            '下载成本': safe_division(total_cost, total_downloads),
        }

        # 通过率趋势
        rate_trend = []
        if not daily_stats.empty:
            for _, row in daily_stats.iterrows():
                rate_trend.append({
                    '时间': row.get('时间'),
                    '准入通过率': safe_ratio(row.get('进件成功人数', 0), row.get('进件人数', 0)),
                    '授信通过率': safe_ratio(row.get('授信成功人数', 0), row.get('授信提交人数', 0)),
                    '支用通过率': safe_ratio(row.get('支用成功人数', 0), row.get('支用申请人数', 0)),
                })
        
        return jsonify({
            'success': True,
            'daily_stats': df_to_json_records(daily_stats),
            'agent_stats': df_to_json_records(agent_stats),
            'bidding_stats': df_to_json_records(bidding_stats) if not bidding_stats.empty else [],
            'agent_bidding_mix': agent_bidding_mix,
            'targeting_spend': targeting_spend,
            'resource_spend': resource_spend,
            'rate_trend': rate_trend,
            'cost_metrics': cost_metrics,
            'total_spend': float(total_cost),
            'total_settlement': float(total_settlement),
            'total_register': int(total_register),
            'total_entry': int(total_entry),
            'total_entry_success': int(total_entry_success),
            'total_credit': int(total_credit_success),
            'total_credit_submit': int(total_credit_submit),
            'total_loan': int(total_loan_success),
            'total_disburse_people': int(total_disburse_people),
            'total_loan_orders': int(total_loan_orders),
            'total_loan_amount': float(total_loan_amount),
            'total_credit_amount': float(total_credit_amount),
            'avg_credit_amount': float(avg_credit_amount) if avg_credit_amount is not None else 0,
            'avg_loan_per_order': float(avg_loan_per_order) if avg_loan_per_order is not None else 0,
            'avg_exec_rate': float(avg_exec_rate) if avg_exec_rate is not None else 0,
        })
    
    except Exception as e:
        print(f"获取统计数据时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/options', methods=['GET'])
def get_filter_options():
    """获取筛选选项（用于下拉框）"""
    try:
        cache_file = session.get('data_cache_file')
        if not cache_file or not os.path.exists(cache_file):
            return jsonify({'success': False, 'message': '数据不存在'}), 404
        
        df = pd.read_excel(cache_file)
        
        options = {
            'agents': sorted(df['代理商来源'].dropna().unique().tolist()) if '代理商来源' in df.columns else [],
            'bidding_methods': sorted(df['出价方式'].dropna().unique().tolist()) if '出价方式' in df.columns else [],
            'targetings': sorted(df['定向'].dropna().unique().tolist()) if '定向' in df.columns else [],
            'resources': sorted(df['资源位'].dropna().unique().tolist()) if '资源位' in df.columns else [],
            'materials': sorted(df['素材样式'].dropna().unique().tolist()) if '素材样式' in df.columns else [],
            'benefits': sorted(df['利益点'].dropna().unique().tolist()) if '利益点' in df.columns else [],
            'dates': sorted(df['时间'].dropna().unique().tolist()) if '时间' in df.columns else [],
        }
        
        return jsonify({
            'success': True,
            'options': options
        })
    
    except Exception as e:
        print(f"获取筛选选项时发生错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/export', methods=['GET'])
def export_data():
    """导出数据"""
    try:
        cache_file = session.get('data_cache_file')
        if not cache_file or not os.path.exists(cache_file):
            return jsonify({'success': False, 'message': '数据不存在'}), 404
        
        return send_file(cache_file, as_attachment=True, 
                        download_name=f'广告数据_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
    
    except Exception as e:
        print(f"导出数据时发生错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


def find_free_port(start_port=5000):
    """查找可用端口"""
    import socket
    port = start_port
    while port < start_port + 100:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        if result != 0:
            return port
        port += 1
    return None

if __name__ == '__main__':
    port = find_free_port(5000)
    if port != 5000:
        print(f"⚠️  警告: 端口5000被占用，使用端口 {port}")
    
    print("=" * 50)
    print("广告数据分析和看板系统")
    print("=" * 50)
    print("服务启动中...")
    print(f"访问地址: http://localhost:{port}")
    print(f"访问地址: http://127.0.0.1:{port}")
    print("=" * 50)
    # 使用 use_reloader=False 避免 watchdog 版本兼容问题
    app.run(debug=True, host='127.0.0.1', port=port, use_reloader=False)

