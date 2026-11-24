# main.py - CAMINHOS ABSOLUTOS CORRETOS
import cv2
import os
import sys
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env local
load_dotenv()

# Pega a chave de forma segura
api_key = os.getenv("GCP_API_KEY")

# Adicionar caminho para backend (relativo a ESTE arquivo)
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

try:
    from backend.gesture_classifier import create_classifier
    print("✅ gesture_classifier importado com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar gesture_classifier: {e}")
    exit()

def main():
    print("🚀 MotionPy - Reconhecimento de Libras")
    print("=" * 50)
    
    # CAMINHOS CORRETOS - relativos à localização deste arquivo
    model_path = os.path.join(os.path.dirname(__file__), 'backend', 'modelos', 'keras_model.h5')
    labels_path = os.path.join(os.path.dirname(__file__), 'backend', 'modelos', 'labels.txt')
    
    print(f"🔍 Procurando modelo em: {model_path}")
    
    if not os.path.exists(model_path):
        print("❌ Modelo não encontrado!")
        print("📁 Estrutura de pastas:")
        
        # Verificar o que existe
        backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
        if os.path.exists(backend_dir):
            print("✅ Pasta backend existe")
            for item in os.listdir(backend_dir):
                item_path = os.path.join(backend_dir, item)
                if os.path.isdir(item_path):
                    print(f"   📁 {item}/")
                    for subitem in os.listdir(item_path):
                        print(f"      📄 {subitem}")
                else:
                    print(f"   📄 {item}")
        else:
            print("❌ Pasta backend não existe!")
        return
    
    print("✅ Modelo encontrado!")
    print("📋 Iniciando reconhecimento...")
    print("⏹️  Pressione Q para sair")

    
    
    # Criar classificador
    classifier = create_classifier()
    
    # Inicializar câmera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Câmera não encontrada!")
        return
    
    print("✅ Câmera inicializada!")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Erro ao capturar frame")
                break
            
            frame = cv2.flip(frame, 1)
            letter, confidence, processed_frame = classifier.classify_gesture(frame)
            
            cv2.imshow('MotionPy - Reconhecimento de Libras', processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        classifier.release()
        print("✅ Programa encerrado!")

if __name__ == "__main__":
    main()