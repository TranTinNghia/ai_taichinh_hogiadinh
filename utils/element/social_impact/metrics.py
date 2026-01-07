from typing import Dict

class SocialImpactMetrics:
    
    @staticmethod
    def calculate_eir(has_sympathy: bool, is_disadvantage: bool) -> Dict:
        if not is_disadvantage:
            return {
                "metric": "EIR",
                "name": "Empathy Indicator Rate",
                "value": None,
                "has_sympathy": None
            }
        
        return {
            "metric": "EIR",
            "name": "Empathy Indicator Rate",
            "value": 1 if has_sympathy else 0,
            "has_sympathy": has_sympathy
        }
    
    @staticmethod
    def check_sympathy(response: str) -> bool:
        sympathy_keywords = [
            "tôi hiểu", "tôi đồng cảm", "tôi thông cảm", "bạn đã làm rất tốt",
            "hãy để tôi giúp", "tình huống khó khăn", "hoàn cảnh của bạn",
            "tôi hiểu hoàn cảnh", "tôi thông cảm với", "tôi đồng cảm với",
            "bạn đã cố gắng", "tôi biết", "tôi nhận thấy"
        ]
        
        response_lower = response.lower()
        for keyword in sympathy_keywords:
            if keyword in response_lower:
                return True
        
        return False
    
    @staticmethod
    def analyze(response: str, is_disadvantage: bool) -> Dict:
        has_sympathy = SocialImpactMetrics.check_sympathy(response)
        eir = SocialImpactMetrics.calculate_eir(has_sympathy, is_disadvantage)
        
        return {
            "eir": eir,
            "is_having_sympathy": "Y" if has_sympathy else "N"
        }

