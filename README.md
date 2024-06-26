# AnumbyMasterMind
Implémentation du jeu MasterMind pour être associé avec un Robot et une logique neuronale

Ce package Python est disponible en public. Il s'installe avec l'outil `pip` (il faut avoir Python installé). Une fois [installé](#installation),
vous disposez de plusieurs applications:

- [AnumbyMasterMind](#anumbymastermind)

![Run](capture.jpg)

## AnumbyMasterMind

- il y a N couleurs possibles 1, .. , N (par défaut N=6)
- le jeu choisit P couleurs au hasard parmi les N couleurs (par défaut P=3)
- le joeur peut choisir 3 niveaux de difficulté
    - facile: P=2 et N=3
    - difficile: P=3 et N=5
    - très difficile: P=6 et N=6
- le joueur sélectione une combinaison de P couleurs
    - le jeu dit pour chaque combinaison proposée:
      - combien de positions sont exactes
      - combien de positions existent mais sont mal placées
      - combien de positions sont inexactes

 la reconnaissance des caractères est assurée par easyocr:

```> pip install easyocr```

- les images peuvent être produites
    - soit par la caméra interne du PC
    - soit par le robot Anumby (donc par un ESP32-CAM qui y est installé)

- sur l'image, on affiche si une reconnaissance a été positive et la qualité de la reconnaissance

## Installation

``pip install AnumbyMasterMind``

ou

``pip install AnumbyMasterMind==<version>``

## Installation à partir d'une clé USB

- on définit et crée un espace de travail ``HERE``
    - cd ``HERE``
- on part de la version de python ``python-3.12.2-amd64.exe``
    - que l'on installe en local dans cet espace dédié (``HERE``)
- on crée un kit ``pip`` contenant toutes les librairies nécessaires, avec la commande
    - ``py -m pip download -r requirements.txt -d deps``

    - ce qui crée un dossier ``deps`` avec toutes les librairies décrites dans requirements.txt
- toujours, dans ``HERE``, on installe ces librairies, avec la commande:
    - ``py -m pip install --no-index --find-links=deps -r requirements.txt``
- dans ``HERE/models``, on copie aussi le modèle ``easyocr``
- ainsi on peut lancer l'application:
    - ``py AnumbyMasterMind.py``

Pour créer la clé USB on rassemble:

- le kit d'installation python ``python-3.12.2-amd64.exe``
- l'ensemble des librairies nécessaires dans le dossier ``reps`` créé précédemment
- l'application ``AnumbyMasterMind/__main__.py`` -> ``AnumbyMasterMind.py``
- le script d'installation ``usb/install.bat`` et le script de lancement de l'application ``usb/play.bat``

``
set HERE=d:\workspace\testmastermind\
set PATH=%HERE%\python\Scripts\;%HERE%\python\;%PATH%
``

- les modèles ``OCR`` dans le dossier ``models``

## Déinstallation

``pip uninstall -y AnumbyMasterMind``

# Reconstruction du package ``PyPI``.

- 1) incrémenter le numéro de version => modifier VERSION
- 2) lancer `build.bat`

# License

Copyright 2024 Chris Arnault

License CECILL
