from session_init_requests import refresh_moodle_session

moodle_session = refresh_moodle_session()
my_space = moodle_session.get("https://moodle.myefrei.fr/my/")
print("\n\nResult:\n\n", my_space.text[:500])
