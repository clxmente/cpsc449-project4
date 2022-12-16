import httpx


def bg_job(game_info, uname, url):
    json_body = {
        "username": uname,
        "guesses": 6 - game_info["remaining_guesses"],
        "status": game_info["status"],
    }
    r = httpx.post(url=url, json=json_body)
    return r.status_code
