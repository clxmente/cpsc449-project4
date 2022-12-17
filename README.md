# [CPSC 449] Project 4

## Team members:

1. Clemente Solorio
2. Clay Golan
3. Muktita Kim
4. Rakesh Singh

## Issues faced:

We couldn't figure out how to set up reads across multiple databases. Below is the code we attempted to try and cycle through different databases

```python
def __get_read_db_str():
    # use itertools.cycle() to choose a new GAMES database from wordle.toml
    # read_db will be the connection string to the database
    read_db_iter = getattr(g, "_read_db_iter", None)

    if read_db_iter is None:
        app.logger.info("Creating read_db_iter")
        read_db_iter = g._read_db_iter = itertools.cycle(
            app.config["DATABASES"]["GAMES"]
        )

    elem = next(read_db_iter)
    app.logger.info(f"Using read_db: {elem}")

    return elem
```

For some reason, the global attribute will always be null so the next element in the cycle is always the first.

## Setup Tutorials

### Initialization Stage

- To configure nginx, copy the contents of the file `nginx-config` at the root of the project, into the file on your VM located at the path `/etc/nginx/sites-enabled/tutorial`, and run `sudo service nginx restart`.

- Then, change directory into the project and run `sh bin/init.sh` to set up the necessary file structure and start the cluster with foreman.

- Finally, in a separate terminal window, while the cluster is running and active, run the command `sh bin/db.sh` from the project root to initialize the tables and populate the database with valid words, and start the services.

- To setup the cronjob, run `crontab -e`, and select the editor of your choice. Then paste in the contents of the file `crontab` into the editor and save the file.

### Using the API

> Every endpoint requires BASIC authentication _except_ for `/auth/register` and `/leaderboard/top10`

- **Create an account** by making a `POST` request to the endpoint `/auth/register` like so:

  `http POST tuffix-vm/auth/register username=your_username password=your_password`

- **Start a game** by making a `POST` request to the endpoint `/games/create` like so:

  `http POST tuffix-vm/games/create -a your_username:your_password`

- **Make a guess** by making a `POST` request with a `guess` field to the endpoint `/games/<string:game_id>` like so:

  `http POST tuffix-vm/games/0accd498-44ed-4b48-b529-9fb52fae5666 guess=YOUR_GUESS -a your_username:your_password`

  > Note: you may only make guesses for games which you started.

- **Check game history** by making a `GET` request to the endpoint `/games/<string:game_id>` like so:

  `http tuffix-vm/games/0accd498-44ed-4b48-b529-9fb52fae5666 -a your_username:your_password`

  > Note: you may only access data for games which you started.

- **Retrieve in progress games** by making a `GET` request to the endpoint `/users/<string:username>` like so:

  `http tuffix-vm/users/your_username -a your_username:your_password`

  > Note: you cannot access another users' games.

- **Check leaderboard top 10** by making a `GET` request to the endpoint `/leaderboard/top10` like so:

  `http tuffix-vm/leaderboard/top10`

- **Add a new game result** by making a `POST` request to the endpoint `/leaderboard/report` like so:

  `http POST tuffix-vm/leaderboard/report username=your_username guesses=num_guess status=win/lost`
