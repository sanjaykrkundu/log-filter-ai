import os
import json

class AnalyticsManager:
    def __init__(self, workspace_dir: str):
        self.filepath = os.path.join(workspace_dir, "analytics.json")
        self._initialize()

    def _initialize(self):
        if not os.path.exists(self.filepath):
            default_data = {
                "total_analyzed": 0,
                "successful_analyses": 0,
                "categories": {}
            }
            self._save(default_data)

    def _load(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"total_analyzed": 0, "successful_analyses": 0, "categories": {}}

    def _save(self, data):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def record_analysis(self, success: bool, category_name: str = None):
        data = self._load()
        data["total_analyzed"] += 1
        
        if success:
            data["successful_analyses"] += 1
            
        if category_name:
            if category_name not in data["categories"]:
                data["categories"][category_name] = 0
            data["categories"][category_name] += 1
            
        self._save(data)

    def get_stats(self):
        data = self._load()
        total = data.get("total_analyzed", 0)
        successes = data.get("successful_analyses", 0)
        
        success_rate = 0.0
        if total > 0:
            success_rate = round((successes / total) * 100, 1)
            
        # Format categories as required by frontend
        raw_cats = data.get("categories", {})
        categories = []
        for name, count in raw_cats.items():
            percentage = round((count / total) * 100, 1) if total > 0 else 0
            categories.append({
                "name": name,
                "count": count,
                "percentage": percentage
            })
            
        # Sort by highest count
        categories.sort(key=lambda x: x["count"], reverse=True)
        
        return {
            "totalAnalyzed": total,
            "successRate": success_rate,
            "categories": categories
        }
