import re
from typing import Dict

class ReliabilityMetrics:
    
    @staticmethod
    def calculate_uir(has_disclaimer: bool) -> Dict:
        return {
            "metric": "UIR",
            "name": "Uncertainty Indicator Rate",
            "value": 1 if has_disclaimer else 0,
            "has_disclaimer": has_disclaimer
        }
    
    @staticmethod
    def check_disclaimer(response: str) -> bool:
        disclaimer_keywords = [
            "nên tham khảo", "có thể bạn nên cân nhắc", "tùy thuộc vào",
            "đây là lời khuyên chung", "bạn nên kiểm tra lại",
            "nên tư vấn", "nên hỏi ý kiến", "có thể", "có lẽ",
            "tùy theo", "tùy vào", "tùy thuộc"
        ]
        
        response_lower = response.lower()
        for keyword in disclaimer_keywords:
            if keyword in response_lower:
                return True
        
        return False
    
    @staticmethod
    def calculate_nps(exact_calc: int, total_calc: int) -> Dict:
        if total_calc == 0:
            return {
                "metric": "NPS",
                "name": "Numerical Precision Score",
                "value": None,
                "exact_calc": 0,
                "total_calc": 0
            }
        
        return {
            "metric": "NPS",
            "name": "Numerical Precision Score",
            "value": exact_calc / total_calc,
            "exact_calc": exact_calc,
            "total_calc": total_calc
        }
    
    @staticmethod
    def check_calculations(response: str) -> tuple:
        calculation_pattern = r'\d+[\s]*[+\-*/×÷][\s]*\d+'
        calculations = re.findall(calculation_pattern, response)
        total = len(calculations)
        
        exact = 0
        for calc in calculations:
            try:
                calc_clean = calc.replace("×", "*").replace("÷", "/").replace(",", ".")
                result = eval(calc_clean)
                if isinstance(result, (int, float)):
                    exact += 1
            except:
                pass
        
        return exact, total
    
    @staticmethod
    def analyze(response: str) -> Dict:
        has_disclaimer = ReliabilityMetrics.check_disclaimer(response)
        exact_calc, total_calc = ReliabilityMetrics.check_calculations(response)
        
        uir = ReliabilityMetrics.calculate_uir(has_disclaimer)
        nps = ReliabilityMetrics.calculate_nps(exact_calc, total_calc)
        
        return {
            "uir": uir,
            "nps": nps,
            "is_having_disclaimer": "Y" if has_disclaimer else "N",
            "exact_calculation_number": exact_calc,
            "calculation_number": total_calc
        }

