import streamlit as st
import bs4, urllib.request, json, ssl
from datetime import date, datetime, time
from sentence_transformers import SentenceTransformer, util
from rapidfuzz import fuzz
from streamlit_autorefresh import st_autorefresh

ssl._create_default_https_context = ssl._create_unverified_context

model = SentenceTransformer('all-MiniLM-L6-v2')
THRESHOLD = 0.4
FUZZY_THRESHOLD = 85

KEYWORDS_FILE = "keywords.json"

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

def load_keywords():
    try:
        with open(KEYWORDS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_keywords(keywords):
    with open(KEYWORDS_FILE, "w") as f:
        json.dump(keywords, f)

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
                            meal_text = ''.join(td_copy.find_all(string=True, recursive=False)).strip()
                            meal_text = ' '.join(meal_text.split())
                            if meal_text:
                                items.append(meal_text)
            menus[mensa_name] = list(dict.fromkeys(items))
        except Exception as e:
            print(f"[ERROR] {mensa_name}: {e}")
            menus[mensa_name] = []
    return menus

st.title("Bayreuth Mensa Reminder")

keywords = load_keywords()

new_keyword = st.text_input("Add a keyword:")
if st.button("Add"):
    if new_keyword:
        keywords.append(new_keyword)
        save_keywords(keywords)
        st.success(f"Keyword added: {new_keyword}")

if st.button("Clear all keywords"):
    save_keywords([])
    keywords = []
    st.warning("All keywords have been cleared.")

# Display saved keywords
if keywords:
    st.subheader("Saved Keywords:")
    for keyword in keywords:
        st.write(f"- {keyword}")
else:
    st.info("No keywords saved yet.")

# -- Auto daily check switch --
if "auto_check" not in st.session_state:
    st.session_state.auto_check = False

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

# Perform auto refresh only between 7:00 and 7:05, up to 5 refreshes (1 min interval)
if st.session_state.auto_check:
    now = datetime.now()
    if time(7, 0) <= now.time() <= time(7, 5):
        st_autorefresh(interval=60 * 1000, limit=5, key="auto_refresh")

# Manual check button and logic
if st.button("Check today's Mensa menus now"):
    with st.spinner("Fetching menus..."):
        menus = scrape_menus()
        matches_found = {}

        for mensa_name, items in menus.items():
            matches = []
            for item in items:
                item_lower = item.lower()
                for keyword in keywords:
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
        else:
            st.info("No matches found in today's menus.")
