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

## 🧩 Features

- Add, view, and clear meal keywords you want to track  
- Enable or disable automatic daily checks  
- Scrape the Mensa website and trigger notifications if matches are found  
- Display results in an engaging UI with emoji feedback  
- Receive structured email notifications with matched dishes by Mensa location  

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

## 🧰 Technologies Used

- **Python**  
- **Streamlit**  
- **FuzzyWuzzy** (fuzzy matching tools)  
- **Word embeddings** (for semantic similarity)  
- **Email automation** (smtplib)  
- **Web scraping** (BeautifulSoup)

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

## 🖼️ Project Poster

The poster was designed as part of the *Intelligent User Interfaces* lecture project and illustrates:
- The motivation and user need (reducing effort in checking Mensa menus)
- The layered matching approach (direct, synonym, fuzzy, semantic)
- The interactive Streamlit UI
- The automated email notification workflow
- Example user interactions and notifications in real context

You can view the full project poster here:  
👉 [Click to view the full poster (PDF)](./poster_iui_YifanLyu_cmyk.pdf)
👉 [Click to view the promotional poster (PDF)](./pitch_iui_YifanLyu.pdf)

