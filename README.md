# myefrei-scrapper

Codebase pour pouvoir scrapper [myefrei](https://www.myefrei.fr) et [moodle.myefrei](https://moodle.myefrei.fr).

## Créer une session myEfrei

Suivre les étapes suivantes

1. Dupliquer `.env.example` et le renommer en `.env`

2. Remplir les variables `USERNAME` et `PASSWORD` avec vos identifiants myEfrei.

3. Remplir la variable `TWOCAPTCHA_API_KEY` avec une clé d'API [2captcha](https://2captcha.com/2captcha-api) permettant de résoudre des reCAPATCHA V2 (NOTE: coût d'une clé reCAPATCHA V2: [$2.99/1000 queries](https://2captcha.com/2captcha-api#rates))

4. Installer les dépendances python3 nécessaire au lancement du script (`python` ou `python3` doit être accessible depuis le `PATH`)

```sh
pip install -r requirements.txt

# Ou, dans le cas d'une double installation python2 et python3

pip3 install -r requirements.txt
```

5. Tester le script `session_init_requests.py` avec python3 (`python` ou `python3` doit être accessible depuis le `PATH`)

```sh
python session_init_requests.py

# Ou, dans le cas d'une double installation python2 et python3

python3 session_init_requests.py
```

6. Pour faire des queries à partir de la session créée, importer le script et utiliser une nouvelle session créée à partir de `refresh_moodle_session` ou `refresh_myefrei_session`. 

Exemple:

`example.py`
```py
from session_init_requests import refresh_moodle_session

moodle_session = refresh_moodle_session()
my_space = moodle_session.get("https://moodle.myefrei.fr/my/")

print("\n\nResult:\n\n", my_space.text[:500])
```

```sh
>>> python3 session_init_requests.py

[INFO] 2021-11-16 22:13:39,976 — Retrieved XSRF-TOKEN & site-key! (session_init_requests.py:104)
[INFO] 2021-11-16 22:13:39,979 — Launching CAPTCHA solver ... (session_init_requests.py:78)
[INFO] 2021-11-16 22:14:01,195 — CAPTCHA Solved! (session_init_requests.py:113)
[INFO] 2021-11-16 22:14:01,394 — SESSION cookie & XSRF-TOKEN were successfully retrieved! (session_init_requests.py:135)
[INFO] 2021-11-16 22:14:01,509 — Successfully created myEfrei session! (session_init_requests.py:145)
[INFO] 2021-11-16 22:14:01,751 — Successfully retrieved OAuth link! (session_init_requests.py:161)
[INFO] 2021-11-16 22:14:04,180 — Successfully created moodle.myefrei session! (session_init_requests.py:166)

Result:

<!DOCTYPE html>
<html  dir="ltr" lang="fr" xml:lang="fr">
<head>
    <title>Tableau de bord</title>
    <link rel="icon" href="https://moodle.myefrei.fr/theme/image.php/adaptable/theme/1636033351/favicon" />

<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="keywords" content="moodle, Tableau de bord" />
<link rel="stylesheet" type="text/css" href="https://moodle.myefrei.fr/theme/yui_combo.php?rollup/3.17.2/yui-moodlesimple-min.css" /><script id="firstthemesheet"

...
```
