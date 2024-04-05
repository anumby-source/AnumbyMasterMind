import sys
import random
import cv2
import numpy as np
import easyocr
import requests
import time
import socket

N = 6
P = 3

internal_mode = 0
robot_mode = 1
mode_camera = internal_mode

# camera
image_w  = 96   # largeur image camera
image_h  = 96   # hauteur image camera

white = (255, 255, 255)
blue = (255, 0, 0)
green = (0, 255, 0)
red = (0, 0, 255)
yellow = (0, 255, 255)
magenta = (255, 0, 255)
cyan = (255, 255, 0)


class OCR:
    """
    Interface pour la reconnaissance de caractères.
    Première implémentation avec la caméra intégrée au PC
    """

    def __init__(self):
        self.reader = easyocr.Reader(['fr'])  # Utiliser EasyOCR avec la langue anglaise
        self.count = 0
        if mode_camera == internal_mode:
            self.width = 640
            self.height = 480
        else:
            #  initialisation socket udp
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.addr_port = ('192.168.4.1', 10086)  # ESP32-CAM address
            self.s.settimeout(1)
            self.color = b'BLACK'
            self.width = image_w
            self.height = image_h

    def shape(self):
        return self.height, self.width

    def internal_camera(self):
        cap = cv2.VideoCapture(0)
        ret, raw_image = cap.read()
        return raw_image

    def esp32cam(self):
        try:
            self.s.sendto(self.color, self.addr_port)
            buf = self.s.recvfrom(50000)
            raw_img = np.asarray(bytearray(buf[0]), dtype=np.uint8)
            return raw_img
        except:
            # timeout de réception de l'image
            # print('no image ', self.count)
            self.count += 1
            return None

        """
        r = requests.get("http://192.168.4.1:80/capture")
        image = np.asarray(bytearray(r.content), dtype=np.uint8)
        return cv2.imdecode(image, cv2.IMREAD_COLOR)
        """

    def read(self):
        if mode_camera == internal_mode:
            frame = self.internal_camera()
        else:
            frame = self.esp32cam()
            # print("OCR::read>", frame)

        if not frame is None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return self.reader.readtext(frame), frame
        else:
            return None, None


class Jeu:
    info_start = "Choisis une position"

    def __init__(self):
        self.info = Jeu.info_start
        self.jeu = [-1 for i in range(P)]
        self.position = -1
        self.t = time.time()

    def set_time(self):
        self.t = time.time()


class MastermindCV:
    def __init__(self):
        self.ocr = OCR()
        self.frame = None

        # Créer une fenêtre OpenCV
        cv2.namedWindow('MasterMind')

        # Définir les valeurs possibles
        self.valeurs = [i for i in range(1, N + 1)]
        self.info_start = "Choisis une position"

        self.proba = 0
        self.chiffre = 0

        #-------------------------------------------------

        self.padding = 10

        self.help_lines = [
            "ABC... : position",
            "Enter : selection",
            "X : solution",
            "",
            "I : camera interne",
            "R : camera robot",
            "N : nouveau jeu",
            "Q : quit",
        ]

        self.help_width = 180
        self.help_height = (len(self.help_lines) + 1) * 20

        self.position_width = 70
        self.position_height = 50

        # zone d'information
        self.info_width = 370
        self.info_height = int(self.position_height * 0.5)

        if mode_camera == internal_mode:
            self.camera_tag = "I"
        else:
            self.camera_tag = "R"

        # chaque ligne de jeu
        self.ligne_height = self.position_height + self.padding + self.info_height + self.padding

        self.frame_position = 0

        # -------------------------------------------------

        self.restart()

    def restart(self):

        # initialise les lignes d'info
        self.info = []
        self.info.append(self.info_start)

        # initialise la combinaison secrète
        self.secret = random.sample(self.valeurs, P)

        self.t0 = time.time()

        self.jeux = []
        self.jeux.append(Jeu())

        # initialise les jeux successives
        self.lignes = 1

        # print("valeurs", self.valeurs, "code", self.secret)

        # Dessiner l'IHM
        self.draw_ihm()

    def jeu_courant(self):
        return self.jeux[self.lignes - 1]

    def result(self):
        """
        analyse la combinaison choisie
        """
        exact = 0
        exists = 0
        off = 0
        jeu = self.jeu_courant()
        for p in range(P):
            k = jeu.jeu[p]
            if k == self.secret[p]:
                exact += 1
            elif k in self.secret:
                exists += 1
            else:
                off += 1

        r = False
        if exact == P:
            jeu.info = f"Bravo c'est gagné!!!"
            r = True
        else:
            jeu.info = f"OK={exact} on={exists} off={off}"
        # print("result", jeu.info)

        self.draw_ihm()

        return r

    def build_image(self):
        # l'image complète de l'IHM
        p_min = P
        if P < 4:
            p_min = 4

        # taille de la zone des lignes de jeu
        lignes_width = p_min * (self.position_width + self.padding)
        lignes_height = self.lignes * self.ligne_height

        if self.info_width > lignes_width:
            lignes_width = self.info_width

        # taille avec la zone d'aide
        help_lignes_width = self.padding + self.help_width + self.padding + lignes_width
        help_lignes_height = self.help_height
        if lignes_height > self.help_height:
            help_lignes_height = lignes_height
        help_lignes_height += self.padding

        self.frame_position = help_lignes_width

        # taille totale
        full_width = help_lignes_width + self.ocr.width + self.padding

        full_height = self.ocr.height
        if help_lignes_height > full_height: full_height = help_lignes_height
        full_height += 2*self.padding

        self.image = np.zeros((full_height, full_width, 3), dtype=np.uint8)

    def draw_help(self):
        x1 = self.padding
        y1 = self.padding
        cv2.rectangle(self.image, (x1, y1), (self.help_width, self.help_height), cyan, -1)

        y = y1 + 16
        for h in self.help_lines:
            cv2.putText(self.image,
                        text=h,
                        org=(x1 + 5, y),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.5,
                        color=red,
                        thickness=1,
                        lineType=cv2.LINE_AA)
            y += 20

    def draw_lignes(self, current_position):
        # print("draw_lignes. Position=", current_position, "lignes=", self.lignes, "info=", self.info)
        p_min = P
        if P < 4:
            p_min = 4

        y = self.padding
        # on affiche successivement toutes les tentatives de combinaisons
        for ligne, jeu in enumerate(self.jeux):
            x1 = self.help_width + self.padding
            y1 = y
            labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
            for position in range(P):
                x2 = x1 + self.position_width
                y2 = y1 + self.position_height
                # Dessiner les zones sur l'image
                # la couleur change pour la zone en cours
                color_fond = green
                color_char = red
                if ligne == (self.lignes - 1):
                    jeu.set_time()
                    if position == current_position:
                        color_fond = red
                        color_char = white

                # print("draw_ihm. i=", i, x1, y1, x2, y2)
                cv2.rectangle(self.image, (x1, y1), (x2, y2), color_fond, -1)

                cv2.putText(self.image,
                            text=labels[position],
                            org=(x1 + 10, y1 + int(self.position_height * 0.3)),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=0.6,
                            color=white,
                            thickness=2,
                            lineType=cv2.LINE_AA)

                j = jeu.jeu[position]

                # print("draw_ihm. position=", position, i, "jeu=", j)
                if j > 0:
                    cv2.putText(self.image,
                                text=f"{j}",
                                org=(x1 + 30, y1 + int(self.position_height * 0.8)),
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale=1.8,
                                color=color_char,
                                thickness=2,
                                lineType=cv2.LINE_AA)

                x1 += self.position_width + self.padding

            x1 = self.help_width + self.padding
            y1 = y + self.position_height + self.padding

            x2 = x1 + self.info_width - self.padding
            y2 = y1 + self.info_height
            c = white

            now = int(jeu.t - self.t0)
            minutes = int(now / 60)
            secondes = now % 60
            cv2.rectangle(self.image, (x1, y1), (x2, y2), c, -1)  # Carré 1 (bleu)
            cv2.putText(self.image,
                        text="(" + self.camera_tag + ") " + jeu.info + f" {minutes}m{secondes}s",
                        org=(x1 + 10, y1 + 18),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.6,
                        color=red,
                        thickness=1,
                        lineType=cv2.LINE_AA)

            y += self.ligne_height

    def draw_frame(self):
        p_min = P
        if P < 4:
            p_min = 4

        if self.frame is not None:
            # print(self.frame.shape)
            x1 = self.frame_position
            y1 = self.padding

            self.image[y1:y1 + self.ocr.height, x1:x1 + self.ocr.width] = self.frame

            text = "p({})={:5.2f}".format(str(self.chiffre), self.proba)

            cv2.putText(self.image,
                        text=text,
                        org=(x1 + 10, y1 + 18),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.6,
                        color=red,
                        thickness=1,
                        lineType=cv2.LINE_AA)


    # Fonction pour dessiner l'IHM
    def draw_ihm(self, current_position=-1):
        # print("draw_ihm. Position=", current_position, "lignes=", self.lignes, "info=", self.info)

        """
             ---
             ppp ppp ppp  image
             info
             ---
             ppp ppp ppp
             info
             ---
        """


        y = 0

        self.build_image()
        self.draw_help()
        self.draw_lignes(current_position)
        self.draw_frame()

        # Afficher l'image
        cv2.imshow('MasterMind', self.image)

    def valid(self, essai):
        jeu = self.jeu_courant()
        if jeu.position >= 0:
            for p in range(P):
                k = jeu.jeu[p]
                # print("valid> p=", p, "k=", k, "pos=", jeu.position, "essai=", essai)
                if p != jeu.position:
                    if essai == k:
                        # print("valid> False")
                        return False

        # print("valid> True")
        return True

    def process_frame(self):
        def contains_integer(text):
            try:
                int(text)
                return True
            except ValueError:
                return False

        result, self.frame = self.ocr.read()
        jeu = self.jeu_courant()

        self.draw_ihm(jeu.position)

        if jeu.position == -1:
            jeu.info = f"choisis une position"
        else:
            jeu.info = f"choisis un chiffre (1..{N})"

        if result is None:
            jeu.info = f"pas d'image"
            self.draw_ihm(jeu.position)
        else:
            condition = ""
            for (bbox, text, prob) in result:
                if prob > 0.5 and contains_integer(text):
                    t = int(text)
                    if t > 0 and t <= N:
                        # print("t=", t, "position=", jeu.position, "jeu=", jeu)
                        if jeu.position >= 0:
                            if self.valid(t):
                                jeu.jeu[jeu.position] = t
                                # print("process_frame. position=", self.position, "jeu=", jeu)
                                jeu.info = f"chiffre {t} choisi"
                            else:
                                jeu.info = f"doublons interdits ({t})"
                        self.proba = prob
                        self.chiffre = t
                        self.draw_ihm(jeu.position)

                    break

    def run(self):
        global mode_camera

        while True:
            # Traitement de l'image pour détecter les chiffres et les reconnaître
            self.process_frame()

            # détection des touches du clavier
            k = cv2.waitKey(1) & 0xFF
            if k != 255:
                # print("k=", k)
                pass
            if k == ord('Q') or k == ord('q'):
                # quit
                break

            zone = -1
            if k == ord('a') or k == ord('A'):
                zone = 0
            elif k == ord('b') or k == ord('B'):
                zone = 1
            elif k == ord('c') or k == ord('C'):
                zone = 2
            elif k == ord('d') or k == ord('D'):
                zone = 3
            elif k == ord('i') or k == ord('I'):
                # internal camera
                mode_camera = internal_mode
            elif k == ord('r') or k == ord('R'):
                # robot
                mode_camera = robot_mode
            elif k == ord('n') or k == ord('N'):
                self.restart()
            elif k == ord('X') or k == ord('x'):
                print(self.secret)
            elif k == 13:
                # enter => valider une combinaison
                zone = 4

            jeu = self.jeu_courant()

            if zone >= 0 and zone <= P:
                # print("zone=", zone)
                jeu.position = zone
                self.draw_ihm(zone)
            elif zone == 4:
                # on teste la combinaison
                ok = self.result()
                if not ok:
                    self.lignes += 1
                    self.jeux.append(Jeu())
                    self.draw_ihm()

        cv2.destroyAllWindows()


def main():
    cv_game = MastermindCV()
    cv_game.run()

if __name__ == "__main__":
    main()
