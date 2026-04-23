#!/usr/bin/env python3
"""
数据库管理模块
用于存储和查询异地就医备案政策信息
"""

import json
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库配置
DB_DIR = Path('.cms-data')
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / 'policies.db'

# 创建数据库引擎
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Policy(Base):
    """政策信息模型"""
    __tablename__ = 'policies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_name = Column(String(500), nullable=False)
    release_date = Column(String(50))
    region = Column(String(100), index=True)
    source = Column(String(500), unique=True, nullable=False)
    source_type = Column(String(50))  # 来源类型：国家医保局、地方政府、官方媒体等
    
    # 门诊信息
    outpatient_available = Column(Boolean)
    outpatient_rate = Column(String(20))
    
    # 住院信息
    inpatient_available = Column(Boolean)
    inpatient_rate = Column(String(20))
    
    # 报销额度
    annual_limit = Column(String(50))
    single_limit = Column(String(50))
    
    # 社康使用
    community_health = Column(Boolean)
    
    # 备案流程（JSON格式）
    filing_process = Column(Text)
    
    # 特殊人群（JSON格式）
    special_groups = Column(Text)
    
    # 直接结算（JSON格式）
    direct_settlement = Column(Text)
    
    # 药品与诊疗（JSON格式）
    drugs_and_treatment = Column(Text)
    
    # 政策时效性（JSON格式）
    policy_timeliness = Column(Text)
    
    # 常见问题（JSON格式）
    common_issues = Column(Text)
    
    # 完整内容（JSON格式）
    full_content = Column(Text)
    
    # 备注
    notes = Column(Text)
    
    # 元数据
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'policy_name': self.policy_name,
            'release_date': self.release_date,
            'region': self.region,
            'source': self.source,
            'source_type': self.source_type,
            'outpatient': {
                'available': self.outpatient_available,
                'reimbursement_rate': self.outpatient_rate
            },
            'inpatient': {
                'available': self.inpatient_available,
                'reimbursement_rate': self.inpatient_rate
            },
            'reimbursement_limit': {
                'annual_limit': self.annual_limit,
                'single_limit': self.single_limit
            },
            'community_health': self.community_health,
            'filing_process': json.loads(self.filing_process) if self.filing_process else {},
            'special_groups': json.loads(self.special_groups) if self.special_groups else {},
            'direct_settlement': json.loads(self.direct_settlement) if self.direct_settlement else {},
            'drugs_and_treatment': json.loads(self.drugs_and_treatment) if self.drugs_and_treatment else {},
            'policy_timeliness': json.loads(self.policy_timeliness) if self.policy_timeliness else {},
            'common_issues': json.loads(self.common_issues) if self.common_issues else {},
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(engine)


def save_policy(policy_info):
    """保存政策信息到数据库"""
    session = Session()
    try:
        # 检查是否已存在（根据source URL）
        existing = session.query(Policy).filter_by(source=policy_info['source']).first()
        
        if existing:
            # 更新现有记录
            existing.policy_name = policy_info['policy_name']
            existing.release_date = policy_info.get('release_date')
            existing.region = policy_info.get('region')
            existing.source_type = policy_info.get('source_type')
            existing.outpatient_available = policy_info['outpatient'].get('available')
            existing.outpatient_rate = policy_info['outpatient'].get('reimbursement_rate')
            existing.inpatient_available = policy_info['inpatient'].get('available')
            existing.inpatient_rate = policy_info['inpatient'].get('reimbursement_rate')
            existing.annual_limit = policy_info['reimbursement_limit'].get('annual_limit')
            existing.single_limit = policy_info['reimbursement_limit'].get('single_limit')
            existing.community_health = policy_info.get('community_health')
            existing.filing_process = json.dumps(policy_info.get('filing_process', {}), ensure_ascii=False)
            existing.special_groups = json.dumps(policy_info.get('special_groups', {}), ensure_ascii=False)
            existing.direct_settlement = json.dumps(policy_info.get('direct_settlement', {}), ensure_ascii=False)
            existing.drugs_and_treatment = json.dumps(policy_info.get('drugs_and_treatment', {}), ensure_ascii=False)
            existing.policy_timeliness = json.dumps(policy_info.get('policy_timeliness', {}), ensure_ascii=False)
            existing.common_issues = json.dumps(policy_info.get('common_issues', {}), ensure_ascii=False)
            existing.full_content = json.dumps(policy_info, ensure_ascii=False)
            existing.notes = policy_info.get('notes')
            existing.updated_at = datetime.now()
            
            session.commit()
            return existing.id, False  # 返回ID和是否新建的标志
        else:
            # 创建新记录
            policy = Policy(
                policy_name=policy_info['policy_name'],
                release_date=policy_info.get('release_date'),
                region=policy_info.get('region'),
                source=policy_info['source'],
                source_type=policy_info.get('source_type'),
                outpatient_available=policy_info['outpatient'].get('available'),
                outpatient_rate=policy_info['outpatient'].get('reimbursement_rate'),
                inpatient_available=policy_info['inpatient'].get('available'),
                inpatient_rate=policy_info['inpatient'].get('reimbursement_rate'),
                annual_limit=policy_info['reimbursement_limit'].get('annual_limit'),
                single_limit=policy_info['reimbursement_limit'].get('single_limit'),
                community_health=policy_info.get('community_health'),
                filing_process=json.dumps(policy_info.get('filing_process', {}), ensure_ascii=False),
                special_groups=json.dumps(policy_info.get('special_groups', {}), ensure_ascii=False),
                direct_settlement=json.dumps(policy_info.get('direct_settlement', {}), ensure_ascii=False),
                drugs_and_treatment=json.dumps(policy_info.get('drugs_and_treatment', {}), ensure_ascii=False),
                policy_timeliness=json.dumps(policy_info.get('policy_timeliness', {}), ensure_ascii=False),
                common_issues=json.dumps(policy_info.get('common_issues', {}), ensure_ascii=False),
                full_content=json.dumps(policy_info, ensure_ascii=False),
                notes=policy_info.get('notes')
            )
            
            session.add(policy)
            session.commit()
            return policy.id, True  # 返回ID和是否新建的标志
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def query_policies(region=None, policy_type=None, limit=10):
    """查询政策信息"""
    session = Session()
    try:
        query = session.query(Policy)
        
        if region:
            query = query.filter(Policy.region.like(f'%{region}%'))
        
        if policy_type:
            if policy_type == '门诊':
                query = query.filter(Policy.outpatient_available == True)
            elif policy_type == '住院':
                query = query.filter(Policy.inpatient_available == True)
        
        # 按更新时间倒序
        query = query.order_by(Policy.updated_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        policies = query.all()
        return [p.to_dict() for p in policies]
    finally:
        session.close()


def get_policy_by_url(url):
    """根据URL获取政策信息"""
    session = Session()
    try:
        policy = session.query(Policy).filter_by(source=url).first()
        return policy.to_dict() if policy else None
    finally:
        session.close()


def get_statistics():
    """获取统计信息"""
    session = Session()
    try:
        total = session.query(Policy).count()
        regions = session.query(Policy.region).distinct().count()
        
        return {
            'total_policies': total,
            'total_regions': regions,
            'last_updated': session.query(Policy.updated_at).order_by(Policy.updated_at.desc()).first()[0].isoformat() if total > 0 else None
        }
    finally:
        session.close()


if __name__ == '__main__':
    # 初始化数据库
    init_db()
    print("数据库初始化完成")
    print(f"数据库路径: {DB_PATH}")
