# Skills Manager 分类映射配置
# 数据源路径：/mnt/g/knowledge/claw-skills/skills/

CATEGORIES = {
    "dev-tools": {
        "name": "开发工具",
        "icon": "🔧",
        "skills": [
            "dev-workflow",
            "skill-forge-eval",
            "autoskill",
            "planning-with-files",
        ],
    },
    "search": {
        "name": "搜索",
        "icon": "🔍",
        "skills": [
            "tabbit-search",
            "web-search",
            "multi-search-engine",
            "find-skills",
        ],
    },
    "content": {
        "name": "内容生成",
        "icon": "📝",
        "skills": [
            "wechat-docx-export",
            "wechat-mp-content-agent",
            "douyin-video-from-docx",
            "english-learning",
            "github-trending-monitor",
            "global-news-monitor",
        ],
    },
    "ai-knowledge": {
        "name": "AI/知识库",
        "icon": "🧠",
        "skills": [
            "knowledge-qa",
            "karpathy-knowledge-base",
            "ontology",
            "knowledge-archiver",
            "knowledge-value-assessment",
            "wiki-qa",
            "goskills",
        ],
    },
    "system": {
        "name": "系统工具",
        "icon": "🛠️",
        "skills": [
            "bleachbit",
            "disk-analyzer",
            "model-downloader",
            "simple-cleanup",
            "simplify",
            "opencli-rs",
            "obsidian",
        ],
    },
    "agent": {
        "name": "智能体",
        "icon": "🤖",
        "skills": [
            "agent-browser",
            "task-dispatcher",
            "self-improving",
            "self-evolution",
            "free-ride",
            "a股市场情绪监控",
        ],
    },
}

# 技能来源判断规则
# 不在映射中的技能归为 "其他" 类别，来源标为 "开源"
