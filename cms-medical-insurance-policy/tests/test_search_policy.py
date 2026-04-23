#!/usr/bin/env python3
"""
测试搜索政策功能
"""

import unittest
import sys
from pathlib import Path

# 添加脚本路径到系统路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts' / 'search'))

from search_policy import (
    build_search_query,
    is_official_url,
    extract_date,
    extract_percentage,
    extract_amount,
    extract_policy_info_from_content
)


class TestSearchPolicy(unittest.TestCase):
    """测试搜索政策功能"""
    
    def test_build_search_query(self):
        """测试构建搜索查询"""
        # 测试基本查询
        query = build_search_query()
        self.assertEqual(query, "异地就医备案政策")
        
        # 测试带地区
        query = build_search_query(region="北京")
        self.assertEqual(query, "异地就医备案政策 北京")
        
        # 测试带政策类型
        query = build_search_query(policy_type="门诊")
        self.assertEqual(query, "异地就医备案政策 门诊")
        
        # 测试带关键词
        query = build_search_query(keyword="直接结算")
        self.assertEqual(query, "直接结算")
        
        # 测试带时间范围
        query = build_search_query(time_range="近1年")
        self.assertIn("2025", query)
        
        # 测试组合查询
        query = build_search_query(region="上海", policy_type="住院", time_range="近2年")
        self.assertIn("上海", query)
        self.assertIn("住院", query)
    
    def test_is_official_url(self):
        """测试官方网站判断（使用正则模式匹配）"""
        # 政府网站 (.gov.cn)
        self.assertTrue(is_official_url("https://www.nhsa.gov.cn/art/2025/art_123.html"))
        self.assertTrue(is_official_url("http://www.gov.cn/zhengce/content/2025-01/01/content_123.htm"))
        self.assertTrue(is_official_url("https://www.mohrss.gov.cn/SYrlzyhshbzb/123.html"))
        self.assertTrue(is_official_url("http://ybj.beijing.gov.cn/policy/123.html"))
        self.assertTrue(is_official_url("https://ybj.sh.gov.cn/news/456.html"))
        
        # 医保局域名
        self.assertTrue(is_official_url("http://ybj.beijing.gov.cn/"))
        self.assertTrue(is_official_url("https://www.nhsa.gov.cn/"))
        
        # 官方媒体
        self.assertTrue(is_official_url("http://www.xinhuanet.com/politics/2025-01/15/c_123.htm"))
        self.assertTrue(is_official_url("http://www.people.com.cn/n1/2025/0115/c123-456.html"))
        self.assertTrue(is_official_url("https://www.cctv.com/2025/01/15/ARTI123.shtml"))
        
        # 非官方网站
        self.assertFalse(is_official_url("https://www.baidu.com"))
        self.assertFalse(is_official_url("https://www.zhihu.com"))
        self.assertFalse(is_official_url("https://news.sina.com.cn"))
        self.assertFalse(is_official_url("https://www.example.com"))
    
    def test_extract_date(self):
        """测试日期提取"""
        # 测试不同日期格式
        self.assertEqual(extract_date("发布日期：2025年1月15日"), "2025-01-15")
        self.assertEqual(extract_date("时间: 2025-01-15"), "2025-01-15")
        self.assertEqual(extract_date("2025/01/15"), "2025-01-15")
        self.assertEqual(extract_date("2025.01.15"), "2025-01-15")
        
        # 测试无效日期
        self.assertIsNone(extract_date("没有日期的文本"))
        self.assertIsNone(extract_date("2025-13-01"))  # 无效月份
    
    def test_extract_percentage(self):
        """测试百分比提取"""
        # 测试门诊报销比例
        text = "门诊报销比例为50%"
        result = extract_percentage(text, ['门诊.*?报销比例'])
        self.assertEqual(result, "50%")
        
        # 测试住院报销比例
        text = "住院费用支付比例达到70%"
        result = extract_percentage(text, ['住院.*?支付比例'])
        self.assertEqual(result, "70%")
        
        # 测试小数百分比
        text = "报销比例为85.5%"
        result = extract_percentage(text, ['报销比例'])
        self.assertEqual(result, "85.5%")
        
        # 测试未找到
        text = "没有百分比"
        result = extract_percentage(text, ['报销比例'])
        self.assertIsNone(result)
    
    def test_extract_amount(self):
        """测试金额提取"""
        # 测试万元单位
        text = "年度限额为10万元"
        result = extract_amount(text, ['年度.*?限额'])
        self.assertEqual(result, "100000")
        
        # 测试元单位
        text = "单次限额为5000元"
        result = extract_amount(text, ['单次.*?限额'])
        self.assertEqual(result, "5000")
        
        # 测试小数
        text = "最高限额为15.5万元"
        result = extract_amount(text, ['最高.*?限额'])
        self.assertEqual(result, "155000")
        
        # 测试未找到
        text = "没有金额"
        result = extract_amount(text, ['限额'])
        self.assertIsNone(result)
    
    def test_extract_policy_info_from_content(self):
        """测试从内容中提取政策信息"""
        title = "关于做好异地就医直接结算工作的通知"
        content = """
        发布日期：2025年1月15日
        
        为进一步做好异地就医直接结算工作，现将有关事项通知如下：
        
        一、门诊报销
        门诊报销比例为50%，参保人员可在定点医疗机构直接结算。
        
        二、住院报销
        住院费用支付比例为70%，年度限额为10万元，单次限额为2万元。
        
        三、备案流程
        参保人员可通过线上或线下方式办理备案，需提供身份证、医保卡等材料。
        备案有效期为1年。
        
        四、特殊人群
        退休人员、在职职工、急诊患者、慢性病患者均可享受异地就医政策。
        
        五、社区医疗
        参保人员可在社区医疗机构就医。
        
        六、药品目录
        执行参保地药品目录，医保范围内的诊疗项目可报销。
        """
        url = "https://www.nhsa.gov.cn/art/2025/art_123.html"
        
        policy_info = extract_policy_info_from_content(title, content, url)
        
        # 验证基本信息
        self.assertEqual(policy_info["policy_name"], title)
        self.assertEqual(policy_info["release_date"], "2025-01-15")
        self.assertEqual(policy_info["source"], url)
        
        # 验证门诊信息
        self.assertTrue(policy_info["outpatient"]["available"])
        self.assertEqual(policy_info["outpatient"]["reimbursement_rate"], "50%")
        
        # 验证住院信息
        self.assertTrue(policy_info["inpatient"]["available"])
        self.assertEqual(policy_info["inpatient"]["reimbursement_rate"], "70%")
        
        # 验证报销额度
        self.assertEqual(policy_info["reimbursement_limit"]["annual_limit"], "100000")
        self.assertEqual(policy_info["reimbursement_limit"]["single_limit"], "20000")
        
        # 验证社康使用
        self.assertTrue(policy_info["community_health"])
        
        # 验证备案流程
        self.assertIn("线上", policy_info["filing_process"]["methods"])
        self.assertIn("线下", policy_info["filing_process"]["methods"])
        self.assertIn("身份证", policy_info["filing_process"]["materials"])
        self.assertIn("医保卡", policy_info["filing_process"]["materials"])
        self.assertEqual(policy_info["filing_process"]["validity"], "1年")
        
        # 验证特殊人群
        self.assertTrue(policy_info["special_groups"]["retirees"])
        self.assertTrue(policy_info["special_groups"]["workers"])
        self.assertTrue(policy_info["special_groups"]["emergency"])
        self.assertTrue(policy_info["special_groups"]["chronic_patients"])
        
        # 验证直接结算
        self.assertEqual(policy_info["direct_settlement"]["scope"], "定点医疗机构")
        
        # 验证药品目录
        self.assertEqual(policy_info["drugs_and_treatment"]["drug_list"], "参保地目录")
        self.assertEqual(policy_info["drugs_and_treatment"]["treatment_scope"], "医保范围内")


if __name__ == '__main__':
    unittest.main()
