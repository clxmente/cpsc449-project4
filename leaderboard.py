import dataclasses
import redis
import textwrap
import httpx
import socket
import os
import time

from quart import Quart, g, request, abort, make_response
from quart_schema import (
    tag,
    validate_request,
    QuartSchema,
    validate_response,
)

app = Quart(__name__)
QuartSchema(app)

r = redis.Redis(charset="utf-8", decode_responses=True)

# Thinking this structure might be best?
# players = { <--- This is a redis sorted set
#   user:username: score
#   .
#   .
#   .
# }
#
# user:username = {
#   gamesPlayed: incrby when post
#   totalScore: 6 - (guesses  - 1)
# }

# -------------------------------#
# -        Data classes         -#
# -------------------------------#
@dataclasses.dataclass
class Error:
    error: str


@dataclasses.dataclass
class User:
    gamesPlayed: int
    totalScore: int


# -------------------------------#
# -        Error Handling       -#
# -------------------------------#
@app.errorhandler(400)
async def bad_request(e):
    return {"error": f"Bad Request: {e.description}"}, 400


# -------------------------------#
# -      Helper Function(s)     -#
# -------------------------------#
async def average_score(username) -> int:
    user = r.hgetall(username)
    return int(user["totalScore"]) / int(user["gamesPlayed"])


# -------------------------------#
# -      Leaderboard Routes     -#
# -------------------------------#
@app.before_serving
def register_callback():
    hostname = socket.getfqdn()
    # port = os.environ["PORT"] # unnused for now? not sure where it would be useful
    callbackURL = f"http://{hostname}/leaderboard/report"

    data = {"url": callbackURL, "client": "leaderboard"}

    try:
        r = httpx.post(f"http://{hostname}/webhook", json=data)
        r.raise_for_status()
    except httpx.HTTPStatusError as exc:
        app.logger.critical(exc)
        app.logger.critical("Failure to Register")
        if exc.response.status_code == 502:
            app.logger.critical("Retrying again in 1 second")
            time.sleep(1)
            register_callback()
        else:
            app.logger.critical(
                f"unknown error found. response code: {exc.response.status_code}"
            )
            return
        return
    except Exception as e:
        app.logger.critical(e)
        app.logger.critical("Failure to Register")
        return

    app.logger.info("Successfully Registered Leaderboard Service")
    return


@app.route("/leaderboard/", methods=["GET"])
def leaderboard():
    return textwrap.dedent("""<h1>Leaderboard service</h1> """)


@app.route("/leaderboard/top10", methods=["GET"])
@tag("Leaderboard")
async def get_top_ten():
    return r.zrevrange("players", 0, 10, withscores=True), 200


@app.route("/leaderboard/report", methods=["POST"])
@tag("Leaderboard")
async def post_game_results():
    req_body = await request.get_json()
    app.logger.info(req_body)
    user = req_body["username"]
    app.logger.info(f"user: {user}")
    guesses = req_body["guesses"]
    app.logger.info(f"guesses: {str(guesses)}")
    status = req_body["status"].lower()
    app.logger.info(f"status: {status}")

    if status != "lost" and status != "won":
        abort(400, "Status is incorrect.")

    if status == "won":
        score = 6 - (int(guesses) - 1)
    else:
        score = 0

    if r.hgetall(user) is not None:
        app.logger.info("user found")
        r.hincrby(user, "gamesPlayed", 1)
        r.hincrby(user, "totalScore", score)
        avg = await average_score(user)
        r.zadd("players", {user: avg})
    else:
        app.logger.info("user not found, creating user")
        r.hmset(user, {"gamesPlayed": 1, "totalScore": score})
        r.zadd("players", {user: score})

    app.logger.info("zadded, now returning")

    return r.hgetall(user), 200
