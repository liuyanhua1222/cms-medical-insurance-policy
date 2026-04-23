#!/usr/bin/env python3
"""
查询各地异地就医备案政策，获取门诊、住院、报销额度等关键信息

依赖：
- playwright：用于处理动态网站和反爬虫保护
- argparse：用于解析命令行参数
- json：用于输出JSON格式结果
- os：用于处理环境变量

最小调用示例：
python search_policy.py --region 北京
"""

import argparse
import json
import re
import logging
import os
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 导入数据库和数据源模块
from database import init_db, save_policy, query_policies, get_policy_by_url, get_statistics
from data_sources import get_source_type, is_official_url, get_region_from_url

# 配置日志
LOG_DIR = Path('.cms-log')
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'search.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 搜索配置
TIMEOUT = 60000
MAX_RETRIES = 3
RETRY_INTERVAL = 2


def build_search_query(region=None, policy_type=None, keyword=None, time_range=None):
    """构建搜索查询"""
    query_parts = []
    
    if keyword:
        query_parts.append(keyword)
    else:
        query_parts.append("异地就医备案政策")
    
    if region:
        query_parts.append(region)
    
    if policy_type:
        query_parts.append(policy_type)
    
    if time_range:
        if time_range == "近1年":
            query_parts.append("2025 2026")
        elif time_range == "近2年":
            query_parts.append("2024 2025 2026")
    
    return " ".join(query_parts)





def extract_date(text):
    """从文本中提取日期"""
    # 支持多种日期格式
    patterns = [
        r'(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})',  # 2025年1月1日 或 2025-01-01
        r'(\d{4})\.(\d{1,2})\.(\d{1,2})',            # 2025.01.01
        r'发布日期[：:]\s*(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})',
        r'时间[：:]\s*(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                groups = match.groups()
                year = int(groups[0])
                month = int(groups[1])
                day = int(groups[2])
                # 验证日期合法性
                date_obj = datetime(year, month, day)
                return date_obj.strftime('%Y-%m-%d')
            except (ValueError, IndexError):
                continue
    
    return None


def extract_percentage(text, keywords):
    """从文本中提取百分比"""
    for keyword in keywords:
        pattern = rf'{keyword}[^\d]*(\d+(?:\.\d+)?)\s*%'
        match = re.search(pattern, text)
        if match:
            return f"{match.group(1)}%"
    return None


def extract_amount(text, keywords):
    """从文本中提取金额"""
    for keyword in keywords:
        # 匹配金额：支持万元、元等单位
        pattern = rf'{keyword}[^\d]*(\d+(?:\.\d+)?)\s*(万元|元)'
        match = re.search(pattern, text)
        if match:
            amount = float(match.group(1))
            unit = match.group(2)
            if unit == '万元':
                return str(int(amount * 10000))
            return str(int(amount))
    return None


def extract_policy_info_from_content(title, content, url):
    """从页面内容中提取政策信息"""
    # 获取来源类型和地区
    source_type = get_source_type(url)
    region_from_url = get_region_from_url(url)
    
    policy_info = {
        "policy_name": title,
        "release_date": None,
        "region": region_from_url or "",
        "source_type": source_type,
        "outpatient": {
            "available": None,
            "reimbursement_rate": None
        },
        "inpatient": {
            "available": None,
            "reimbursement_rate": None
        },
        "reimbursement_limit": {
            "annual_limit": None,
            "single_limit": None
        },
        "community_health": None,
        "filing_process": {
            "methods": [],
            "materials": [],
            "validity": None,
            "change_process": None
        },
        "special_groups": {
            "retirees": None,
            "workers": None,
            "emergency": None,
            "chronic_patients": None
        },
        "direct_settlement": {
            "scope": None,
            "steps": [],
            "reimbursement_requirements": []
        },
        "drugs_and_treatment": {
            "drug_list": None,
            "treatment_scope": None,
            "consumables_reimbursement": None
        },
        "policy_timeliness": {
            "latest_adjustment": None,
            "cross_regional_differences": None,
            "transition_period": None
        },
        "common_issues": {
            "filing_failure_reasons": [],
            "unfiled_treatment": None,
            "duplicate_insurance": None
        },
        "source": url,
        "notes": "具体以当地最新政策为准"
    }
    
    # 提取发布日期
    policy_info["release_date"] = extract_date(content)
    
    # 提取门诊报销比例
    outpatient_rate = extract_percentage(content, ['门诊.*?报销比例', '门诊.*?支付比例', '普通门诊'])
    if outpatient_rate:
        policy_info["outpatient"]["available"] = True
        policy_info["outpatient"]["reimbursement_rate"] = outpatient_rate
    elif '门诊' in content and ('异地' in content or '直接结算' in content):
        policy_info["outpatient"]["available"] = True
    
    # 提取住院报销比例
    inpatient_rate = extract_percentage(content, ['住院.*?报销比例', '住院.*?支付比例', '住院费用'])
    if inpatient_rate:
        policy_info["inpatient"]["available"] = True
        policy_info["inpatient"]["reimbursement_rate"] = inpatient_rate
    elif '住院' in content and ('异地' in content or '直接结算' in content):
        policy_info["inpatient"]["available"] = True
    
    # 提取报销额度
    annual_limit = extract_amount(content, ['年度.*?限额', '年度.*?最高', '全年.*?限额'])
    if annual_limit:
        policy_info["reimbursement_limit"]["annual_limit"] = annual_limit
    
    single_limit = extract_amount(content, ['单次.*?限额', '每次.*?限额', '单笔.*?限额'])
    if single_limit:
        policy_info["reimbursement_limit"]["single_limit"] = single_limit
    
    # 提取社康使用情况
    if '社区' in content and ('医疗' in content or '卫生' in content):
        policy_info["community_health"] = True
    
    # 提取备案方式
    if '线上' in content or '网上' in content or 'APP' in content or '小程序' in content:
        policy_info["filing_process"]["methods"].append("线上")
    if '线下' in content or '窗口' in content or '现场' in content:
        policy_info["filing_process"]["methods"].append("线下")
    
    # 提取备案材料
    materials_keywords = ['身份证', '医保卡', '社保卡', '居住证', '户口本', '就医证明']
    for material in materials_keywords:
        if material in content:
            policy_info["filing_process"]["materials"].append(material)
    
    # 提取备案有效期
    validity_match = re.search(r'有效期[：:为]\s*(\d+)\s*(年|个月)', content)
    if validity_match:
        policy_info["filing_process"]["validity"] = f"{validity_match.group(1)}{validity_match.group(2)}"
    
    # 提取特殊人群
    if '退休' in content or '离休' in content:
        policy_info["special_groups"]["retirees"] = True
    if '在职' in content or '职工' in content:
        policy_info["special_groups"]["workers"] = True
    if '急诊' in content or '紧急' in content:
        policy_info["special_groups"]["emergency"] = True
    if '慢性病' in content or '慢病' in content:
        policy_info["special_groups"]["chronic_patients"] = True
    
    # 提取直接结算范围
    if '定点' in content and ('医疗机构' in content or '医院' in content):
        policy_info["direct_settlement"]["scope"] = "定点医疗机构"
    
    # 提取结算步骤
    settlement_steps = ['备案', '就医', '结算']
    for step in settlement_steps:
        if step in content:
            policy_info["direct_settlement"]["steps"].append(step)
    
    # 提取报销要求
    requirements = ['发票', '费用明细', '诊断证明', '病历']
    for req in requirements:
        if req in content:
            policy_info["direct_settlement"]["reimbursement_requirements"].append(req)
    
    # 提取药品目录
    if '参保地' in content and '目录' in content:
        policy_info["drugs_and_treatment"]["drug_list"] = "参保地目录"
    elif '就医地' in content and '目录' in content:
        policy_info["drugs_and_treatment"]["drug_list"] = "就医地目录"
    
    # 提取诊疗范围
    if '医保范围' in content or '医保目录' in content:
        policy_info["drugs_and_treatment"]["treatment_scope"] = "医保范围内"
    
    return policy_info


def search_baidu_with_playwright(query, max_results=5):
    """使用Playwright搜索百度"""
    url = f"https://www.baidu.com/s?wd={query}&ie=utf-8"
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"搜索尝试 {attempt + 1}/{MAX_RETRIES}: {query}")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=os.getenv('HEADLESS', 'true').lower() == 'true',
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-blink-features=AutomationControlled',
                    ],
                )
                
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                    locale='zh-CN',
                    viewport={'width': 1920, 'height': 1080},
                    extra_http_headers={
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    },
                )
                
                # 隐藏自动化特征
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                    });
                    window.chrome = { runtime: {} };
                """)
                
                page = context.new_page()
                
                logger.info(f"导航到: {url}")
                response = page.goto(url, wait_until='domcontentloaded', timeout=TIMEOUT)
                logger.info(f"HTTP Status: {response.status}")
                
                # 等待页面加载
                page.wait_for_timeout(3000)
                
                # 检查Cloudflare
                cloudflare = page.evaluate('''
                    () => {
                        return document.body.innerText.includes("Checking your browser") ||
                               document.body.innerText.includes("Just a moment") ||
                               document.querySelector('iframe[src*="challenges.cloudflare.com"]') !== null;
                    }
                ''')
                
                if cloudflare:
                    logger.warning('检测到 Cloudflare 挑战，等待 10 秒...')
                    page.wait_for_timeout(10000)
                
                # 提取搜索结果
                results = page.evaluate('''
                    () => {
                        const results = [];
                        const containers = document.querySelectorAll('.c-container, .result');
                        
                        containers.forEach(container => {
                            const titleElem = container.querySelector('.t a, .c-title a, h3 a');
                            if (!titleElem) return;
                            
                            const title = titleElem.textContent.trim();
                            const url = titleElem.href;
                            const summaryElem = container.querySelector('.c-abstract, .c-font-normal, .c-span9');
                            const summary = summaryElem ? summaryElem.textContent.trim() : '';
                            
                            results.push({ title, url, summary });
                        });
                        
                        return results;
                    }
                ''')
                
                browser.close()
                
                # 过滤官方网站
                official_results = [r for r in results if is_official_url(r['url'])]
                logger.info(f"找到 {len(official_results)} 条官方网站结果")
                
                return official_results[:max_results]
                
        except PlaywrightTimeout:
            logger.error(f"搜索超时 (尝试 {attempt + 1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                logger.info(f"等待 {RETRY_INTERVAL} 秒后重试...")
                import time
                time.sleep(RETRY_INTERVAL)
            else:
                raise
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            if attempt < MAX_RETRIES - 1:
                logger.info(f"等待 {RETRY_INTERVAL} 秒后重试...")
                import time
                time.sleep(RETRY_INTERVAL)
            else:
                raise
    
    return []


def extract_policy_info_with_playwright(url):
    """使用Playwright提取政策信息"""
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"提取政策信息尝试 {attempt + 1}/{MAX_RETRIES}: {url}")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=os.getenv('HEADLESS', 'true').lower() == 'true',
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                    ],
                )
                
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                    locale='zh-CN',
                )
                
                page = context.new_page()
                page.goto(url, wait_until='domcontentloaded', timeout=TIMEOUT)
                page.wait_for_timeout(2000)
                
                # 提取页面内容
                content = page.evaluate('document.body.innerText')
                title = page.title()
                
                browser.close()
                
                # 从内容中提取政策信息
                policy_info = extract_policy_info_from_content(title, content, url)
                logger.info(f"成功提取政策信息: {title}")
                
                return policy_info
                
        except PlaywrightTimeout:
            logger.error(f"提取超时 (尝试 {attempt + 1}/{MAX_RETRIES}): {url}")
            if attempt < MAX_RETRIES - 1:
                logger.info(f"等待 {RETRY_INTERVAL} 秒后重试...")
                import time
                time.sleep(RETRY_INTERVAL)
            else:
                return None
        except Exception as e:
            logger.error(f"提取失败: {e}")
            if attempt < MAX_RETRIES - 1:
                logger.info(f"等待 {RETRY_INTERVAL} 秒后重试...")
                import time
                time.sleep(RETRY_INTERVAL)
            else:
                return None
    
    return None


def get_official_policy(region=None, policy_type=None, keyword=None, time_range=None, use_cache=True):
    """获取官方政策信息"""
    # 如果启用缓存，先从数据库查询
    if use_cache:
        logger.info("尝试从数据库查询缓存数据...")
        cached_policies = query_policies(region=region, policy_type=policy_type, limit=10)
        if cached_policies:
            logger.info(f"从数据库找到 {len(cached_policies)} 条缓存数据")
            return cached_policies
    
    # 构建搜索查询
    query = build_search_query(region, policy_type, keyword, time_range)
    logger.info(f"搜索查询: {query}")
    
    # 使用Playwright搜索百度
    search_results = search_baidu_with_playwright(query)
    
    if not search_results:
        logger.warning("未找到搜索结果")
        return []
    
    # 提取政策信息
    policies = []
    for result in search_results:
        logger.info(f"处理: {result['title']}")
        
        # 检查是否已在数据库中
        if use_cache:
            cached = get_policy_by_url(result['url'])
            if cached:
                logger.info(f"从数据库获取缓存: {result['title']}")
                policies.append(cached)
                continue
        
        # 提取新政策信息
        policy_info = extract_policy_info_with_playwright(result['url'])
        if policy_info:
            # 设置地区信息
            if region and not policy_info.get("region"):
                policy_info["region"] = region
            
            # 保存到数据库
            try:
                policy_id, is_new = save_policy(policy_info)
                logger.info(f"{'新增' if is_new else '更新'}政策到数据库 (ID: {policy_id})")
            except Exception as e:
                logger.error(f"保存政策到数据库失败: {e}")
            
            policies.append(policy_info)
    
    if not policies:
        logger.warning("未找到相关政策信息，请尝试调整搜索参数或稍后再试")
    else:
        logger.info(f"成功提取 {len(policies)} 条政策信息")
    
    return policies


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="查询异地就医备案政策")
    parser.add_argument('--region', type=str, help='地区名称，如省份、城市')
    parser.add_argument('--policy_type', type=str, help='政策类型，如门诊、住院、报销额度等')
    parser.add_argument('--keyword', type=str, help='搜索关键词')
    parser.add_argument('--time_range', type=str, help='时间范围，如近1年、近2年')
    parser.add_argument('--no-cache', action='store_true', help='不使用缓存，强制重新抓取')
    parser.add_argument('--stats', action='store_true', help='显示数据库统计信息')
    
    args = parser.parse_args()
    
    # 初始化数据库
    init_db()
    
    try:
        # 显示统计信息
        if args.stats:
            stats = get_statistics()
            print(json.dumps({
                "status": "success",
                "statistics": stats
            }, ensure_ascii=False, indent=2))
            return
        
        # 获取官方政策信息
        use_cache = not args.no_cache
        policies = get_official_policy(
            region=args.region,
            policy_type=args.policy_type,
            keyword=args.keyword,
            time_range=args.time_range,
            use_cache=use_cache
        )
        
        # 输出结果
        output = {
            "status": "success",
            "data": policies,
            "count": len(policies),
            "from_cache": use_cache and len(policies) > 0
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}", exc_info=True)
        output = {
            "status": "error",
            "message": f"搜索失败: {str(e)}"
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
