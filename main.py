from fastapi import FastAPI, Query, Request
import random
from datetime import datetime, timedelta

app = FastAPI(title="Mock Meta Marketing API v21.0 (2000 Ads)")

# 1. Generate 20 Campaigns
OBJECTIVES = [
    "OUTCOME_AWARENESS",
    "OUTCOME_TRAFFIC",
    "OUTCOME_SALES",
    "OUTCOME_LEADS",
    "OUTCOME_APP_PROMOTION",
]
CAMPAIGNS = [
    {
        "id": f"120210{i:02d}",
        "name": f"Campaign_{i:02d}_{OBJECTIVES[i % len(OBJECTIVES)]}_2026",
        "objective": OBJECTIVES[i % len(OBJECTIVES)],
        "status": "ACTIVE" if i % 4 != 0 else "PAUSED",
    }
    for i in range(1, 21)
]

# 2. Generate 100 Ad Sets (5 Ad Sets per Campaign)
AD_SETS = []
for camp in CAMPAIGNS:
    for j in range(1, 6):
        adset_id = f"2385{camp['id'][-2:]}{j:02d}"
        AD_SETS.append({
            "id": adset_id,
            "campaign_id": camp["id"],
            "campaign_name": camp["name"],
            "name": f"AdSet_{adset_id}_IN_Audience_{j}",
            "daily_budget": random.choice(),
        })

# 3. Generate 2,000 Ads (20 Ads per Ad Set)
FORMATS = ["Video", "Carousel", "Static_Image", "Collection", "Reels"]
PLATFORMS = ["facebook", "instagram", "audience_network"]
ADS = []
for idx in range(1, 2001):
    adset = AD_SETS[idx % len(AD_SETS)]
    ad_format = FORMATS[idx % len(FORMATS)]
    ADS.append({
        "id": f"65410{idx:04d}",
        "adset_id": adset["id"],
        "adset_name": adset["name"],
        "campaign_id": adset["campaign_id"],
        "campaign_name": adset["campaign_name"],
        "name": f"Ad_{idx:04d}_{ad_format}_Creative",
        "publisher_platform": PLATFORMS[idx % len(PLATFORMS)],
    })

# 4. Generate Daily Insights (2,000 ads x 3 days = 6,000 total rows)
def build_insights_data(days: int = 3):
    random.seed(42)
    records = []
    start_date = datetime(2026, 11, 14)

    for d in range(days):
        date_str = (start_date + timedelta(days=d)).strftime("%Y-%m-%d")
        for ad in ADS:
            impressions = random.randint(1500, 45000)
            clicks = int(impressions * random.uniform(0.01, 0.05))
            spend = round(clicks * random.uniform(5.0, 22.0), 2)
            purchases = int(clicks * random.uniform(0.02, 0.15))

            records.append({
                "campaign_id": ad["campaign_id"],
                "campaign_name": ad["campaign_name"],
                "adset_id": ad["adset_id"],
                "adset_name": ad["adset_name"],
                "ad_id": ad["id"],
                "ad_name": ad["name"],
                "publisher_platform": ad["publisher_platform"],
                "date_start": date_str,
                "date_stop": date_str,
                "impressions": str(impressions),
                "clicks": str(clicks),
                "spend": str(spend),
                "actions": [
                    {"action_type": "link_click", "value": str(clicks)},
                    {"action_type": "purchase", "value": str(purchases)},
                ],
            })
    return records

INSIGHTS_DB = build_insights_data(days=3)

@app.get("/v21.0/act_{ad_account_id}/insights")
def get_insights(
    request: Request,
    ad_account_id: str,
    limit: int = Query(default=250, le=1000),
    offset: int = Query(default=0),
):
    page_data = INSIGHTS_DB[offset : offset + limit]
    next_offset = offset + limit

    payload = {"data": page_data}
    if next_offset < len(INSIGHTS_DB):
        scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
        host = request.headers.get("host", request.url.netloc)
        payload["paging"] = {
            "next": f"{scheme}://{host}/v21.0/act_{ad_account_id}/insights?limit={limit}&offset={next_offset}"
        }
    return payload
