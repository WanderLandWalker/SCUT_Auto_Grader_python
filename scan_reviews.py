#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_reviews.py - 扫描作业互评系统中所有未评作业
运行方式: python scan_reviews.py
"""

import json
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.common.exceptions import TimeoutException

OUTPUT_FILE = "reviews.json"


def setup_driver():
    options = webdriver.EdgeOptions()
    options.add_argument("--start-maximized")
    try:
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)
    except Exception:
        driver = webdriver.Edge(options=options)
    return driver


def login(driver, username, password):
    driver.get("https://1024.se.scut.edu.cn/%E4%BD%9C%E4%B8%9A%E4%BA%92%E8%AF%84.aspx")
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "MainContent_dropTitleList"))
        )
        print("已直接进入互评页面")
        return
    except TimeoutException:
        pass
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "un")))
    driver.find_element(By.ID, "un").send_keys(username)
    driver.find_element(By.ID, "pd").send_keys(password)
    driver.find_element(By.ID, "index_login_btn").click()
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "MainContent_dropTitleList"))
    )
    print("登录成功")


def wait_postback(driver, old_element, timeout=15):
    """Wait for ASP.NET postback to complete. old_element becomes stale when page reloads."""
    try:
        WebDriverWait(driver, timeout).until(EC.staleness_of(old_element))
    except TimeoutException:
        pass  # No postback happened (same value selected, or page didn't change)
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "MainContent_dropTitleList"))
    )
    time.sleep(0.5)


def select_option(driver, element_id, value, postback_target):
    """Select a dropdown by value and trigger ASP.NET postback. Returns True on success."""
    try:
        old_el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        old_val = Select(old_el).first_selected_option.get_attribute("value")
        if old_val == value:
            return True  # Already selected, no postback needed

        driver.execute_script("""
            document.getElementById(arguments[0]).value = arguments[1];
            __doPostBack(arguments[2], '');
        """, element_id, value, postback_target)

        wait_postback(driver, old_el)
        return True
    except Exception as e:
        return False


def is_graded(driver):
    try:
        return "您评定的成绩" in driver.find_element(By.TAG_NAME, "body").text
    except Exception:
        return False


def has_submit_btn(driver):
    for inp in driver.find_elements(By.TAG_NAME, "input"):
        val = (inp.get_attribute("value") or "").strip()
        if val in ("提交", "保存", "确定", "Submit", "Save"):
            return True
    for btn in driver.find_elements(By.TAG_NAME, "button"):
        text = (btn.text or "").strip()
        if text in ("提交", "保存", "确定"):
            return True
    return False


def extract_data(driver):
    result = {"reference_answer": "", "student_content": "", "page_html": driver.page_source}
    try:
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        for ta in textareas:
            style = (ta.get_attribute("style") or "").lower()
            if "bbffff" in style or "187, 255, 255" in style:
                result["reference_answer"] = ta.get_attribute("value") or ta.text or ""
                break
        if not result["reference_answer"] and textareas:
            result["reference_answer"] = textareas[0].get_attribute("value") or textareas[0].text or ""
    except Exception:
        pass
    try:
        div = driver.find_element(By.CLASS_NAME, "autoBR")
        result["student_content"] = div.text or ""
    except Exception:
        try:
            result["student_content"] = driver.find_element(By.TAG_NAME, "body").text or ""
        except Exception:
            pass
    return result


def main():
    print("=" * 50)
    print("   作业互评 - 扫描工具")
    print("=" * 50)
    username = input("请输入学号: ").strip()
    password = input("请输入密码: ").strip()
    print("\n正在启动 Edge 浏览器...")
    driver = setup_driver()
    reviews = []

    try:
        login(driver, username, password)

        # Get all topic options with their values
        title_el = driver.find_element(By.ID, "MainContent_dropTitleList")
        title_options = Select(title_el).options
        topic_values = [(opt.text, opt.get_attribute("value")) for opt in title_options]
        total = len(topic_values)
        print(f"\n共发现 {total} 个题目\n")

        for ti in range(total):
            topic_name, topic_val = topic_values[ti]
            print(f"[{ti+1}/{total}] {topic_name}")

            # Select topic
            if not select_option(driver, "MainContent_dropTitleList", topic_val, "ctl00$MainContent$dropTitleList"):
                print("  选择题目失败")
                continue

            # Get student options
            try:
                stu_options = Select(driver.find_element(By.ID, "MainContent_dropStudent")).options
                stu_list = [(opt.text, opt.get_attribute("value")) for opt in stu_options]
            except Exception:
                print("  未找到学生列表")
                continue

            for si in range(len(stu_list)):
                stu_name, stu_val = stu_list[si]

                if not select_option(driver, "MainContent_dropStudent", stu_val, "ctl00$MainContent$dropStudent"):
                    continue

                # Click 显示 button
                try:
                    btn = driver.find_element(By.ID, "MainContent_btnDisplayTitle")
                    # Save old element for postback detection
                    old_ref = driver.find_element(By.ID, "MainContent_dropTitleList")
                    btn.click()
                    wait_postback(driver, old_ref, 10)
                except Exception:
                    print(f"  {stu_name}: 未找到显示按钮")
                    continue

                if is_graded(driver):
                    print(f"  {stu_name}: 已评分")
                    continue

                body_text = driver.find_element(By.TAG_NAME, "body").text
                if "未提交" in body_text:
                    print(f"  {stu_name}: 学生未提交")
                    continue

                if not has_submit_btn(driver):
                    print(f"  {stu_name}: 无可评分状态")
                    continue

                data = extract_data(driver)
                data["title"] = topic_name
                data["student"] = stu_name
                reviews.append(data)
                print(f"  {stu_name}: 已提取")

        print(f"\n--- 扫描完成 ---")

    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if reviews:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(reviews, f, ensure_ascii=False, indent=2)
            print(f"\n共提取 {len(reviews)} 个未评作业")
            print(f"文件: {os.path.abspath(OUTPUT_FILE)}")
            print(f"\n请将 {OUTPUT_FILE} 发给我进行评分处理")
        else:
            print("\n未找到未评作业")
        input("\n按 Enter 关闭浏览器...")
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
