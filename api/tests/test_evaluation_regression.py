import sys, os
from run_evaluation import check_hallucination
from run_evaluation import check_hallucination

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_hallucination_check_detects_match():
    assert check_hallucination("Company shall pay $500", "pay $500") == True

def test_hallucination_check_detects_mismatch():
    assert check_hallucination("Company shall pay $500", "totally invented text") == False