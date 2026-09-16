"""
12 product entries for Northwind Cloud (fictional B2B SaaS).
Each entry is a plain dict – no classes, no schemas – so knowledge_base.py
can be read and explained in under 30 seconds.
"""

PRODUCTS: list[dict] = [
    {
        "id": 1,
        "name": "Analytics Dashboard",
        "category": "Business Intelligence",
        "description": (
            "A real-time analytics dashboard that aggregates data from "
            "all connected sources into a single pane of glass. Teams can "
            "build custom charts, set KPI alerts, and share live reports "
            "with stakeholders in one click."
        ),
        "key_features": [
            "Drag-and-drop chart builder",
            "Real-time data refresh (< 5 s latency)",
            "Role-based dashboard sharing",
            "Scheduled PDF/email reports",
            "Anomaly detection alerts",
        ],
        "ideal_for": "Data teams and operations managers who need live business visibility.",
        "pricing_tier": "Growth",
    },
    {
        "id": 2,
        "name": "Workflow Automation Engine",
        "category": "Process Automation",
        "description": (
            "A no-code / low-code engine that lets teams design, deploy, "
            "and monitor multi-step business workflows triggered by events, "
            "schedules, or API calls. Cuts repetitive manual work by up to 80%."
        ),
        "key_features": [
            "Visual drag-and-drop workflow designer",
            "300+ pre-built action connectors",
            "Conditional branching and loops",
            "Human-in-the-loop approval steps",
            "Full audit trail per execution",
        ],
        "ideal_for": "Operations and RevOps teams automating repetitive cross-system tasks.",
        "pricing_tier": "Growth",
    },
    {
        "id": 3,
        "name": "Customer Data Platform",
        "category": "Data Management",
        "description": (
            "A unified CDP that stitches together customer data from CRM, "
            "marketing, support, and product sources into a single golden "
            "customer profile. Enables real-time segmentation and activation."
        ),
        "key_features": [
            "Identity resolution across sources",
            "Real-time audience segmentation",
            "One-click sync to marketing tools",
            "GDPR / CCPA consent management",
            "Predictive churn and LTV scoring",
        ],
        "ideal_for": "Marketing and growth teams needing a 360° customer view.",
        "pricing_tier": "Enterprise",
    },
    {
        "id": 4,
        "name": "AI Chat Support Agent",
        "category": "Customer Support",
        "description": (
            "An AI-powered chat agent trained on your product documentation "
            "and support history that handles Tier-1 tickets autonomously. "
            "Seamlessly escalates to human agents when confidence is low."
        ),
        "key_features": [
            "LLM-powered intent understanding",
            "Automatic knowledge-base sync",
            "Live handoff to human agents",
            "CSAT collection post-resolution",
            "Multilingual support (40+ languages)",
        ],
        "ideal_for": "Support teams looking to deflect repetitive Tier-1 tickets at scale.",
        "pricing_tier": "Growth",
    },
    {
        "id": 5,
        "name": "Identity & SSO",
        "category": "Security & Identity",
        "description": (
            "Enterprise-grade Single Sign-On and identity federation supporting "
            "SAML 2.0, OIDC, and LDAP. Provides adaptive MFA, device trust, "
            "and centralised user lifecycle management for large organisations."
        ),
        "key_features": [
            "SAML 2.0 and OIDC federation",
            "Adaptive multi-factor authentication",
            "Just-in-time provisioning (SCIM)",
            "Device trust and posture checks",
            "Centralised user directory sync",
        ],
        "ideal_for": "Enterprise IT and security teams standardising authentication across apps.",
        "pricing_tier": "Enterprise",
    },
    {
        "id": 6,
        "name": "Billing & Subscriptions",
        "category": "Revenue Operations",
        "description": (
            "A flexible billing engine that handles usage-based, seat-based, "
            "and hybrid SaaS pricing models. Automates invoicing, dunning, "
            "revenue recognition, and integrates with Stripe and major ERPs."
        ),
        "key_features": [
            "Usage-based and seat pricing models",
            "Automated dunning and retry logic",
            "Revenue recognition (ASC 606)",
            "Stripe, Zuora, and ERP connectors",
            "Self-serve customer billing portal",
        ],
        "ideal_for": "Finance and product teams launching or scaling subscription revenue.",
        "pricing_tier": "Growth",
    },
    {
        "id": 7,
        "name": "Data Warehouse Connectors",
        "category": "Data Integration",
        "description": (
            "Pre-built, maintenance-free connectors that sync data from 150+ "
            "SaaS sources into Snowflake, BigQuery, Redshift, or Databricks. "
            "Handles schema drift, backfills, and incremental loads automatically."
        ),
        "key_features": [
            "150+ source connectors (CRM, ERP, Ads)",
            "Incremental and full-refresh sync modes",
            "Auto schema drift detection",
            "Data freshness SLA monitoring",
            "Column-level lineage tracking",
        ],
        "ideal_for": "Data engineering teams centralising data into a cloud warehouse.",
        "pricing_tier": "Starter",
    },
    {
        "id": 8,
        "name": "Compliance & Audit Logging",
        "category": "Security & Compliance",
        "description": (
            "Immutable, tamper-proof audit logs for every user action across "
            "the platform. Provides out-of-the-box compliance reports for "
            "SOC 2, ISO 27001, HIPAA, and GDPR with one-click export."
        ),
        "key_features": [
            "Immutable append-only event store",
            "SOC 2, HIPAA, GDPR report templates",
            "Real-time anomaly alerting",
            "Retention policies up to 7 years",
            "SIEM integration (Splunk, Datadog)",
        ],
        "ideal_for": "Compliance, security, and legal teams in regulated industries.",
        "pricing_tier": "Enterprise",
    },
    {
        "id": 9,
        "name": "Mobile SDK",
        "category": "Developer Tools",
        "description": (
            "Lightweight iOS and Android SDKs that embed Northwind Cloud "
            "capabilities—analytics tracking, push notifications, and in-app "
            "messaging—into any mobile app with under 10 lines of code."
        ),
        "key_features": [
            "< 200 KB SDK footprint",
            "Offline event buffering",
            "Push and in-app notification delivery",
            "A/B testing and feature flags",
            "Crash and performance monitoring",
        ],
        "ideal_for": "Mobile engineering teams adding analytics and engagement to native apps.",
        "pricing_tier": "Starter",
    },
    {
        "id": 10,
        "name": "API Gateway & Rate Limiting",
        "category": "Infrastructure",
        "description": (
            "A managed API gateway that handles authentication, rate limiting, "
            "request transformation, and canary deployments for internal and "
            "public APIs. Zero-downtime deploys with automatic rollback."
        ),
        "key_features": [
            "JWT and API-key authentication",
            "Per-plan and per-user rate limiting",
            "Request/response transformation",
            "Canary and blue-green deployments",
            "Latency and error-rate dashboards",
        ],
        "ideal_for": "Platform and backend teams exposing or consuming APIs at scale.",
        "pricing_tier": "Growth",
    },
    {
        "id": 11,
        "name": "Realtime Notifications",
        "category": "Engagement",
        "description": (
            "A multi-channel notification service delivering email, SMS, "
            "push, and in-app alerts in under 200 ms at any scale. "
            "Provides preference management, frequency capping, and deep analytics."
        ),
        "key_features": [
            "Email, SMS, push, and in-app channels",
            "< 200 ms global delivery latency",
            "User notification preference center",
            "Frequency capping and quiet hours",
            "Delivery, open, and click analytics",
        ],
        "ideal_for": "Product teams needing reliable, low-latency multi-channel user alerts.",
        "pricing_tier": "Starter",
    },
    {
        "id": 12,
        "name": "Forecasting & Reporting Suite",
        "category": "Business Intelligence",
        "description": (
            "An AI-driven forecasting engine that generates revenue, pipeline, "
            "and headcount projections from your historical data. Includes "
            "pre-built executive report templates and scenario modelling."
        ),
        "key_features": [
            "AI revenue and pipeline forecasting",
            "Scenario and what-if modelling",
            "Executive board-ready report templates",
            "Salesforce and HubSpot native sync",
            "Variance analysis vs actuals",
        ],
        "ideal_for": "Finance, sales leadership, and C-suite requiring forward-looking insights.",
        "pricing_tier": "Enterprise",
    },
]
