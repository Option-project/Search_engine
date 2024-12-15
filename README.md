# Search_engine : Etape à suivre pour tester l'app

Après avoir pull la dernière version de main, suivre les étapes suivantes :

## 1-installation du LLM

(On attend que Nada termine les tests pour cette partie)

## 2-installation des requirements

faire : 

pip install -r requirements.txt

dans son environement de travail

## 3-demarrer l'API

Se placer dans Search_engine et faire :

uvicorn API.api:app --reload

Si ça fonctionne, les 3 dernières lignes devraient être :
"""
INFO:     Started server process [11604]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
"""


## 4-demarrer l'UI

Faire :

npm install

Puis :

npm start

Cela va directement demarrer l'UI dans le navigateur par defaut.