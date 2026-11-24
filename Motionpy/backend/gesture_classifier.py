# MotionPy/backend/gesture_classifier.py - IMPORTS CORRETOS
import cv2
import numpy as np
import tensorflow as tf
import os
import mediapipe as mp
import sys
import os

# Adicionar o diretório atual ao path para importar hand_detector
sys.path.append(os.path.dirname(__file__))

try:
    from hand_detector import LibrasDetector
    print("hand_detector importado com sucesso!")
except ImportError as e:
    print(f"Erro ao importar hand_detector: {e}")
    # Tentar import absoluto
    try:
        from MotionPy.backend.hand_detector import LibrasDetector
        print("hand_detector importado com caminho absoluto!")
    except ImportError:
        print("Não foi possível importar hand_detector")
        exit()

# O RESTO DO CÓDIGO PERMANECE IGUAL...
class LibrasGestureClassifier:
    def __init__(self, model_path='MotionPy/backend/modelos/keras_model.h5', 
                 labels_path='MotionPy/backend/modelos/labels.txt'):
        self.model_path = model_path
        self.labels_path = labels_path
        self.model = None
        self.labels = []
        self.gesture_history = []
        self.hand_detector = LibrasDetector()
        
        # Configuração MediaPipe para bounding box
        self.mp_hands = mp.solutions.hands
        self.hands_bbox = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        self.load_model()
    
    # ... resto da classe permanece igual
    
    def load_model(self):
        """Carrega o modelo do Teachable Machine"""
        try:
            if not os.path.exists(self.model_path):
                print(f"Modelo não encontrado: {self.model_path}")
                return False
            
            self.model = tf.keras.models.load_model(self.model_path, compile=False)
            
            # Carregar labels
            if os.path.exists(self.labels_path):
                with open(self.labels_path, 'r', encoding='utf-8') as f:
                    self.labels = [line.strip().split(' ')[1] for line in f.readlines()]
            else:
                self.labels = ['A', 'B', 'C', 'Oi', 'Casa']
            
            print(f"Modelo carregado! Classes: {self.labels}")
            return True
            
        except Exception as e:
            print(f"Erro ao carregar modelo: {e}")
            return False
    
    def classify_gesture(self, frame):
        """Classifica gesto a partir do frame completo"""
        if self.model is None:
            return "Modelo não carregado", 0.0, frame
        
        try:
            # Primeiro detecta mãos e conta dedos (usando SEU detector)
            features, processed_frame = self.hand_detector.extract_hand_features(frame)
            finger_count = features[0] if features else 0
            
            # Configurar para bounding box precisa
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands_bbox.process(frame_rgb)
            
            h, w, _ = frame.shape
            predicted_letter = "?"
            confidence = 0.0
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Calcular bounding box
                    x_coords = [lm.x * w for lm in hand_landmarks.landmark]
                    y_coords = [lm.y * h for lm in hand_landmarks.landmark]
                    
                    x_min, x_max = int(min(x_coords)), int(max(x_coords))
                    y_min, y_max = int(min(y_coords)), int(max(y_coords))
                    
                    margin = 50
                    x_min = max(0, x_min - margin)
                    y_min = max(0, y_min - margin)
                    x_max = min(w, x_max + margin)
                    y_max = min(h, y_max + margin)
                    
                    # Recortar e processar mão
                    hand_roi = frame[y_min:y_max, x_min:x_max]
                    
                    if hand_roi.size > 0:
                        # Pré-processamento para Teachable Machine
                        hand_resized = cv2.resize(hand_roi, (224, 224))
                        normalized = (hand_resized.astype(np.float32) / 127.0) - 1
                        
                        # Predição
                        prediction = self.model.predict(np.array([normalized]), verbose=0)
                        index = np.argmax(prediction)
                        confidence = np.max(prediction)
                        predicted_letter = self.labels[index]
                        
                        # Desenhar bounding box verde
                        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 3)
                        
                        # Mostrar predição perto da mão
                        status_text = f"{predicted_letter} ({confidence:.2f})"
                        text_color = (0, 255, 0) if confidence > 0.7 else (0, 255, 255)
                        
                        # Fundo para texto
                        text_width = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0][0]
                        cv2.rectangle(frame, (x_min, y_min-40), (x_min + text_width + 10, y_min), (0, 0, 0), -1)
                        cv2.putText(frame, status_text, (x_min, y_min-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
            
            # Suavizar predição
            smoothed_letter, smoothed_confidence = self.smooth_prediction(predicted_letter, confidence)
            
            # Adicionar informações ao frame usando SEU detector
            final_frame = self.hand_detector.draw_hand_info(
                processed_frame, 
                finger_count, 
                smoothed_letter
            )
            
            return smoothed_letter, smoothed_confidence, final_frame
            
        except Exception as e:
            print(f"Erro na classificação: {e}")
            return "Erro", 0.0, frame
    
    def smooth_prediction(self, current_letter, current_confidence, history_length=5):
        """Suaviza as predições usando histórico"""
        self.gesture_history.append((current_letter, current_confidence))
        
        if len(self.gesture_history) > history_length:
            self.gesture_history.pop(0)
        
        if self.gesture_history:
            letters = [letter for letter, conf in self.gesture_history]
            best_letter = max(set(letters), key=letters.count)
            
            confidences = [conf for letter, conf in self.gesture_history if letter == best_letter]
            avg_confidence = sum(confidences) / len(confidences) if confidences else current_confidence
            
            return best_letter, avg_confidence
        
        return current_letter, current_confidence
    
    def get_gesture_info(self, letter):
        """Retorna informações sobre o gesto"""
        gesture_info = {
            'A': "Mão fechada em punho com o polegar ao lado",
            'B': "Mão aberta com dedos estendidos e o polegar cruzado", 
            'C': "Mão em forma de C curvada",
            'Oi': "Mão em formato de O e o dedo mindinho levantando",
            'Casa': "Mão em formato de telhado"
        }
        return gesture_info.get(letter, "Gesto não reconhecido")
    
    def release(self):
        """Libera recursos"""
        if hasattr(self, 'hand_detector') and self.hand_detector:
            self.hand_detector.release()
        if hasattr(self, 'hands_bbox'):
            self.hands_bbox.close()

def create_classifier():
    """Cria e retorna uma instância do classificador"""
    return LibrasGestureClassifier()

