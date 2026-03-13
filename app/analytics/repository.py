from app.db import get_analytics_snapshots_collection


class AnalyticsRepository:
    def __init__(self) -> None:
        self.collection = get_analytics_snapshots_collection()

    async def create_indexes(self) -> None:
        await self.collection.create_index("metric")
        await self.collection.create_index("created_at")