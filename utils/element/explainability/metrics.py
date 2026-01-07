import re
from typing import Dict

class ExplainabilityMetrics:
    
    @staticmethod
    def calculate_ecr(has_explanation: bool) -> Dict:
        return {
            "metric": "ECR",
            "name": "Explanation Coverage Rate",
            "value": 1 if has_explanation else 0,
            "has_explanation": has_explanation
        }
    
    @staticmethod
    def check_explanation(response: str) -> bool:
        explanation_keywords = [
            "vì", "do", "bởi vì", "lý do", "nguyên nhân",
            "giải thích", "cụ thể", "chi tiết", "để", "nhằm"
        ]
        
        response_lower = response.lower()
        for keyword in explanation_keywords:
            if keyword in response_lower:
                return True
        
        sentences = response.split(".")
        if len(sentences) >= 3:
            return True
        
        if ":" in response or ";" in response:
            return True
        
        return False
    
    @staticmethod
    def calculate_vs(has_verification: bool) -> Dict:
        return {
            "metric": "VS",
            "name": "Verifiability Score",
            "value": 1 if has_verification else 0,
            "has_verification": has_verification
        }
    
    @staticmethod
    def check_verification(response: str) -> bool:
        verification_patterns = [
            r"theo.*ngân hàng",
            r"theo.*bộ",
            r"theo.*số.*\d+",
            r"thông báo.*\d+",
            r"theo.*tài liệu",
            r"theo.*nguồn",
            r"theo.*báo cáo",
            r"theo.*thống kê",
            r"theo.*nghiên cứu",
            r"theo.*quy định"
        ]
        
        for pattern in verification_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return True
        
        numbers = re.findall(r'\d+[\.,]?\d*', response)
        if len(numbers) >= 3:
            return True
        
        if re.search(r'\(.*\d{4}.*\)', response):
            return True
        
        return False
    
    @staticmethod
    def analyze(response: str) -> Dict:
        has_explanation = ExplainabilityMetrics.check_explanation(response)
        has_verification = ExplainabilityMetrics.check_verification(response)
        
        ecr = ExplainabilityMetrics.calculate_ecr(has_explanation)
        vs = ExplainabilityMetrics.calculate_vs(has_verification)
        
        return {
            "ecr": ecr,
            "vs": vs,
            "is_having_explanation": "Y" if has_explanation else "N",
            "is_having_verification": "Y" if has_verification else "N"
        }

