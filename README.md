# Filman Web Scraper

A Flask-based web application that allows you to search and stream content from filman.cc. The application provides a clean interface to search for movies/series, browse episodes, and access streaming links.

## Features

- 🔍 **Search functionality** - Search for movies and TV series
- 🎬 **Episode browsing** - View seasons and episodes for TV series
- 🎥 **Multiple streaming hosts** - Access content from various hosting providers
- 🌓 **Dark/Light theme** - Toggle between dark and light modes
- 🍪 **Cookie management** - Configure session cookies for authenticated access
- ⚡ **Async operations** - Fast, non-blocking requests using aiohttp
- 🗜️ **Zstandard compression** - Efficient handling of compressed responses

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Installation

1. **Clone or download the project**
   ```bash
   cd filman
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure settings (optional)**
   
   Edit `settings.json` to add your cookies if needed:
   ```json
   {
     "cookies": {
       "PHPSESSID": "your_session_id",
       "user_id": "your_user_id"
     },
     "theme": "dark"
   }
   ```

## Usage

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Access the web interface**
   
   Open your browser and navigate to:
   ```
   http://localhost:5050
   ```

3. **Search for content**
   - Enter a movie or series name in the search box
   - Click on a result to view available episodes/seasons
   - Select an episode to view streaming links
   - Click on a host to open the video player

## Configuration

### Cookies
If you need authenticated access to filman.cc:
1. Log in to filman.cc in your browser
2. Open browser DevTools (F12) → Application/Storage → Cookies
3. Copy the `PHPSESSID` and `user_id` values
4. Update them via the web interface settings or directly in `settings.json`

### Theme
Switch between dark and light themes using the settings panel in the web interface.

### Port Configuration
To change the default port (5050), edit the last line in `app.py`:
```python
app.run(host="0.0.0.0", port=YOUR_PORT, debug=True)
```

## Project Structure

```
filman/
├── app.py              # Main Flask application
├── settings.json       # Configuration file (cookies, theme)
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── base.html      # Base template with layout
│   ├── index.html     # Search page
│   ├── movie.html     # Movie/series details page
│   └── episode.html   # Episode player page
└── static/            # Static assets
    ├── style.css      # Stylesheet
    └── script.js      # Client-side JavaScript
```

## API Endpoints

- `GET /` - Home page with search
- `GET /movie?url=<movie_url>` - Movie/series details
- `GET /episode?url=<episode_url>` - Get episode streaming links (JSON)
- `POST /update_cookies` - Update session cookies
- `POST /update_theme` - Update theme preference

## Troubleshooting

### Import Errors
If you encounter import errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt --upgrade
```

### Connection Issues
- Verify that filman.cc is accessible from your network
- Check if you need to update cookies for authenticated content
- Ensure your firewall allows outbound connections

### Port Already in Use
If port 5050 is already in use, either:
- Stop the application using that port
- Change the port in `app.py` (see Configuration section)

## Dependencies

- **Flask** - Web framework
- **aiohttp** - Async HTTP client for fast requests
- **BeautifulSoup4** - HTML parsing and scraping
- **zstandard** - Zstandard compression support

## Notes

- This application is for educational purposes only
- Ensure you comply with filman.cc's terms of service
- The application runs in debug mode by default (disable for production)

## License

This project is provided as-is for educational purposes.