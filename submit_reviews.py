#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
submit_reviews.py - 根据评分结果自动提交评分
运行方式: python submit_reviews.py
"""

import json
import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.common.exceptions import TimeoutException


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


def wait_postback(driver, old_element, timeout=15):
    try:
        WebDriverWait(driver, timeout).until(EC.staleness_of(old_element))
    except TimeoutException:
        pass
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "MainContent_dropTitleList"))
    )
    time.sleep(0.5)


def select_option(driver, element_id, value, postback_target):
    try:
        old_el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        old_val = Select(old_el).first_selected_option.get_attribute("value")
        if old_val == value:
            return True
        driver.execute_script("""
            document.getElementById(arguments[0]).value = arguments[1];
            __doPostBack(arguments[2], '');
        """, element_id, value, postback_target)
        wait_postback(driver, old_el)
        return True
    except Exception:
        return False


def find_score_dropdown(driver):
    try:
        for s in driver.find_elements(By.TAG_NAME, "select"):
            options = s.find_elements(By.TAG_NAME, "option")
            if len(options) > 50:
                vals = [o.get_attribute("value") for o in options[:5] if o.get_attribute("value")]
                if all(v.isdigit() for v in vals):
                    return s
    except Exception:
        pass
    return None


def find_comment_textarea(driver):
    try:
        for ta in driver.find_elements(By.TAG_NAME, "textarea"):
            style = (ta.get_attribute("style") or "").lower()
            if "bbffff" in style or "187, 255, 255" in style:
                continue
            return ta
    except Exception:
        pass
    return None


def find_submit_button(driver):
    try:
        for inp in driver.find_elements(By.TAG_NAME, "input"):
            val = (inp.get_attribute("value") or "").strip()
            if val in ("提交", "保存", "确定", "Submit", "Save"):
                return inp
        for inp in driver.find_elements(By.CSS_SELECTOR, "input[type='submit']"):
            if inp.get_attribute("value"):
                return inp
    except Exception:
        pass
    return None


def main():
    print("=" * 50)
    print("   作业互评 - 提交工具")
    print("=" * 50)

    default_file = "reviews.json"
    input_file = input(f"请输入评分结果文件路径 (默认: {default_file}): ").strip()
    if not input_file:
        input_file = default_file

    if not os.path.exists(input_file):
        print(f"文件不存在: {input_file}")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        reviews = json.load(f)

    if not reviews:
        print("文件中没有数据")
        sys.exit(1)

    username = input("请输入学号: ").strip()
    password = input("请输入密码: ").strip()

    print("\n正在启动浏览器...")
    driver = setup_driver()
    success = 0
    skipped = 0
    failed = 0

    try:
        login(driver, username, password)

        for idx, review in enumerate(reviews):
            title = review.get("title", "")
            student = review.get("student", "")
            score = review.get("score", "")
            comment = review.get("comment", "")

            if not score or not comment:
                print(f"\n[{idx+1}/{len(reviews)}] {title} - {student}: 缺少评分或评语")
                skipped += 1
                continue

            print(f"\n[{idx+1}/{len(reviews)}] {title} - {student}: {score}分")

            # Find topic value
            try:
                topic_el = driver.find_element(By.ID, "MainContent_dropTitleList")
                topic_val = None
                for opt in Select(topic_el).options:
                    if opt.text.strip() == title.strip():
                        topic_val = opt.get_attribute("value")
                        break
                if not topic_val:
                    print("  未找到题目")
                    failed += 1
                    continue
            except Exception:
                print("  获取题目列表失败")
                failed += 1
                continue

            if not select_option(driver, "MainContent_dropTitleList", topic_val, "ctl00$MainContent$dropTitleList"):
                print("  选择题目失败")
                failed += 1
                continue

            # Find student value
            try:
                stu_el = driver.find_element(By.ID, "MainContent_dropStudent")
                stu_val = None
                for opt in Select(stu_el).options:
                    if opt.text.strip() == student.strip():
                        stu_val = opt.get_attribute("value")
                        break
                if not stu_val:
                    print("  未找到学生")
                    failed += 1
                    continue
            except Exception:
                print("  获取学生列表失败")
                failed += 1
                continue

            if not select_option(driver, "MainContent_dropStudent", stu_val, "ctl00$MainContent$dropStudent"):
                print("  选择学生失败")
                failed += 1
                continue

            # Click 显示 button
            try:
                old_ref = driver.find_element(By.ID, "MainContent_dropTitleList")
                driver.find_element(By.ID, "MainContent_btnDisplayTitle").click()
                wait_postback(driver, old_ref, 10)
            except Exception:
                print("  点击显示失败")
                failed += 1
                continue

            # Find score, comment, submit
            score_dd = find_score_dropdown(driver)
            comment_ta = find_comment_textarea(driver)
            submit_btn = find_submit_button(driver)

            if not score_dd:
                print("  未找到分数下拉列表 (可能已评分)")
                skipped += 1
                continue
            if not comment_ta:
                print("  未找到评语文本框")
                failed += 1
                continue
            if not submit_btn:
                print("  未找到提交按钮")
                failed += 1
                continue

            try:
                Select(score_dd).select_by_value(str(int(score)))
            except Exception as e:
                print(f"  设置分数失败: {e}")
                failed += 1
                continue

            try:
                comment_ta.clear()
                comment_ta.send_keys(comment)
            except Exception:
                print("  填写评语失败")
                failed += 1
                continue

            time.sleep(0.5)
            try:
                submit_btn.click()
                time.sleep(3)
                print("  提交成功")
                success += 1
            except Exception as e:
                print(f"  提交失败: {e}")
                failed += 1

    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\n{'='*50}")
        print(f"   提交结果: {success} 成功 | {skipped} 跳过 | {failed} 失败")
        print(f"{'='*50}")
        input("\n按 Enter 关闭浏览器...")
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
