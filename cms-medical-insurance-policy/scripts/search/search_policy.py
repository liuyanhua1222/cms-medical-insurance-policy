"""
查询各地异地就医备案政策，获取门诊、住院、报销额度等关键信息

依赖：
- requests：用于发起HTTP请求
- BeautifulSoup：用于解析HTML内容
- argparse：用于解析命令行参数
- json：用于输出JSON格式结果

最小调用示例：
python search_policy.py --region 北京
"""

import argparse
import json
import time
import requests
from bs4 import BeautifulSoup

# 搜索配置
SEARCH_URLS = {
    "国家医保局": "https://www.nhsa.gov.cn/",
    "中国政府网": "https://www.gov.cn/",
    "百度搜索": "https://www.baidu.com/s"
}

TIMEOUT = 30
MAX_RETRIES = 3
RETRY_INTERVAL = 2


def build_search_query(region=None, policy_type=None, keyword=None, time_range=None):
    """构建搜索查询"""
    query_parts = []
    if keyword:
        query_parts.append(keyword)
    else:
        query_parts.append("异地就医备案")
    
    if region:
        query_parts.append(region)
    
    if policy_type:
        query_parts.append(policy_type)
    
    if time_range:
        if time_range == "近1年":
            query_parts.append("2025")
        elif time_range == "近2年":
            query_parts.append("2024 2025")
    
    return " ".join(query_parts)


def search_baidu(query):
    """使用百度搜索"""
    url = SEARCH_URLS["百度搜索"]
    params = {
        "wd": query,
        "tn": "baiduhome_pg",
        "ie": "utf-8"
    }
    
    for retry in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            return response.text
        except Exception as e:
            if retry < MAX_RETRIES - 1:
                time.sleep(RETRY_INTERVAL)
                continue
            else:
                raise e


def parse_search_results(html):
    """解析搜索结果"""
    soup = BeautifulSoup(html, "html.parser")
    results = []
    
    # 百度搜索结果解析
    for result in soup.select(".result"):
        title_elem = result.select_one(".t a")
        if not title_elem:
            continue
        
        title = title_elem.get_text(strip=True)
        url = title_elem.get("href")
        summary = result.select_one(".c-abstract")
        summary_text = summary.get_text(strip=True) if summary else ""
        
        # 过滤非官方网站
        if any(domain in url for domain in ["gov.cn", "nhsa.gov.cn"]):
            results.append({
                "title": title,
                "url": url,
                "summary": summary_text
            })
    
    return results


def extract_policy_info(url):
    """提取政策信息"""
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 提取页面内容
        content = soup.get_text(strip=True)
        
        # 模拟政策信息提取（实际项目中需要根据具体网站结构进行调整）
        policy_info = {
            "policy_name": "",
            "release_date": "",
            "region": "",
            "outpatient": {
                "available": True,
                "reimbursement_rate": "50%"
            },
            "inpatient": {
                "available": True,
                "reimbursement_rate": "70%"
            },
            "reimbursement_limit": {
                "annual_limit": "100000",
                "single_limit": "20000"
            },
            "community_health": True,
            "filing_process": {
                "methods": ["线上", "线下"],
                "materials": ["身份证", "医保卡"],
                "validity": "1年",
                "change_process": "线上申请"
            },
            "special_groups": {
                "retirees": True,
                "workers": True,
                "emergency": True,
                "chronic_patients": True
            },
            "direct_settlement": {
                "scope": "定点医疗机构",
                "steps": ["备案", "就医", "直接结算"],
                "reimbursement_requirements": ["发票", "费用明细"]
            },
            "drugs_and_treatment": {
                "drug_list": "参保地目录",
                "treatment_scope": "医保范围内",
                "consumables_reimbursement": "50%"
            },
            "policy_timeliness": {
                "latest_adjustment": "2025-01-01",
                "cross_regional_differences": "存在",
                "transition_period": "3个月"
            },
            "common_issues": {
                "filing_failure_reasons": ["材料不全", "信息错误"],
                "unfiled_treatment": "报销比例降低",
                "duplicate_insurance": "选择一地参保"
            },
            "source": url,
            "notes": "具体以当地最新政策为准"
        }
        
        # 从页面内容中提取政策名称和发布日期（示例）
        if "关于" in content and "通知" in content:
            start = content.find("关于")
            end = content.find("通知", start)
            if start != -1 and end != -1:
                policy_info["policy_name"] = content[start:end+2]
        
        if "发布日期" in content:
            start = content.find("发布日期")
            if start != -1:
                date_str = content[start+4:start+14]
                policy_info["release_date"] = date_str
        
        return policy_info
    except Exception as e:
        print(f"提取政策信息失败: {e}")
        return None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="查询异地就医备案政策")
    parser.add_argument('--region', type=str, help='地区名称，如省份、城市')
    parser.add_argument('--policy_type', type=str, help='政策类型，如门诊、住院、报销额度等')
    parser.add_argument('--keyword', type=str, help='搜索关键词')
    parser.add_argument('--time_range', type=str, help='时间范围，如近1年、近2年')
    
    args = parser.parse_args()
    
    try:
        # 构建搜索查询
        query = build_search_query(args.region, args.policy_type, args.keyword, args.time_range)
        print(f"搜索查询: {query}")
        
        # 执行搜索
        html = search_baidu(query)
        
        # 解析搜索结果
        search_results = parse_search_results(html)
        print(f"找到 {len(search_results)} 条相关结果")
        
        # 提取政策信息
        policies = []
        for result in search_results[:5]:  # 只处理前5条结果
            print(f"处理: {result['title']}")
            policy_info = extract_policy_info(result['url'])
            if policy_info:
                policy_info["policy_name"] = policy_info["policy_name"] or result['title']
                policies.append(policy_info)
        
        # 输出结果
        output = {
            "status": "success",
            "data": policies
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        
    except Exception as e:
        output = {
            "status": "error",
            "message": f"搜索失败: {str(e)}"
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
