import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
from PIL import Image
import pytesseract
import tkinter as tk
from tkinter import scrolledtext, simpledialog

# Setup
driver = webdriver.Chrome()
driver.set_window_size(1200, 1000)
wait = WebDriverWait(driver, 20)

# Function to process each roll number
def process_roll_number(roll_number, text_area):
    print(f"🌐 Opened Program Selection Page for Roll No: {roll_number}")
    driver.get("https://result.rgpv.ac.in/result/programselect.aspx?id=$%25")

    # Click the B.Tech. label under Main Result
    btech_label = wait.until(EC.element_to_be_clickable((By.XPATH, "//label[@for='radlstProgram_1']")))
    btech_label.click()
    print("✅ Clicked B.Tech. Label")

    # Wait for CAPTCHA image to appear and capture it
    captcha_img = wait.until(EC.presence_of_element_located((By.XPATH, "//img[contains(@src, 'CaptchaImage.axd')]")))
    time.sleep(4)  # Wait for clarity
    captcha_img.screenshot("captcha.png")
    img = Image.open("captcha.png")

    # OCR to extract CAPTCHA
    captcha_text = pytesseract.image_to_string(img).strip().replace(" ", "").replace("\n", "")
    print("🔍 Extracted CAPTCHA Text:", captcha_text)

    # Fill roll number
    driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtrollno").send_keys(roll_number)
    print(f"✍️ Entered Roll Number: {roll_number}")
    time.sleep(1)

    # Fill CAPTCHA
    driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_TextBox1").send_keys(captcha_text)
    print(f"✍️ Entered CAPTCHA Text: {captcha_text}")
    time.sleep(1)

    # Select Semester 3
    semester_dropdown = Select(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_drpSemester"))
    semester_dropdown.select_by_visible_text("3")
    print("📘 Selected Semester: 3")
    time.sleep(1)

    # Submit the form
    submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='View Result']")))
    submit_btn.click()
    print("🚀 Submitted the Form")

    # Wait for 5 seconds to ensure the page loads
    time.sleep(5)

    try:
        # Handle any unexpected alerts (e.g., incorrect CAPTCHA message)
        alert = driver.switch_to.alert
        alert.accept()  # Accept the alert to close it
        print("❌ CAPTCHA Error - Alert Dismissed. Retrying...")
        return False
    except:
        pass  # No alert present, continue with the normal flow

    # Grab all the visible text from the page
    result_text = driver.find_element(By.TAG_NAME, "body").text

    print("\n📄 Full Result:")
    print(result_text)  # Print all the text content on the result page
    text_area.insert(tk.END, f"✅ Successfully processed Roll No: {roll_number}\n{result_text}\n\n")
    text_area.yview(tk.END)  # Scroll to the bottom
    return result_text  # Return the result text to display on screen

# Create the Tkinter window
window = tk.Tk()
window.title("Roll Number Result Scraper")
window.geometry("800x600")

# Create a ScrolledText widget to display the results
text_area = scrolledtext.ScrolledText(window, width=100, height=30)
text_area.pack(padx=10, pady=10)

# Function to process the roll numbers and display the results in the GUI
def start_processing():
    # Ask the user for the constant part of the roll number
    constant_part = simpledialog.askstring("Input", "Enter the constant part of the roll number (e.g. 0103AL231):", parent=window)
    
    # Ask the user for the range of roll numbers
    start_roll = simpledialog.askstring("Input", "Enter the starting roll number (e.g. 001):", parent=window)
    end_roll = simpledialog.askstring("Input", "Enter the ending roll number (e.g. 084):", parent=window)

    # Validate the user input
    if constant_part and start_roll and end_roll and start_roll.isdigit() and end_roll.isdigit():
        start_roll = int(start_roll)
        end_roll = int(end_roll)

        # Start processing each roll number in a separate thread
        def process_roll_numbers():
            for i in range(start_roll, end_roll + 1):  # Loop through the range entered by the user
                roll_number = f"{constant_part}{i:03d}"
                while True:
                    result = process_roll_number(roll_number, text_area)
                    if result:
                        break  # Break from the while loop once the result is successful
                    else:
                        text_area.insert(tk.END, f"🔄 Retrying Roll No: {roll_number}...\n")
                        text_area.yview(tk.END)
                        time.sleep(2)  # Wait for a moment before retrying

            text_area.insert(tk.END, "✅ All roll numbers processed!\n")
            text_area.yview(tk.END)  # Scroll to the bottom when done

        # Run the roll number processing in a separate thread to keep the UI responsive
        threading.Thread(target=process_roll_numbers, daemon=True).start()

    else:
        text_area.insert(tk.END, "❌ Invalid input! Please enter valid data.\n")
        text_area.yview(tk.END)

# Create a button to start the processing
start_button = tk.Button(window, text="Start Processing", command=start_processing)
start_button.pack(pady=20)

# Run the Tkinter event loop
window.mainloop()

# Close the browser after all results are scraped
driver.quit()
