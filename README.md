# Hymnal API

Browse and search 4,485 hymns across 7 collections.

## Collections

| ID | Name | Hymns |
|---|---|---|
| 1 | Fihirana Advantista (Malagasy) | 802 |
| 2 | Hymne et Louange | 650 |
| 3 | SDA Hymnal | 695 |
| 4 | Chant Jeunesse | 6 |
| 5 | J'aime l'Eternel (JEM) | 998 |
| 6 | Fihirana Fanampiny (FFPM) | 814 |
| 7 | Donnez-Lui gloire | 520 |

## Static JSON API

Hosted on GitHub Pages — no server required.

| Endpoint | Description |
|---|---|
| `api/hymns.json` | All hymns (no lyrics) |
| `api/hymns/{id}.json` | Single hymn with lyrics |
| `api/categories.json` | All categories with counts |
| `api/categories/{id}.json` | Hymns by category (no lyrics) |

### Example

```bash
# Fetch all categories
curl https://<username>.github.io/hymnal-api/api/categories.json

# Fetch a single hymn with lyrics
curl https://<username>.github.io/hymnal-api/api/hymns/1.json
```

## FastAPI Server (optional)

For local development with search, pagination, and filtering:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Endpoints at `http://127.0.0.1:8000`:

| Method | Path | Description |
|---|---|---|
| GET | `/hymns` | List hymns (pagination + filters: `category`, `number`, `active`) |
| GET | `/hymns/search?q=praise` | Full-text search on title & lyrics |
| GET | `/hymns/by-number/{number}` | All hymns sharing a number across collections |
| GET | `/hymns/{id}` | Single hymn by ID |

Interactive docs at `/docs`.

## Deploy to GitHub Pages

1. Create a GitHub repository
2. Push all files including the `api/` folder and `index.html`
3. Go to **Settings > Pages > Source** and select the `main` branch
4. Your site will be live at `https://<username>.github.io/<repo-name>/`
