import aiohttp
from bs4 import BeautifulSoup
from googlesearch import search

RRB_SITES = [
    "https://www.rrbcdg.gov.in",
    "https://www.rrbbbs.gov.in",
    "https://www.rrbmuzaffarpur.gov.in/",
    "https://www.rrbpatna.gov.in/"
]

async def fetch_html(session, url):
    async with session.get(url) as resp:
        return await resp.text()

async def find_rrb_result(session, exam_name, year):
    """Check official sites first"""
    for site in RRB_SITES:
        html = await fetch_html(session, site)
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", string=lambda t: t and exam_name in t and year in t)
        if links:
            link = links[0]['href']
            link = site.rstrip("/") + "/" + link.lstrip("/")
            return {
                "link": link,
                "status": "Published",
                "result_date": "Check site"
            }

    # fallback: Google search
    query = f"RRB {exam_name} {year} site:rrb.gov.in result"
    for url in search(query, num_results=1):
        return {
            "link": url,
            "status": "Check link",
            "result_date": "N/A"
        }

    return None