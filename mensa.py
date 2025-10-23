import bs4, urllib.request
import tkinter as tk, json, webbrowser
from tkinter import messagebox
import ssl
from datetime import date, timedelta
from sentence_transformers import SentenceTransformer, util
from rapidfuzz import fuzz

ssl._create_default_https_context = ssl._create_unverified_context

model = SentenceTransformer('all-MiniLM-L6-v2')
THRESHOLD = 0.4
KEYWORDS_FILE = "keywords.json"

CATEGORY_SYNONYMS = {
    "nudeln": ["pasta", "spaghetti", "teigwaren", "maccheroni", "lasagne", "tagliatelle", "penne"],
    "reis": ["reis", "basmatireis", "wildreis", "jasminreis"],
    "kartoffeln": ["kartoffel", "pommes", "kartoffelbrei", "kartoffelsalat", "bratkartoffeln", "rosenkartoffeln"],

    # 肉类
    "hähnchen": ["huhn", "poulet", "hähnchenbrust", "pouletbrust", "hähnchenfleisch"],
    "rind": ["rindfleisch", "rind", "rinderfilet", "rinderhack", "rinderbraten"],
    "schwein": ["schweinefleisch", "schwein", "schweineschnitzel", "schweinebraten"],
    "fisch": ["fisch", "lachs", "forelle", "seelachs", "fischfilet"],

    # 素食/蔬菜类
    "vegan": ["vegetarisch", "pflanzlich", "gemüse", "salat", "tofu", "falafel"],
    "asiatisch": ["japanisch", "chinesisch", "thai", "koreanisch", "vietnamesisch", "indisch", "indonesisch"],

    # 奶制品/甜点
    "käse": ["käse", "emmentaler", "schafskäse", "mozarella", "parmesan"],
    "dessert": ["nachtisch", "kuchen", "pudding", "creme", "eis", "torte", "apfelstrudel"],

    # 特色菜系
    "burger": ["burger", "hamburger", "cheeseburger", "veggie burger", "chicken burger"],
    "pizza": ["pizza", "fladenbrotpizza", "margherita", "pepperoni", "vegetarisch pizza"],

    # 调味和酱汁
    "dip": ["dip", "soße", "sauce", "dressing", "ketchup", "mayonnaise", "senf"],
}

FUZZY_THRESHOLD = 85  

MENSA_URLS = {
    "Hauptmensa": "https://www.studentenwerk-oberfranken.de/essen/speiseplaene/bayreuth/hauptmensa/tag/",
    "Frischraum": "https://www.studentenwerk-oberfranken.de/essen/speiseplaene/bayreuth/frischraum/tag/",
}

def load_keywords():
    try:
        with open(KEYWORDS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_keywords(keywords):
    with open(KEYWORDS_FILE, "w") as f:
        json.dump(keywords, f)

def get_today_date():
    return date.today().strftime("%Y-%m-%d")

def scrape_menus():
    today_date = get_today_date()
    print(f"[INFO] Using date: {today_date}")
    menus = {}

    for mensa_name, base_url in MENSA_URLS.items():
        full_url = base_url + today_date + ".html"
        print(f"[INFO] Fetching: {full_url}")
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
                            # 创建可修改副本并去除 <sup>
                            td_copy = td.__copy__()
                            for sup in td_copy.find_all("sup"):
                                sup.decompose()
                            
                            # 精准提取“直接子节点文本”，排除反馈按钮等嵌入标签文字
                            meal_text = ''.join(td_copy.find_all(string=True, recursive=False)).strip()
                            
                            # 可选：规范空白
                            meal_text = ' '.join(meal_text.split())
                            
                            if meal_text:
                                items.append(meal_text)


            menus[mensa_name] = list(dict.fromkeys(items))

        except Exception as e:
            print(f"[ERROR] Error scraping {mensa_name}: {e}")
            menus[mensa_name] = []
    return menus

def check_for_matches():
    keywords = load_keywords()
    if not keywords:
        print("[INFO] No keywords saved.")
        return

    menus = scrape_menus()
    matches_found = {}

    for mensa_name, items in menus.items():
        matches = []
        for item in items:
            item_lower = item.lower()
            for keyword in keywords:
                keyword_lower = keyword.lower()

                # 1. 直接包含匹配
                if keyword_lower in item_lower:
                    if item not in matches:
                        matches.append(f"{item} (direct match)")
                    break

                # 2. 词表辅助匹配（检测关键词的同义词是否包含在菜名中）
                synonyms = CATEGORY_SYNONYMS.get(keyword_lower, [])
                if any(syn in item_lower for syn in synonyms):
                    if item not in matches:
                        matches.append(f"{item} (category match)")
                    break

                # 3. RapidFuzz模糊匹配（拼写容错）
                score = fuzz.partial_ratio(keyword_lower, item_lower)
                if score >= FUZZY_THRESHOLD:
                    if item not in matches:
                        matches.append(f"{item} (fuzzy match, score: {score})")
                    break
                
                # 4. 句向量语义匹配
                emb1 = model.encode(keyword, convert_to_tensor=True)
                emb2 = model.encode(item, convert_to_tensor=True)
                sim = util.cos_sim(emb1, emb2)
                sim_score = sim.item()
                if sim_score >= THRESHOLD:
                    if item not in matches:
                        matches.append(f"{item} (semantic match, score: {sim_score:.2f})")
                    break
                
        if matches:
            matches_found[mensa_name] = list(dict.fromkeys(matches))

    if matches_found:
        popup = tk.Tk()
        popup.title("Matches Found!")

        label = tk.Label(popup, text="Time for Mensa's food!", font=("Verdana", 12, "bold"))
        label.pack(pady=10)

        text_box = tk.Text(popup, width=60, height=20)
        for mensa_name, matches in matches_found.items():
            text_box.insert(tk.END, f"\n{mensa_name}:\n", "bold")
            for match in matches:
                text_box.insert(tk.END, f" • {match}\n")
        text_box.tag_configure("bold", font=("Verdana", 10, "bold"))
        text_box.config(state=tk.DISABLED)
        text_box.pack(pady=5)

        def open_menu():
            today_date = get_today_date()
            for mensa_name in matches_found.keys():  # 只打开有匹配结果的 Mensa
                base_url = MENSA_URLS[mensa_name]
                webbrowser.open(base_url + today_date + ".html")


        tk.Button(popup, text="Open Full Menu", command=open_menu, bg="lightgreen").pack(pady=5)
        tk.Button(popup, text="Close", command=popup.destroy, bg="lightcoral").pack(pady=5)

        popup.mainloop()
    else:
        print("[INFO] No matches found today.")

class MensaReminderApp:
    def __init__(self, master):
        self.master = master
        master.title("Bayreuth Mensa Reminder")

        tk.Label(master, text="Enter your favorite dish keyword:").pack(pady=5)
        self.entry = tk.Entry(master, width=40)
        self.entry.pack(pady=5)

        tk.Button(master, text="Add Keyword", command=self.add_keyword, bg="lightblue").pack(pady=5)
        tk.Button(master, text="Show Saved Keywords", command=self.show_keywords, bg="lightgreen").pack(pady=5)
        tk.Button(master, text="Clear All Keywords", command=self.clear_keywords, bg="orange").pack(pady=5)
        tk.Button(master, text="Check Now", command=check_for_matches, bg="lightyellow").pack(pady=5)
        tk.Button(master, text="Exit", command=master.quit, bg="lightcoral").pack(pady=5)

    def add_keyword(self):
        keyword = self.entry.get().strip()
        if keyword:
            keywords = load_keywords()
            keywords.append(keyword)
            save_keywords(keywords)
            messagebox.showinfo("Saved", f"Keyword '{keyword}' saved.")
            self.entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Please enter a keyword.")

    def show_keywords(self):
        keywords = load_keywords()
        if keywords:
            messagebox.showinfo("Saved Keywords", "\n".join(keywords))
        else:
            messagebox.showinfo("Saved Keywords", "No keywords saved.")

    def clear_keywords(self):
        save_keywords([])
        messagebox.showinfo("Cleared", "All keywords have been cleared.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MensaReminderApp(root)
    root.geometry("400x400+700+300")
    root.mainloop()