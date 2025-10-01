import asyncio
import aiohttp
import zstandard as zstd
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify
import logging, json, os, base64

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

SETTINGS_FILE = "settings.json"

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"cookies": {"PHPSESSID":"","user_id":""}, "theme":"dark"}
    with open(SETTINGS_FILE,"r") as f:
        return json.load(f)

def save_settings(data):
    with open(SETTINGS_FILE,"w") as f:
        json.dump(data,f, indent=2)

# Load settings
SETTINGS = load_settings()
COOKIES = SETTINGS.get("cookies", {"PHPSESSID":"","user_id":""})
THEME = SETTINGS.get("theme","dark")

HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://filman.cc",
    "Referer": "https://filman.cc/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

# --- Helper Functions ---
def safe_decompress(raw, enc):
    try:
        if "zstd" in enc:
            dctx = zstd.ZstdDecompressor()
            with dctx.stream_reader(raw) as reader:
                chunks=[]
                while True:
                    c = reader.read(16384)
                    if not c: break
                    chunks.append(c)
                return b"".join(chunks).decode("utf-8", errors="replace")
        else:
            return raw.decode("utf-8", errors="replace")
    except Exception as e:
        logging.warning("Decompress error: %s", e)
        return raw.decode("utf-8", errors="replace")

async def fetch_url(url, method="GET", data=None):
    async with aiohttp.ClientSession(headers=HEADERS, cookies=COOKIES) as session:
        if method=="POST":
            async with session.post(url, data=data) as resp:
                raw = await resp.read()
                return safe_decompress(raw, resp.headers.get("Content-Encoding",""))
        else:
            async with session.get(url) as resp:
                raw = await resp.read()
                return safe_decompress(raw, resp.headers.get("Content-Encoding",""))

# --- Search ---
async def search_filman(phrase):
    url = "https://filman.cc/szukam"
    data = {"phrase": phrase}
    html = await fetch_url(url, method="POST", data=data)
    soup = BeautifulSoup(html, "html.parser")
    results=[]
    for div in soup.select("div.col-xs-3.col-lg-2"):
        a = div.find("a")
        img = div.find("img")
        if a and img:
            results.append({
                "title": img.get("alt","No title"),
                "url": a.get("href"),
                "img": img.get("src")
            })
    return results

# --- Movie episodes ---
async def parse_movie(url):
    html = await fetch_url(url)
    soup = BeautifulSoup(html,"html.parser")
    episodes = {}
    title_tag = soup.find("h1")
    movie_title = title_tag.text.strip() if title_tag else "Movie"

    ep_list = soup.select("ul#episode-list > li")
    if not ep_list:  # No seasons, single movie
        eps = [{"title": "Play", "url": url}]
        episodes["Movie"] = eps
        return movie_title, episodes

    for li in ep_list:
        season_name = li.find("span").text.strip() if li.find("span") else "Season"
        eps = []
        for a in li.select("ul li a"):
            eps.append({"title": a.text.strip(), "url": a.get("href")})
        episodes[season_name] = eps
    return movie_title, episodes

# --- Episode links ---
async def parse_episode_links(ep_url):
    html = await fetch_url(ep_url)
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a_tag in soup.select("a[data-iframe]"):
        data_attr = a_tag.get("data") or a_tag.get("data-iframe")
        if not data_attr:
            continue
        try:
            try:
                iframe_data = json.loads(data_attr)
            except:
                iframe_data = json.loads(base64.b64decode(data_attr))
            links.append({
                "host": a_tag.get_text(strip=True).split()[0],
                "url": iframe_data.get("src"),
                "width": iframe_data.get("width"),
                "height": iframe_data.get("height")
            })
        except:
            continue
    return links

# --- Routes ---
@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q")
    results=[]
    if query:
        results = asyncio.run(search_filman(query))
    return render_template("index.html", results=results, query=query, theme=THEME, cookies=COOKIES)

@app.route("/movie", methods=["GET"])
def movie():
    url = request.args.get("url")
    if not url:
        return "No URL provided"
    movie_title, episodes = asyncio.run(parse_movie(url))
    return render_template("movie.html", movie_title=movie_title, episodes=episodes, theme=THEME, cookies=COOKIES)

@app.route("/episode", methods=["GET"])
def episode():
    url = request.args.get("url")
    if not url:
        return jsonify({"links":[]})
    links = asyncio.run(parse_episode_links(url))
    return jsonify({"links": links})

@app.route("/update_cookies", methods=["POST"])
def update_cookies():
    global COOKIES, SETTINGS
    PHPSESSID = request.form.get("PHPSESSID")
    user_id = request.form.get("user_id")
    COOKIES["PHPSESSID"] = PHPSESSID
    COOKIES["user_id"] = user_id
    SETTINGS["cookies"] = COOKIES
    save_settings(SETTINGS)
    return jsonify({"status":"success"})

@app.route("/update_theme", methods=["POST"])
def update_theme():
    global THEME, SETTINGS
    theme = request.form.get("theme","dark")
    THEME = theme
    SETTINGS["theme"] = theme
    save_settings(SETTINGS)
    return jsonify({"status":"success"})

if __name__=="__main__":
    app.run(host="0.0.0.0", debug=True)
