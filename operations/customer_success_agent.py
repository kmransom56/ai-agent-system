#!/usr/bin/env python3
"""
Customer Success Agent - Proactive Customer Health Monitoring
Monitors customer health, identifies expansion opportunities, prevents churn
"""
import os
import sys
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from base_agent import BaseAgent

class CustomerSuccessAgent(BaseAgent):
    """AI agent for customer success and health monitoring"""

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(
            name="Customer Success Agent",
            role="Customer Success",
            config=config or {}
        )

        # Known customers (from GTM plan - proven deployment)
        self.customers = [
            {"name": "Arby's", "locations": 3400, "devices": 10200, "vertical": "restaurant"},
            {"name": "Buffalo Wild Wings", "locations": 1200, "devices": 3600, "vertical": "restaurant"},
            {"name": "Sonic", "locations": 3500, "devices": 10500, "vertical": "restaurant"}
        ]

        self.logger.info(f"👥 Monitoring {len(self.customers)} customers")

    async def daily_health_check(self) -> Dict[str, Any]:
        """Execute daily customer health check workflow"""
        self.logger.info("🏥 Starting daily customer health check")

        try:
            # Step 1: Calculate health scores
            health_scores = await self.calculate_health_scores()

            # Step 2: Identify at-risk customers
            at_risk = [c for c in health_scores if c["health_score"] < 70]

            # Step 3: Identify expansion opportunities
            expansion_opps = await self.identify_expansion_opportunities(health_scores)

            # Step 4: Generate proactive outreach
            outreach_plan = await self.generate_outreach_plan(at_risk, expansion_opps)

            # Compile report
            report = {
                "date": datetime.now().isoformat(),
                "total_customers": len(self.customers),
                "health_scores": health_scores,
                "at_risk_customers": at_risk,
                "expansion_opportunities": expansion_opps,
                "outreach_plan": outreach_plan,
                "summary_metrics": self.calculate_summary_metrics(health_scores)
            }

            # Save context
            self.save_context(
                f"health_check_{datetime.now().strftime('%Y%m%d')}",
                report
            )

            self.logger.info(f"✅ Health check complete - {len(at_risk)} at-risk, {len(expansion_opps)} opportunities")
            self.log_metric("at_risk_customers", len(at_risk))
            self.log_metric("expansion_opportunities", len(expansion_opps))

            return {
                "success": True,
                "report": report,
                "alerts": self.generate_health_alerts(report)
            }

        except Exception as e:
            self.logger.error(f"❌ Health check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def calculate_health_scores(self) -> List[Dict]:
        """Calculate health score for each customer"""
        health_scores = []

        for customer in self.customers:
            # Calculate multi-factor health score (0-100)
            score = await self.calculate_customer_health_score(customer)

            health_scores.append({
                "customer": customer["name"],
                "health_score": score,
                "locations": customer["locations"],
                "devices": customer["devices"],
                "vertical": customer["vertical"],
                "risk_level": self.categorize_risk(score),
                "factors": await self.get_health_factors(customer)
            })

        return health_scores

    async def calculate_customer_health_score(self, customer: Dict) -> float:
        """Calculate individual customer health score"""
        # Multi-factor scoring model
        factors = {
            "platform_usage": 85.0,  # Active platform usage
            "feature_adoption": 75.0,  # Using key features
            "support_tickets": 90.0,  # Low support volume
            "executive_engagement": 80.0,  # Regular QBRs
            "payment_status": 100.0,  # On-time payments
            "nps_score": 85.0  # Net Promoter Score
        }

        # Weighted average
        weights = {
            "platform_usage": 0.25,
            "feature_adoption": 0.20,
            "support_tickets": 0.15,
            "executive_engagement": 0.15,
            "payment_status": 0.15,
            "nps_score": 0.10
        }

        score = sum(factors[k] * weights[k] for k in factors.keys())

        return round(score, 1)

    def categorize_risk(self, score: float) -> str:
        """Categorize customer risk level"""
        if score >= 80:
            return "healthy"
        elif score >= 70:
            return "attention_needed"
        else:
            return "at_risk"

    async def get_health_factors(self, customer: Dict) -> Dict[str, Any]:
        """Get detailed health factors for customer"""
        return {
            "last_login": "2025-11-07",
            "support_tickets_30d": 2,
            "feature_usage": ["device_monitoring", "alerting", "reporting"],
            "last_qbr": "2025-10-15",
            "contract_renewal": "2026-03-15"
        }

    async def identify_expansion_opportunities(self, health_scores: List[Dict]) -> List[Dict]:
        """Identify expansion and upsell opportunities"""
        opportunities = []

        for customer_health in health_scores:
            if customer_health["health_score"] >= 80:  # Only healthy customers
                # Check for expansion potential
                customer = next(c for c in self.customers if c["name"] == customer_health["customer"])

                # Upsell to additional features
                opportunities.append({
                    "customer": customer["name"],
                    "type": "feature_upsell",
                    "opportunity": "DNS/Certificate SaaS add-on",
                    "potential_arr": "$79-199/month",
                    "confidence": "high",
                    "next_step": "Schedule expansion discussion"
                })

                # Expand to more locations
                if customer["locations"] < 5000:
                    opportunities.append({
                        "customer": customer["name"],
                        "type": "location_expansion",
                        "opportunity": "Expand to remaining corporate locations",
                        "potential_arr": "$50K-150K",
                        "confidence": "medium",
                        "next_step": "Present ROI for full deployment"
                    })

        return opportunities

    async def generate_outreach_plan(self, at_risk: List[Dict], expansion_opps: List[Dict]) -> Dict[str, List]:
        """Generate proactive outreach plan"""
        plan = {
            "at_risk_outreach": [],
            "expansion_outreach": [],
            "routine_check_ins": []
        }

        # At-risk customer outreach
        for customer in at_risk:
            plan["at_risk_outreach"].append({
                "customer": customer["customer"],
                "action": "Executive escalation call",
                "urgency": "high",
                "owner": "VP Customer Success",
                "due_date": (datetime.now() + timedelta(days=2)).isoformat()
            })

        # Expansion opportunity outreach
        for opp in expansion_opps:
            plan["expansion_outreach"].append({
                "customer": opp["customer"],
                "action": opp["next_step"],
                "opportunity": opp["opportunity"],
                "urgency": "medium",
                "owner": "Account Manager",
                "due_date": (datetime.now() + timedelta(days=7)).isoformat()
            })

        return plan

    def calculate_summary_metrics(self, health_scores: List[Dict]) -> Dict[str, Any]:
        """Calculate summary health metrics"""
        if not health_scores:
            return {}

        avg_score = sum(c["health_score"] for c in health_scores) / len(health_scores)

        risk_counts = {
            "healthy": len([c for c in health_scores if c["risk_level"] == "healthy"]),
            "attention_needed": len([c for c in health_scores if c["risk_level"] == "attention_needed"]),
            "at_risk": len([c for c in health_scores if c["risk_level"] == "at_risk"])
        }

        return {
            "average_health_score": round(avg_score, 1),
            "risk_distribution": risk_counts,
            "health_trend": "improving"  # Would compare to historical data
        }

    def generate_health_alerts(self, report: Dict) -> List[str]:
        """Generate customer health alerts"""
        alerts = []

        at_risk = report.get("at_risk_customers", [])
        if at_risk:
            for customer in at_risk:
                alerts.append(f"⚠️  {customer['customer']} health score: {customer['health_score']} - Immediate attention required")

        expansion_opps = report.get("expansion_opportunities", [])
        if len(expansion_opps) > 3:
            alerts.append(f"💰 {len(expansion_opps)} expansion opportunities identified")

        return alerts

    async def run(self) -> Dict[str, Any]:
        """Main execution - called by orchestrator"""
        return await self.daily_health_check()

async def main():
    """Test customer success agent"""
    agent = CustomerSuccessAgent()
    results = await agent.run()
    print(agent.generate_report(results))

if __name__ == "__main__":
    asyncio.run(main())
