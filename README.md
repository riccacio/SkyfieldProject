# Progetto di Tesi Triennale in Ingegneria Informatica  
## Analisi di strategie di instradamento di flussi dati su costellazioni satellitari LEO

### Descrizione

Questo progetto è un **simulatore** che utilizza i dati **TLE** dei satelliti Starlink per simulare una connessione tra più città, date le loro coordinate geodetiche.  
Il simulatore calcola i percorsi minimi tra i satelliti che i pacchetti devono attraversare per comunicare tra due città.  
Successivamente, misura la distanza totale di ogni percorso e la latenza, salvando i risultati in file CSV e generando i relativi grafici per l’analisi.

### Test effettuati

1. **Impatto del range laser**  
   Si analizza come la variazione del range laser tra i satelliti influisce sulla latenza. Vengono confrontati:
   - Due algoritmi di routing:
     - **Dijkstra** (peso = distanza)
     - **MinHop** (basato sul numero minimo di salti)
   - Due topologie di collegamento:
     - **+Grid** (Ogni satellite può avere fino a 4 collegamenti, due con quelli dello stesso piano orbitale, due con quelli dei piani subito adiacenti)
     - **Libera** (ogni satellite comunica con tutti quelli entro un certo range espresso in km)

2. **Confronto RTT satellitare vs terrestre**  
   In questo test, il range laser viene fissato e si variano le città di destinazione. Si confronta:
   - L’**RTT satellitare simulato** con l’**RTT terrestre misurato**
   - L’RTT simulato con un **dataset pubblicato dall'Università di Vancouver** per determinare la topologia più realistica

### Tecnologie utilizzate
- Linguaggio: **Python**
- IDE: **PyCharm 2023.3.4**
- Sistema operativo di sviluppo: **macOS**

> ⚠️ Nota: Il codice è stato sviluppato su macOS. Se utilizzato su Windows o altri sistemi operativi, potrebbe essere necessario apportare alcune modifiche.

---

## Come scaricare e avviare il progetto

1. **Clona il repository**
   ```bash
   git clone https://github.com/riccacio/SkyfieldProject.git
   cd SkyfieldProject

2. **Installa le dipendenze**
   ```bash
   pip install -r requirements.txt
   
3. **Avvia il programma**
   ```bash
   python main.py
   
**Autore**   
[![Author](https://img.shields.io/badge/Author-Riccardo%20Pacini-blue)](https://github.com/riccacio)

Sviluppato da **Riccardo Pacini**
📧 Email: riccardopacini0711@gmail.com
📅 Anno: 2025
