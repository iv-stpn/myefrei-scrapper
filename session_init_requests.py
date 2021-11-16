import re
import os
import logging
import pprint
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "myefrei-session"

# Sets up a custom logger
LOG_LEVEL = logging.getLevelName(os.getenv("LOG_LEVEL") or "WARN")


class CustomFormatter(logging.Formatter):
    from yachalk import chalk
    fmt = "[%(levelname)s] %(asctime)s — %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: chalk.blue(fmt),
        logging.INFO: chalk.green(fmt),
        logging.WARNING: chalk.yellow(fmt),
        logging.ERROR: chalk.red(fmt),
        logging.CRITICAL: chalk.bold.red(fmt)
    }

    def format(self, record):
        return logging.Formatter(self.FORMATS[record.levelno]).format(record)


logger = logging.getLogger(APP_NAME)
logger.setLevel(LOG_LEVEL)
ch = logging.StreamHandler()
ch.setLevel(LOG_LEVEL)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


# Exits the program if the given condition "cond" is False
# (displays given error message "err")
def check_or_exit(cond, err):
    if (not cond):
        logger.fatal(err)
        exit()


# Gets environment variables from the names passed in "varnames"
def get_vars_env(varnames):
    vars = {}
    for var in varnames:
        check_or_exit(
            os.getenv(var),
            f"{var} environment variable is not set! (check your .env)")
        vars[var] = os.getenv(var)

    return vars


env = get_vars_env(
    ["MYEFREI_USERNAME", "MYEFREI_PASSWORD", "TWOCAPTCHA_API_KEY"])

MYEFREI_LOGIN_URL = "https://auth.myefrei.fr/uaa/login"
MOODLE_LOGIN_URL = "https://moodle.myefrei.fr/login/index.php"

MYEFREI_HOME_URL = "https://www.myefrei.fr/portal/student/planning"

import html
import requests


def solve_captcha(site_key, url, **params):
    """
    Current implementation uses 2captcha to solve captchas 
    """
    from twocaptcha import TwoCaptcha
    try:
        solver = TwoCaptcha(env["TWOCAPTCHA_API_KEY"])
        logger.info("Launching CAPTCHA solver ...")
        captcha_result = solver.recaptcha(sitekey=site_key, url=url, **params)

    except Exception as err:
        logger.fatal(f"Unknown exception when processing captcha ({err})!")
        exit()

    return captcha_result["code"]


# Retrieve site-key & XSRF-TOKEN
def refresh_myefrei_session():
    session = requests.Session()
    myefrei_login_page = session.get(MYEFREI_LOGIN_URL)

    match_site_key = re.search('data-sitekey="([^"]*)"',
                               html.unescape(myefrei_login_page.text))

    check_or_exit(match_site_key, "reCAPATCHA sitekey not found!")
    site_key = match_site_key.group(1)

    check_or_exit("XSRF-TOKEN" in myefrei_login_page.cookies,
                  "XSRF-TOKEN not found!")
    xsrf_cookie = myefrei_login_page.cookies["XSRF-TOKEN"]

    info = {"XSRF-TOKEN": xsrf_cookie, "site-key": site_key}
    logger.info(f"Retrieved XSRF-TOKEN & site-key!")
    logger.debug(f"Data:\n{pprint.pformat(info)}")

    # Solve CAPTCHA
    captcha_success = solve_captcha(site_key,
                                    MYEFREI_LOGIN_URL,
                                    invisible=1,
                                    enterprise=0)

    logger.info(f"CAPTCHA Solved!")
    logger.debug(f"Result:\nCode: {pprint.pformat(captcha_success)}")

    # Send POST "login" request
    login_post = session.post(MYEFREI_LOGIN_URL,
                              data={
                                  "username": env["MYEFREI_USERNAME"],
                                  "password": env["MYEFREI_PASSWORD"],
                                  "_csrf": xsrf_cookie,
                                  "g-recaptcha-response": captcha_success
                              })

    logger.debug(
        f"Cookies after 'login':\n{pprint.pformat(session.cookies.get_dict())}"
    )

    # Retrieve SESSION cookie & XSRF-TOKEN
    logger.debug(f"Response Headers:\n{pprint.pformat(login_post.headers)}")
    check_or_exit(
        "SESSION" in session.cookies and "XSRF-TOKEN" in session.cookies,
        f"SESSION or XSRF-TOKEN cookie not set in response (login failed)!")

    logger.info("SESSION cookie & XSRF-TOKEN were successfully retrieved!")

    home_get = session.get(MYEFREI_HOME_URL)
    check_or_exit(home_get.url != MYEFREI_LOGIN_URL,
                  "Authentification failed (redirected to login page)!")

    logger.debug(f"Response Headers:\n{pprint.pformat(home_get.headers)}")
    check_or_exit("myefrei.sid" in session.cookies,
                  f"myefrei.sid cookie not set (unexpected)!")

    logger.info(f"Successfully created myEfrei session!")

    return session


def refresh_moodle_session():
    session = refresh_myefrei_session()

    moodle_login_page = session.get(MOODLE_LOGIN_URL)
    match_oauth_link = re.search('href="([^"]*)" title="Efrei Paris"',
                                 html.unescape(moodle_login_page.text))

    # Get OAuth link from 'https://moodle.myefrei.fr/login/index.php'
    check_or_exit(match_oauth_link,
                  "OAuth link not found in page (was expected)!")
    oauth_link = match_oauth_link.group(1)
    logger.info(f"Successfully retrieved OAuth link!")
    logger.debug(f"Link: {oauth_link}")

    session.get(oauth_link)
    logger.debug(f"Cookies:\n{pprint.pformat(session.cookies.get_dict())}")
    logger.info(f"Successfully created moodle.myefrei session!")

    return session


# A session that can query on myefrei.fr
# session = refresh_myefrei_session()

# A session that can query both on myefrei.fr and moodle.myefrei.fr
# session = refresh_moodle_session()
