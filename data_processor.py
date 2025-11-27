"""
数据处理模块
基于merge_ads_data_v4逻辑实现数据清洗和合并
"""
import pandas as pd
import warnings
import os

# 忽略警告
warnings.filterwarnings('ignore')


def clean_id_column(series):
    """
    ID清洗：转字符串，去小数点，去空格
    
    Args:
        series: pandas Series，包含计划ID数据
        
    Returns:
        清洗后的Series
    """
    def _process(x):
        if pd.isna(x):
            return ""
        if isinstance(x, float):
            return str(int(x))
        return str(x).strip()
    return series.apply(_process)


def normalize_date(series):
    """
    日期清洗和标准化
    
    Args:
        series: pandas Series，包含日期数据
        
    Returns:
        标准化后的日期Series（格式：YYYY-MM-DD）
    """
    return pd.to_datetime(series, errors='coerce').dt.strftime('%Y-%m-%d')


def process_agent_data(kiwi_file_path=None, wabang_file_path=None):
    """
    处理代理商数据 (奇异果/哇棒)
    
    Args:
        kiwi_file_path: 奇异果文件路径
        wabang_file_path: 哇棒文件路径
        
    Returns:
        处理后的代理商数据DataFrame，如果失败返回None
    """
    print("正在处理代理商数据...")
    
    # 字段映射字典
    kiwi_map = {
        '计划名称': '计划名称', '计划ID': '计划id', '计划id': '计划id',
        '日期': '时间', '时间': '时间', '花费': '花费', '消耗': '花费',
        '曝光量': '曝光量', '展示量': '曝光量', '点击量': '点击量', '点击率': '点击率',
        '下载量': '下载量', '点击下载率': '点击下载率', '下载成本': '下载成本', '安装量': '安装量'
    }

    wabang_map = {
        '计划名称': '计划名称', '计划ID': '计划id', '时间': '时间', '花费': '花费',
        '曝光量': '曝光量', '点击量': '点击量', '点击率': '点击率', '下载量': '下载量',
        '点击下载率': '点击下载率', '下载成本': '下载成本', '安装量': '安装量'
    }

    target_columns = ['计划名称', '计划id', '时间', '花费', '曝光量', '点击量', '点击率', 
                     '下载量', '点击下载率', '下载成本', '安装量']
    dfs = []

    # 处理奇异果数据
    if kiwi_file_path and os.path.exists(kiwi_file_path):
        try:
            print(f"-> 正在读取奇异果文件: {os.path.basename(kiwi_file_path)}")
            df = pd.read_excel(kiwi_file_path, sheet_name='计划数据')
            df = df.rename(columns=kiwi_map)
            # 确保所有目标列都存在
            for col in target_columns:
                if col not in df.columns:
                    df[col] = None
            df = df[target_columns]
            df['代理商来源'] = '奇异果'
            dfs.append(df)
            print(f"   成功读取 {len(df)} 行数据")
        except Exception as e:
            print(f"读取奇异果文件失败: {e}")
            return None

    # 处理哇棒数据
    if wabang_file_path and os.path.exists(wabang_file_path):
        try:
            print(f"-> 正在读取哇棒文件: {os.path.basename(wabang_file_path)}")
            df = pd.read_excel(wabang_file_path, sheet_name='总数据源')
            df = df.rename(columns=wabang_map)
            # 确保所有目标列都存在
            for col in target_columns:
                if col not in df.columns:
                    df[col] = None
            df = df[target_columns]
            df['代理商来源'] = '哇棒'
            dfs.append(df)
            print(f"   成功读取 {len(df)} 行数据")
        except Exception as e:
            print(f"读取哇棒文件失败: {e}")
            return None

    if not dfs:
        print("错误：未找到任何代理商数据文件")
        return None

    # 合并数据
    full_df = pd.concat(dfs, ignore_index=True)
    
    # 数据清洗
    full_df['计划id'] = clean_id_column(full_df['计划id'])
    full_df['时间'] = normalize_date(full_df['时间'])

    # 拆分计划名称
    print("正在拆分计划名称...")
    split_cols = ['代理', '资源位', '出价方式', '年龄', '定向', '素材样式', '利益点', '时间_split']
    split_data = full_df['计划名称'].astype(str).str.split('-', n=8, expand=True).iloc[:, :8]
    if split_data.shape[1] < 8:
        for i in range(split_data.shape[1], 8):
            split_data[i] = None
    split_data.columns = split_cols
    full_df = pd.concat([full_df, split_data], axis=1)

    # 规范出价方式大小写
    if '出价方式' in full_df.columns:
        def normalize_bidding(val):
            if pd.isna(val):
                return None
            text = str(val).strip()
            if not text or text.lower() in ['nan', 'none']:
                return None
            return text.upper()
        full_df['出价方式'] = full_df['出价方式'].apply(normalize_bidding)

    # 统一年龄写法
    if '年龄' in full_df.columns:
        age_mapping = {
            '24～54岁': '24-54岁',
            '24至54岁': '24-54岁',
            '24~54岁': '24-54岁',
        }
        full_df['年龄'] = full_df['年龄'].replace(age_mapping)

    # 统一定向写法（全部转为大写）
    if '定向' in full_df.columns:
        def normalize_targeting(val):
            if pd.isna(val):
                return None
            text = str(val).strip()
            if not text or text.lower() in ['nan', 'none']:
                return None
            return text.upper()
        full_df['定向'] = full_df['定向'].apply(normalize_targeting)

    print(f"代理商数据处理完成，共 {len(full_df)} 行数据")
    return full_df


def process_backend_data(backend_file_path):
    """
    处理后端数据 (华为)
    
    Args:
        backend_file_path: 后端文件路径
        
    Returns:
        处理后的后端数据DataFrame，如果失败返回None
    """
    print("正在处理后端数据...")
    
    if not backend_file_path or not os.path.exists(backend_file_path):
        print("错误：未找到后端数据文件")
        return None
    
    try:
        print(f"-> 正在读取后端文件: {os.path.basename(backend_file_path)}")
        df_backend = pd.read_excel(backend_file_path, sheet_name='分计划明细表')
        
        print(f"   后端文件包含列: {list(df_backend.columns)}")
        
        # 字段重命名
        backend_rename = {'event_chnl_dtl': '计划id', 'event_dt': '时间'}
        df_backend = df_backend.rename(columns=backend_rename)
        
        # 数据清洗
        df_backend['计划id'] = clean_id_column(df_backend['计划id'])
        df_backend['时间'] = normalize_date(df_backend['时间'])
        
        print(f"   成功读取 {len(df_backend)} 行后端数据")
        return df_backend
    except Exception as e:
        print(f"读取后端文件失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def merge_data(df_front, df_back):
    """
    合并前后端数据
    
    Args:
        df_front: 前端数据DataFrame
        df_back: 后端数据DataFrame
        
    Returns:
        合并后的DataFrame
    """
    print("正在进行前后端数据匹配...")
    
    if df_back is not None:
        merged_df = pd.merge(df_front, df_back, on=['计划id', '时间'], 
                           how='left', suffixes=('', '_后端'))
    else:
        merged_df = df_front
        print("警告：未提供后端数据，仅使用前端数据")
    
    # 数据清洗
    print("正在清洗最终数据...")
    
    # 处理带 % 的利率列
    rate_columns = ['平均执行利率', '平均对客利率', '点击率', '点击下载率']
    
    for col in merged_df.columns:
        # 如果是利率相关的列
        if col in rate_columns or '率' in str(col):
            # 步骤A: 替换 %
            merged_df[col] = merged_df[col].astype(str).str.replace('%', '', regex=False)
            # 步骤B: 替换 'nan' 字符串为实际的 NaN
            merged_df[col] = merged_df[col].replace({'nan': None, 'None': None, '': None})
            # 步骤C: 强转数字
            merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')

        # 如果是其他数值列
        elif any(x in str(col) for x in ['花费', '曝光', '点击', '下载', '安装', '金额', '人数', '成本']):
            merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')
    
    # 统一指标命名
    if '授信成功人数' in merged_df.columns:
        merged_df['授信人数'] = merged_df['授信成功人数']
    if '支用通过人数' in merged_df.columns:
        merged_df['支用成功人数'] = merged_df['支用通过人数']

    print(f"数据合并完成，共 {len(merged_df)} 行数据")
    return merged_df


def calculate_cost_metrics(df):
    """
    计算成本指标
    
    Args:
        df: 合并后的数据DataFrame
        
    Returns:
        添加了成本指标列的DataFrame
    """
    print("正在计算成本指标...")
    
    def safe_div(numerator, denominator):
        if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
            return None
        return numerator / denominator

    def calc_settlement(row):
        clicks = row.get('点击量')
        if pd.isna(clicks) or clicks == 0:
            return None
        agent_name = row.get('代理') or row.get('代理商来源')
        if not agent_name or pd.isna(agent_name):
            return None
        agent_text = str(agent_name)
        if '奇异果' in agent_text:
            rate = 0.58
        elif '哇棒' in agent_text:
            rate = 0.5
        else:
            return None
        return clicks * rate

    if '曝光量' in df.columns:
        df['结算花费'] = df.apply(calc_settlement, axis=1)

    if '花费' in df.columns:
        if '注册人数' in df.columns:
            df['注册成本'] = df.apply(
                lambda row: safe_div(row.get('花费'), row.get('注册人数')),
                axis=1
            )
        if '进件人数' in df.columns:
            df['进件成本'] = df.apply(
                lambda row: safe_div(row.get('花费'), row.get('进件人数')),
                axis=1
            )
        if '授信成功人数' in df.columns:
            df['授信成本'] = df.apply(
                lambda row: safe_div(row.get('花费'), row.get('授信成功人数')),
                axis=1
            )
        if '支用成功人数' in df.columns:
            df['支用成本'] = df.apply(
                lambda row: safe_div(row.get('花费'), row.get('支用成功人数')),
                axis=1
            )
        if '下载量' in df.columns:
            df['下载成本'] = df.apply(
                lambda row: safe_div(row.get('花费'), row.get('下载量')),
                axis=1
            )
    
    print("成本指标计算完成")
    return df


def process_all_data(kiwi_file_path=None, wabang_file_path=None, backend_file_path=None):
    """
    处理所有数据的入口函数
    
    Args:
        kiwi_file_path: 奇异果文件路径
        wabang_file_path: 哇棒文件路径
        backend_file_path: 后端文件路径
        
    Returns:
        处理后的完整数据DataFrame，如果失败返回None
    """
    try:
        # 处理前端数据
        df_front = process_agent_data(kiwi_file_path, wabang_file_path)
        if df_front is None:
            return None
        
        # 处理后端数据
        df_back = process_backend_data(backend_file_path)
        
        # 合并数据
        merged_df = merge_data(df_front, df_back)
        
        # 计算成本指标
        merged_df = calculate_cost_metrics(merged_df)
        
        return merged_df
    except Exception as e:
        print(f"数据处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None


