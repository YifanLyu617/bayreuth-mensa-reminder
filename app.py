import streamlit as st
import bs4, urllib.request, ssl
from datetime import date, datetime, time
from sentence_transformers import SentenceTransformer, util
from rapidfuzz import fuzz
from streamlit_autorefresh import st_autorefresh
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =============== Initialization ===============

# Ensure session state initialization at the TOP
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "keywords" not in st.session_state:
    st.session_state.keywords = []

if "auto_check" not in st.session_state:
    st.session_state.auto_check = False

# =============== Email Configuration ===============
SENDER_EMAIL = "ubt.mensa.reminder@gmail.com"
SENDER_PASSWORD = "yyhlxnuijpobfjqc"

# =============== Utility Functions ===============
def send_email(subject, body, to_email):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        st.success(f"Email sent to {to_email} successfully.")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

ssl._create_default_https_context = ssl._create_unverified_context
model = SentenceTransformer('all-MiniLM-L6-v2')
THRESHOLD = 0.4
FUZZY_THRESHOLD = 85

CATEGORY_SYNONYMS = {
    "nudeln": ["pasta", "spaghetti", "teigwaren", "maccheroni", "lasagne", "tagliatelle", "penne"],
    "reis": ["rice", "basmati rice", "wild rice", "jasmine rice"],
    "kartoffeln": ["potato", "french fries", "mashed potatoes", "potato salad", "fried potatoes", "rose potatoes"],
    "hähnchen": ["chicken", "poulet", "chicken breast", "poulet breast", "chicken meat"],
    "rind": ["beef", "beef fillet", "ground beef", "roast beef"],
    "schwein": ["pork", "pork schnitzel", "roast pork"],
    "fisch": ["fish", "salmon", "trout", "pollock", "fish fillet"],
    "vegan": ["vegetarian", "plant-based", "vegetables", "salad", "tofu", "falafel"],
    "asiatisch": ["japanese", "chinese", "thai", "korean", "vietnamese", "indian", "indonesian"],
    "käse": ["cheese", "emmental", "feta cheese", "mozzarella", "parmesan"],
    "dessert": ["dessert", "cake", "pudding", "cream", "ice cream", "torte", "apple strudel"],
    "burger": ["burger", "hamburger", "cheeseburger", "veggie burger", "chicken burger"],
    "pizza": ["pizza", "flatbread pizza", "margherita", "pepperoni", "vegetarian pizza"],
    "dip": ["dip", "sauce", "dressing", "ketchup", "mayonnaise", "mustard"],
}

MENSA_URLS = {
    "Hauptmensa": "https://www.studentenwerk-oberfranken.de/essen/speiseplaene/bayreuth/hauptmensa/tag/",
    "Frischraum": "https://www.studentenwerk-oberfranken.de/essen/speiseplaene/bayreuth/frischraum/tag/",
}

def get_today_date():
    return date.today().strftime("%Y-%m-%d")

def scrape_menus():
    today_date = get_today_date()
    menus = {}
    for mensa_name, base_url in MENSA_URLS.items():
        full_url = base_url + today_date + ".html"
        try:
            response = urllib.request.urlopen(full_url)
            webpage = response.read()
            soup = bs4.BeautifulSoup(webpage, "html.parser")
            items = []
            hauptgerichte_divs = soup.find_all("div", class_="tx-bwrkspeiseplan__hauptgerichte")
            for div in hauptgerichte_divs:
                tables = div.find_all("table", class_="tx-bwrkspeiseplan__table-meals")
                for table in tables:
                    rows = table.find_all("tr")
                    for row in rows:
                        td = row.find("td")
                        if td:
                            td_copy = td.__copy__()
                            for sup in td_copy.find_all("sup"):
                                sup.decompose()
                            text_candidates = [t.strip() for t in td_copy.stripped_strings]
                            if text_candidates:
                                meal_text = text_candidates[0]  # 只取第一行
                                items.append(meal_text)
            menus[mensa_name] = list(dict.fromkeys(items))
        except Exception as e:
            print(f"[ERROR] {mensa_name}: {e}")
            menus[mensa_name] = []
    return menus

# =============== Streamlit Interface ===============
st.title("Bayreuth Mensa Reminder")

# --- Email Section ---
st.subheader("Email Notification Settings")
user_email_input = st.text_input("Enter your email address to receive daily notifications:", value=st.session_state.user_email)
if st.button("Save Email"):
    st.session_state.user_email = user_email_input.strip()
    st.success(f"Email address saved: {st.session_state.user_email}")

if st.session_state.user_email:
    st.info(f"Current notification email: {st.session_state.user_email}")
else:
    st.info("No email set yet for notifications.")

# --- Keywords Section ---
st.subheader("Keyword Settings")
new_keyword = st.text_input("Add a keyword:")
if st.button("Add Keyword"):
    if new_keyword.strip():
        st.session_state.keywords.append(new_keyword.strip())
        st.success(f"Keyword added: {new_keyword.strip()}")

if st.button("Clear all keywords"):
    st.session_state.keywords = []
    st.warning("All keywords have been cleared.")

if st.session_state.keywords:
    st.subheader("Saved Keywords:")
    for kw in st.session_state.keywords:
        st.write(f"- {kw}")
else:
    st.info("No keywords saved yet.")

# --- Auto Daily Check Section ---
st.subheader("Auto Daily Check")
col1, col2 = st.columns(2)
with col1:
    if st.button("Start Daily Auto Check at 7 AM"):
        st.session_state.auto_check = True
        st.success("Daily auto check enabled.")
with col2:
    if st.button("Stop Daily Auto Check"):
        st.session_state.auto_check = False
        st.warning("Daily auto check disabled.")

if st.session_state.auto_check:
    now = datetime.now()
    if time(7, 0) <= now.time() <= time(7, 5):
        st_autorefresh(interval=60 * 1000, limit=5, key="auto_refresh")

# --- Manual Check Button ---
if st.button("Check today's Mensa menus now"):
    with st.spinner("Fetching menus..."):
        menus = scrape_menus()
        matches_found = {}

        for mensa_name, items in menus.items():
            matches = []
            for item in items:
                item_lower = item.lower()
                for keyword in st.session_state.keywords:
                    keyword_lower = keyword.lower()
                    if keyword_lower in item_lower:
                        matches.append(f"{item} (direct match)")
                        break
                    synonyms = CATEGORY_SYNONYMS.get(keyword_lower, [])
                    if any(syn in item_lower for syn in synonyms):
                        matches.append(f"{item} (category match)")
                        break
                    score = fuzz.partial_ratio(keyword_lower, item_lower)
                    if score >= FUZZY_THRESHOLD:
                        matches.append(f"{item} (fuzzy match: {score})")
                        break
                    emb1 = model.encode(keyword, convert_to_tensor=True)
                    emb2 = model.encode(item, convert_to_tensor=True)
                    sim_score = util.cos_sim(emb1, emb2).item()
                    if sim_score >= THRESHOLD:
                        matches.append(f"{item} (semantic match: {sim_score:.2f})")
                        break
            if matches:
                matches_found[mensa_name] = matches

        if matches_found:
            for mensa_name, matches in matches_found.items():
                st.subheader(mensa_name)
                for match in matches:
                    st.write(match)

            if st.session_state.user_email:
                email_body = ""
                for mensa_name, matches in matches_found.items():
                    email_body += f"\n{mensa_name}:\n"
                    for match in matches:
                        email_body += f"- {match}\n"
                send_email(
                    subject="Mensa Reminder: Matched Dishes Found Today",
                    body=email_body,
                    to_email=st.session_state.user_email
                )
        else:
            st.info("No matches found in today's menus.")


