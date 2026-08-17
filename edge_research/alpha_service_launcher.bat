@echo off
set "RATIFIED_CODE_DIR=C:\Users\MEDION GAMING\.alpha_vendor\ratified_code"
set "CANONICAL_CODE_DIR=C:\Users\MEDION GAMING\.alpha_vendor\canonical_code"
cd /d "C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
"C:\Users\MEDION GAMING\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m edge_research.alpha_service >> "C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\edge_research\loop_state\service_stdouterr.log" 2>&1
