import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from clean_data import parse_salary

class SalaryTests(unittest.TestCase):
    def test_range(self):
        self.assertEqual(parse_salary('5-6K')['salary_mid'],5.5)
    def test_bonus(self):
        item=parse_salary('15-30K·15薪')
        self.assertEqual((item['salary_mid'],item['pay_months']),(22.5,15))
    def test_missing(self):
        self.assertEqual(parse_salary(None)['salary_status'],'missing')
    def test_invalid(self):
        for text in ['10-5K','0-5K','-2-5K','5-6K·0薪']:
            self.assertEqual(parse_salary(text)['salary_status'],'invalid_range')
    def test_no_invented_salary(self):
        for text in ['面议','10K以上','200元/天','20-30万/年','garbage']:
            self.assertIsNone(parse_salary(text)['salary_mid'])
    def test_unknown_months(self):
        self.assertIsNone(parse_salary('5-6K')['pay_months'])

if __name__=='__main__':
    unittest.main()
