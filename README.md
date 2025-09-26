# Comparaison d'algorithmes de compression 3D.

Dans le cadre de l'UE Compression, Streaming, Vidéo 3D, nous faisons implémenter à des étudiants des algorithmes de compression de maillages 3D. L'objectif de ce site Web est de comparer les différentes implémentations de chacun des groupes participant à l'UE.

## Installation

### Récupération des sources du projet
```
git clone https://gitlab.enseeiht.fr/ralcouff/csi_benchmark.git
cd csi_benchmark
```

### Création d'un environnement de travail python
```
python3 -m venv python_env
source python_env/bin/activate
pip install -r requirements.txt
```

### Premier lancement de l'application en local
```
cd benchmarkapp
flask db init
flask db migrate -m "First initialization"
flask db upgrade
flask run
```

## Pour lancer l'application
Depuis le dossier benchmarkapp
```
flask run
```


## Installation sur une machine externe
Sur Ubuntu 20.04
```
sudo apt install certbot nginx python3-certbot-nginx
```

Installer https://github.com/perusio/nginx_ensite  
Créer un fichier dans `/etc/nginx/sites-available/site.example.com`  
Dans ce fichier ajouter quelquechose dans ce genre :
```
server {
    server_name pytron.tforgione.fr;
    location / {
        proxy_pass http://localhost:3000/;
    }
}
```
Ensuite on utilise nginx pour faire : `sudo nginx_ensite site.example.com`  
Et on redémarre nginx : `sudo systemctl reload nginx`  
Et enfin on génère les certificats SSl : `sudo certbot -d site.example.com`  

## Un peu de documentation

https://getbootstrap.com/docs/3.4/css/