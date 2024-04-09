import sys
import random
import cv2
import numpy as np
import easyocr
import requests
import time
import socket

N = 3
P = 2
max_lignes = 8

internal_mode = 0
robot_mode = 1
mode_camera = robot_mode


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
        self.reader = easyocr.Reader(['fr'],  model_storage_directory="./models")
        self.count = 0
        self.set_camera_mode(mode_camera)

    def set_camera_mode(self, mode):
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
            # self.fd.write('      fin de boucle {:6.3f}\r\n'.format(perf_counter() - self.t))
            # self.fd.write('image {}\r\n'.format(self.count))
            # self.t = perf_counter()
            # print(f"sendto> {self.addr_port} {self.color}")
            self.s.sendto(self.color, self.addr_port)
            buf = self.s.recvfrom(50000)
            # self.fd.write('     received {:6.3f}\r\n'.format(perf_counter() - self.t))
            # self.count += 1
            raw_img = np.asarray(bytearray(buf[0]), dtype=np.uint8)
            frame = cv2.imdecode(raw_img, cv2.IMREAD_COLOR)
            return frame

            # frame = cv2.imdecode(raw_img, cv2.IMREAD_COLOR)
            # self.fd.write('     decoded {:6.3f}\r\n'.format(perf_counter() - self.t))
            # res = self.reader.readtext(frame)
            # self.fd.write('     processed {:6.3f}\r\n'.format(perf_counter() - self.t))
            # print('image ', self.count)
            # return res, frame
        except:          # timeout de réception de l'image
            # self.fd.write('     no image {:6.3f}\r\n'.format(perf_counter()-self.t))
            self.s.sendto(self.color, self.addr_port)
            return None

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


class MastermindCV(OCR):
    def __init__(self):
        super().__init__()
        self.frame = None

        # Créer une fenêtre OpenCV
        cv2.namedWindow('ANUMBY - MasterMind')
        cv2.setMouseCallback('ANUMBY - MasterMind', self.mouse)

        # Définir les valeurs possibles
        self.valeurs = [i for i in range(1, N + 1)]
        self.info_start = "Choisis une position"

        self.proba = 0
        self.chiffre = 0

        self.show_secret = False

        #-------------------------------------------------

        self.padding = 10

        self.help_lines = [
            f"1... : position",
            "Enter : selection",
            "X : solution",
            "",
            "F : facile (2/3)",
            "D : difficile (3/5)",
            "T : tres difficile (6/6)",
            "",
            "I : camera interne",
            "R : camera robot",
            "N : nouveau jeu",
            "Q : quit",
        ]

        self.position_width = 70
        self.position_height = 50

        self.help_width = 180

        (width, height), baseline = cv2.getTextSize("",
                                                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                                    fontScale=0.5,
                                                    thickness=1)

        self.help_height = (len(self.help_lines) + 1) * (height + baseline + 2)

        # zone d'information
        self.info_width = 370
        self.info_height = int(self.position_height * 0.5)

        self.secret_width = self.help_width
        self.secret_height = self.info_height

        # chaque ligne de jeu
        self.ligne_height = self.position_height + self.padding + self.info_height + self.padding

        if mode_camera == internal_mode:
            self.camera_tag = "I"
        else:
            self.camera_tag = "R"

        self.frame_position = 0

        self.title_width = 300
        self.title_height = 40

        self.title =  'ANUMBY - MasterMind'

        self.mouse_x1 = 0
        self.mouse_y1 = 0
        self.mouse_x2 = 0
        self.mouse_y2 = 0

        self.mode_difficulty('F')

        # -------------------------------------------------

        self.restart()

    def draw_help_line(self, help_line):
        lignes = len(self.help_lines)
        h = int(self.help_height / lignes)

        h_left = self.padding
        h_right = h_left + self.help_width
        h_top = self.padding + self.title_height + self.padding
        h_bottom = h_top + self.help_height

        self.mouse_x1 = h_left
        self.mouse_y1 = h_top + help_line * h
        self.mouse_x2 = self.mouse_x1 + self.help_width
        self.mouse_y2 = self.mouse_y1 + h

    def mode_difficulty(self, difficulty='F'):
        global N, P, max_lignes

        if difficulty == 'F':
            N = 3
            P = 2
            max_lignes = P * 2
        elif difficulty == 'D':
            N = 6
            P = 3
            max_lignes = P * 2
            self.restart()
        elif difficulty == 'T':
            N = 6
            P = 6
            max_lignes = P * 2
            self.restart()
        self.restart()

    def action(self, commande):
        global N, P, max_lignes
        global mode_camera

        zones = ['1', '2', '3', '4', '5', '6', '7', '8']

        lignes = len(self.help_lines)
        h = int(self.help_height / lignes)

        zone = -1

        # print(f"action> {commande}")

        if commande == 'Q':
            help_line = 11
            return
        elif commande in zones:
            help_line = 0
            zone = zones.index(commande)
        elif commande == 'I':
            help_line = 8
            mode_camera = internal_mode
            self.set_camera_mode(mode_camera)
        elif commande == 'R':
            help_line = 9
            mode_camera = robot_mode
            self.set_camera_mode(mode_camera)
        elif commande == 'N':
            help_line = 10
            self.restart()
        elif commande == 'X':
            help_line = 2
            self.show_secret = not self.show_secret
        elif commande == 'F':
            help_line = 4
            self.mode_difficulty('F')
        elif commande == 'D':
            help_line = 5
            self.mode_difficulty('D')
        elif commande == 'T':
            help_line = 6
            self.mode_difficulty('T')
        elif commande == 'Z':
            # enter => valider une combinaison
            help_line = 1
            zone = 4

        self.draw_help_line(help_line)
        jeu = self.jeu_courant()

        if zone >= 0 and zone <= P:
            # print("zone=", zone)
            jeu.position = zone
            self.draw_ihm(zone)
        elif zone == 4:
            # on teste la combinaison
            ok = self.result()
            if not ok:
                old = self.jeu_courant()
                if self.lignes >= max_lignes:
                    old.info = "Perdu! trop d'essais"
                else:
                    self.lignes += 1
                    self.jeux.append(Jeu())
                    jeu = self.jeu_courant()
                    jeu.jeu = [k for k in old.jeu]

                self.draw_ihm()

    def mouse(self, event, x, y, flags, param):

        # pour détecter un click dans la zone help
        h_left = self.padding
        h_right = h_left + self.help_width
        h_top = self.padding + self.title_height + self.padding
        h_bottom = h_top + self.help_height

        # pour détecter un click dans la zone des pavés
        p_left = self.padding + self.help_width + self.padding
        p_right = p_left + P*(self.position_width + self.padding)
        p_top = self.padding + self.title_height + self.padding
        p_bottom = h_top + self.position_height

        if event == cv2.EVENT_LBUTTONUP:
            if x > h_left and x < h_right and y > h_top and y < h_bottom:
                # on a clické dans la zone help
                # print("help")
                lignes = len(self.help_lines)
                h = int(self.help_height / lignes) # hauteur d'une ligne de help

                help_line = int((y - h_top) / h)

                self.mouse_x1 = h_left
                self.mouse_y1 = h_top + help_line*h
                self.mouse_x2 = self.mouse_x1 + self.help_width
                self.mouse_y2 = self.mouse_y1 + h

                if help_line == 0:
                    # 1..P
                    pass
                if help_line == 1:
                    # enter
                    self.action('Z')
                if help_line == 2:
                    # X
                    self.action('X')
                if help_line == 3:
                    # none
                    pass
                if help_line == 4:
                    # F
                    self.action('F')
                if help_line == 5:
                    # M
                    self.action('D')
                if help_line == 6:
                    # T
                    self.action('T')
                if help_line == 7:
                    # none
                    pass
                if help_line == 8:
                    # I
                    self.action('I')
                if help_line == 9:
                    # R
                    self.action('R')
                if help_line == 10:
                    # N
                    self.action('N')
                if help_line == 11:
                    # Q
                    self.action('Q')

            elif x > p_left and x < p_right and y > p_top and y < p_bottom:
                positions_width = P * (self.position_width + self.padding)
                w = self.position_width + self.padding # largeur d'une position
                position = int((x - p_left) / w) + 1
                # print(f"positions> {position}")
                self.action(f'{position}')

            jeu = self.jeu_courant()
            self.draw_ihm(jeu.position)

        """
        if event == cv2.EVENT_LBUTTONUP:
            print(f"mouse UP {x} {y} {flags} {param}")
        elif event == cv2.EVENT_LBUTTONDOWN:
            print(f"mouse DOWN {x} {y} {flags} {param}")
        else:
            print(f"mouse {event} {x} {y} {flags} {param}")
        """

    def restart(self):

        self.valeurs = [i for i in range(1, N + 1)]

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
        self.box = None

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
            jeu.info = f"Bravo c'est gagne!!!"
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

        # print(f"build_image> w={self.width} h={self.height}")

        # taille totale
        self.full_width = help_lignes_width + self.width + self.padding

        self.padding_title = self.padding + self.title_height + self.padding
        self.full_height = self.padding_title + self.height
        if (self.padding_title + help_lignes_height) > self.full_height: self.full_height = self.padding_title + help_lignes_height
        self.full_height += 2*self.padding

        self.image = np.zeros((self.full_height, self.full_width, 3), dtype=np.uint8)

    def draw_title(self):
        x1 = self.padding
        y1 = self.padding
        cv2.rectangle(self.image, (x1, y1), (x1 + self.full_width - 2*self.padding, y1 + self.title_height), yellow, -1)

        (width, height), baseline = cv2.getTextSize(self.title,
                                                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                                    fontScale=1.4,
                                                    thickness=2)

        # print(f"draw_title> {width} {height} {baseline}")

        cv2.putText(self.image,
                    text=self.title,
                    org=(x1 + int(self.full_width/2 - width/2), y1 + int(self.title_height/2 + height/2)),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1.4,
                    color=red,
                    thickness=2,
                    lineType=cv2.LINE_AA)

    def draw_help(self):
        x1 = self.padding
        y1 = self.padding_title
        cv2.rectangle(self.image, (x1, y1), (x1 + self.help_width, y1 + self.help_height), cyan, -1)

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

        cv2.rectangle(self.image,
                      (self.mouse_x1, self.mouse_y1),
                      (self.mouse_x2, self.mouse_y2), red, 2)

    def draw_secret(self):
        x1 = self.padding
        y1 = self.padding + self.title_height + self.padding + self.help_height + self.padding

        cv2.rectangle(self.image, (x1, y1), (x1 + self.secret_width, y1 + self.secret_height), magenta, -1)

        if self.show_secret:
            cv2.putText(self.image,
                        text=f"secret={self.secret}",
                        org=(x1 + 10, y1 + 18),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.6,
                        color=white,
                        thickness=1,
                        lineType=cv2.LINE_AA)

    def draw_lignes(self, current_position):
        # print("draw_lignes. Position=", current_position, "lignes=", self.lignes, "info=", self.info)
        p_min = P
        if P < 4:
            p_min = 4

        y = self.padding_title
        # on affiche successivement toutes les tentatives de combinaisons
        for ligne, jeu in enumerate(self.jeux):
            x1 = self.padding + self.help_width + self.padding
            y1 = y
            labels = ['1', '2', '3', '4', '5', '6', '7', '8']
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

            x1 = self.padding + self.help_width + self.padding
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
            y1 = self.padding_title

            # print(self.frame.shape)

            self.image[y1:y1 + self.height, x1:x1 + self.width] = self.frame

            if self.chiffre == 0:
                text = "aucune detection"
            else:
                text = "p({})={:5.2f}".format(str(self.chiffre), self.proba)

                if not self.box is None:
                    (px1, py1) = self.box[0]
                    (px2, py2) = self.box[2]
                    cv2.rectangle(self.image, (px1 + x1, py1 + y1), (px2 + x1, py2 + y1), red, 1)

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
        self.draw_title()
        self.draw_help()
        self.draw_secret()
        self.draw_lignes(current_position)
        self.draw_frame()

        # Afficher l'image
        cv2.imshow('ANUMBY - MasterMind', self.image)

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

        result, self.frame = self.read()
        jeu = self.jeu_courant()

        self.draw_ihm(jeu.position)

        if self.lignes >= max_lignes:
            jeu.info = "Perdu! trop d'essais"
            self.draw_ihm(jeu.position)
            return

        if jeu.position == -1:
            jeu.info = f"choisis une position"
        else:
            jeu.info = f"choisis un chiffre (1..{N})"

        if result is None:
            jeu.info = f"pas d'image"
            self.draw_ihm(jeu.position)
            return

        self.proba = 0
        self.chiffre = 0
        self.box = None
        for (bbox, text, prob) in result:
            if prob > 0.8 and contains_integer(text):
                t = int(text)
                if t > 0 and t <= N:
                    # print("t=", t, "position=", jeu.position, "jeu=", jeu)
                    if jeu.position >= 0:
                        if self.valid(t):
                            jeu.jeu[jeu.position] = t
                            # print("process_frame. position=", self.position, "jeu=", jeu)
                            jeu.info = f"chiffre {t} choisi"
                            self.proba = prob
                            self.chiffre = t
                            self.box = bbox
                        else:
                            jeu.info = f"doublons interdits ({t})"
                break

        self.draw_ihm(jeu.position)

        # Mise à jour de la coulur nopixel
        if self.chiffre > 0:
            if self.proba > 0.8:
                self.color = b'GREEN'
                # self.s.sendto(b'GREEN', self.addr_port)
            else:
                self.color = b'BLUE'
                # self.s.sendto(b'BLUE', self.addr_port)
        else:
            self.color = b'RED'
            # self.s.sendto(b'RED', self.addr_port)

        # print(f"process_frame> {self.color}")

    def run(self):
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
                self.action('Q')
                break

            zone = -1
            if k == ord('1'):
                self.action('1')
            elif k == ord('2'):
                self.action('2')
            elif k == ord('3'):
                self.action('3')
            elif k == ord('4'):
                self.action('4')
            elif k == ord('5'):
                self.action('5')
            elif k == ord('6'):
                self.action('6')
            elif k == ord('7'):
                self.action('7')
            elif k == ord('8'):
                self.action('8')
            elif k == ord('i') or k == ord('I'):
                # internal camera
                self.action('I')
            elif k == ord('r') or k == ord('R'):
                # robot
                self.action('R')
            elif k == ord('n') or k == ord('N'):
                self.action('N')
            elif k == ord('X') or k == ord('x'):
                self.action('X')
            elif k == ord('F') or k == ord('f'):
                self.action('F')
            elif k == ord('D') or k == ord('d'):
                self.action('D')
            elif k == ord('T') or k == ord('t'):
                self.action('T')
            elif k == 13:
                self.action('Z')

        cv2.destroyAllWindows()


def main():
    cv_game = MastermindCV()
    cv_game.run()

if __name__ == "__main__":
    main()
