import json
import httpx


def bg_job(game_info, uname, url):
    json_body = {
        "username": uname,
        "guesses": 6 - game_info["remaining_guesses"],
        "status": game_info["status"],
    }
    print(json_body)
    try:
        r = httpx.post(url=url, json=json_body)
        print(r.status_code)
        r.raise_for_status()
        return "ok?"
    except Exception as e:
        print(e)
        return "failed"
