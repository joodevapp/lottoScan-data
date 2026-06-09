import json
import os
import re
import time
from playwright.sync_api import sync_playwright

def get_machine_numbers_from_lottotapa():
    machine_dict = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='ko-KR'
        )
        page = context.new_page()
        
        page.goto('https://lottotapa.com/stat/result_hogi.php', timeout=60000)
        page.wait_for_load_state('domcontentloaded')
        time.sleep(5)
        
        selects = page.evaluate("Array.from(document.querySelectorAll('select')).map(s => ({name: s.name, id: s.id, options: s.options.length}))")
        print(f"Select 목록: {selects}")
        
        browser.close()
    
    return machine_dict

get_machine_numbers_from_lottotapa()
