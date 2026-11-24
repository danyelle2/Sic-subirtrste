#SÓ DETECTA MÃO E POSIÇÃO DOS DEDOS

import cv2
import mediapipe as mp
import numpy as np

class LibrasDetector:
    """Classe especializada apenas na detecção de mãos"""
    def __init__(self):
        try:
            self.mp_hands = mp.solutions.hands
            self.mp_drawing = mp.solutions.drawing_utils
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            )
        except ImportError:
            print("MediaPipe não instalado. Instale com: pip install mediapipe")
            self.hands = None
    
    def extract_hand_features(self, frame):
        """Extrai características das mãos do frame"""
        if self.hands is None:
            return [], frame
            
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)
            
            total_fingers = 0
            hands_detected = 0
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Desenha os landmarks
                    self.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Calcula contagem de dedos para CADA mão
                    fingers_up = self.count_fingers(hand_landmarks)
                    total_fingers += fingers_up
                    hands_detected += 1
                
                return [total_fingers], frame
            
            return [], frame
            
        except Exception as e:
            print(f"Erro na extração: {e}")
            return [], frame
    
    def count_fingers(self, landmarks):
        """Conta quantos dedos estão levantados em uma mão"""
        try:
            finger_tips = [8, 12, 16, 20]
            finger_pips = [6, 10, 14, 18]
            
            count = 0
            
            # Verifica dedos (exceto polegar)
            for tip, pip in zip(finger_tips, finger_pips):
                if landmarks.landmark[tip].y < landmarks.landmark[pip].y:
                    count += 1
            
            # Verifica polegar
            thumb_tip = landmarks.landmark[4]
            thumb_ip = landmarks.landmark[3]
            if thumb_tip.x < thumb_ip.x:
                count += 1
            
            return count
            
        except Exception as e:
            print(f"Erro na contagem de dedos: {e}")
            return 0
    
    def draw_hand_info(self, frame, fingers_count, letter):
        """Desenha informações da mão no frame com fundo preto"""
        # Fundo preto para "Dedos: X"
        cv2.rectangle(frame, (5, 5), (180, 35), (0, 0, 0), -1)
        cv2.putText(frame, f"Dedos: {fingers_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Fundo preto para "Letra: X"
        cv2.rectangle(frame, (5, 40), (180, 70), (0, 0, 0), -1)
        cv2.putText(frame, f"Letra: {letter}", (10, 65), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
    
    def release(self):
        """Libera recursos"""
        if hasattr(self, 'hands') and self.hands:
            self.hands.close()