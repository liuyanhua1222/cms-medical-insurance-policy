#!/usr/bin/env python3
"""
数据源配置模块
定义各类政策信息来源
"""

# 参考数据源配置（仅供参考，实际搜索不限于此）
# Agent 会通过搜索引擎动态发现所有相关的官方网站
DATA_SOURCES = {
    # 国家级官方网站示例
    'national_examples': [
        '国家医保局 (nhsa.gov.cn)',
        '中国政府网 (gov.cn)',
        '人社部 (mohrss.gov.cn)'
    ],
    
    # 省级政府网站示例
    'provincial_examples': [
        '各省市医保局 (ybj.*.gov.cn)',
        '各省市政府网站 (*.gov.cn)'
    ],
    
    # 官方媒体示例
    'media_examples': [
        '新华网 (xinhuanet.com)',
        '人民网 (people.com.cn)',
        '央视网 (cctv.com)'
    ],
    
    # 搜索策略说明
    'search_strategy': {
        'description': '通过搜索引擎动态发现所有相关官方网站',
        'filters': [
            '优先选择 .gov.cn 域名',
            '识别医保局相关域名',
            '包含官方媒体报道',
            '不限制于预定义白名单'
        ]
    }
}


# 官方域名模式（用于识别官方网站）
OFFICIAL_DOMAIN_PATTERNS = [
    # 政府网站特征
    r'\.gov\.cn$',           # 所有 .gov.cn 域名
    r'\.gov\.cn/',           # 所有 .gov.cn 路径
    
    # 医保局特征
    r'ybj\.',                # 医保局域名
    r'yibao',                # 医保相关
    r'nhsa',                 # 国家医保局
    
    # 官方媒体
    r'xinhuanet\.com',       # 新华网
    r'people\.com\.cn',      # 人民网
    r'cctv\.com',            # 央视网
    r'news\.cn',             # 新华社
]

# 参考数据源（仅供参考，不限制搜索范围）
REFERENCE_SOURCES = {
    'national': {
        '国家医保局': 'https://www.nhsa.gov.cn/',
        '中国政府网': 'https://www.gov.cn/',
        '人社部': 'https://www.mohrss.gov.cn/'
    },
    'provincial_examples': {
        '北京': 'http://ybj.beijing.gov.cn/',
        '上海': 'https://ybj.sh.gov.cn/',
        '广东': 'http://ybj.gd.gov.cn/'
    },
    'media': {
        '新华网': 'http://www.xinhuanet.com/',
        '人民网': 'http://www.people.com.cn/',
        '央视网': 'https://www.cctv.com/'
    }
}


def get_source_type(url):
    """根据URL判断来源类型"""
    if 'nhsa.gov.cn' in url:
        return '国家医保局'
    elif 'mohrss.gov.cn' in url:
        return '人社部'
    elif 'gov.cn' in url and 'ybj' in url:
        return '地方医保局'
    elif 'gov.cn' in url:
        return '政府网站'
    elif any(domain in url for domain in ['xinhuanet.com', 'people.com.cn', 'cctv.com', 'news.cn']):
        return '官方媒体'
    elif '.gov.cn' in url:
        return '政府网站'
    else:
        return '其他来源'


def is_official_url(url):
    """检查是否为官方网站（使用模式匹配，不限制白名单）"""
    import re
    
    # 检查是否匹配任何官方域名模式
    for pattern in OFFICIAL_DOMAIN_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    
    return False


def get_region_from_url(url):
    """从URL中提取地区信息"""
    region_mapping = {
        'beijing': '北京',
        'shanghai': '上海',
        'sh.gov.cn': '上海',
        'guangdong': '广东',
        'gd.gov.cn': '广东',
        'zhejiang': '浙江',
        'zj.gov.cn': '浙江',
        'jiangsu': '江苏',
        'sichuan': '四川',
        'sc.gov.cn': '四川',
        'shandong': '山东',
        'henan': '河南',
        'hubei': '湖北',
        'hunan': '湖南'
    }
    
    for key, region in region_mapping.items():
        if key in url.lower():
            return region
    
    return None


if __name__ == '__main__':
    print("数据源配置:")
    print(f"国家级示例: {len(DATA_SOURCES['national_examples'])} 个")
    print(f"省级示例: {len(DATA_SOURCES['provincial_examples'])} 个")
    print(f"官方媒体示例: {len(DATA_SOURCES['media_examples'])} 个")
    print(f"官方域名模式: {len(OFFICIAL_DOMAIN_PATTERNS)} 个")
    print("\n搜索策略: 动态发现所有相关官方网站，不限于预定义列表")
