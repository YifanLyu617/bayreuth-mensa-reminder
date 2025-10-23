# 🍽️ Uni Bayreuth Mensa Reminder

**Helping you find and get notified about your favorite dishes.**  
An interactive web application built for the *Intelligent User Interfaces* lecture at the University of Bayreuth.

---

## 🧠 Overview

Have you ever wanted to eat your favorite Mensa dish again, but it’s too much trouble to check the menu every day?  
The **Uni Bayreuth Mensa Reminder** automatically tracks your preferred meal keywords and notifies you when matching dishes appear on the daily Mensa menu.

This Streamlit-based application connects students’ meal preferences with the daily Mensa website, helping them:
- Save time by automating menu checking  
- Reduce decision fatigue  
- Improve the daily campus dining experience

---

## ⚙️ Technical Foundation

The system uses a **multi-level keyword matching pipeline** that combines:

| Matching Level | Description |
|----------------|-------------|
| **1. Direct string matching** | Checks if the exact user input appears in the menu text |
| **2. Category synonym matching** | Maps user input to predefined category synonyms to catch variations |
| **3. Fuzzy matching** | Allows spelling mistakes from user input |
| **4. Semantic matching** | Captures meaning-based similarity using text embeddings |

The application runs as a **Streamlit web interface** and uses a **scheduler** to perform automatic daily checks at 7 AM.

---

## 🧩 Features

- Add, view, and clear meal keywords you want to track  
- Enable or disable automatic daily checks  
- Scrape the Mensa website and trigger notifications if matches are found  
- Display results in an engaging UI with emoji feedback  
- Receive structured email notifications with matched dishes by Mensa location  

---

## 🖼️ Interaction Example

In the first screenshot, the user inputs preferred keywords and clicks  
**“Check today’s Mensa menus now”**, which displays matching results directly in the UI.

In the second example, the user receives an automatic **Mensa Reminder email**,  
listing all matched dishes for the day — sorted by Mensa location.

*(You can replace the image paths below with your own screenshots.)*

![UI Screenshot](images/interface.png)  
![Email Screenshot](images/email_example.png)

---

## 🧰 Technologies Used

- **Python**  
- **Streamlit**  
- **FuzzyWuzzy / difflib** (or similar fuzzy matching tools)  
- **Word embeddings** (for semantic similarity)  
- **Email automation** (smtplib or external email service)  
- **Web scraping** (requests, BeautifulSoup)

---

## 🧑‍💻 Author

**Yifan Lyu**  
Master’s Student in Computer Science  
University of Bayreuth  
Project for the course *Intelligent User Interfaces*

---

## 📜 License

This project is released under the [MIT License](LICENSE).

---

## 💡 Future Improvements

- Add multilingual support (German/English)  
- Improve semantic similarity with transformer-based transformer embeddings (e.g. SentenceTransformers)  
- Allow custom notification times and per-user scheduling  
- Integrate with a user login system to save user preferences
