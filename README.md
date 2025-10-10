
````markdown
# Crypto Trading Bot AI-Assisted

Questo progetto è un **bot di trading simulato per criptovalute** che utilizza indicatori tecnici (RSI, MACD, SMA) per generare segnali di acquisto e vendita. Il bot invia notifiche su Telegram e tiene traccia delle operazioni in un file CSV.

---

## Funzionalità principali

1. **Simulazione trading**
   - Compra e vendi BTC/USDT basandosi sui segnali generati dagli indicatori tecnici.
   - Mantiene il saldo simulato in USDT e BTC.
   - Supporta un sistema di stop loss e take profit configurabile.

2. **Indicatori tecnici**
   - **RSI (Relative Strength Index)**: per identificare ipercomprato/ipervenduto.
   - **MACD (Moving Average Convergence Divergence)**: per rilevare inversioni di tendenza.
   - **SMA (Simple Moving Average)**: per determinare la direzione del trend.

3. **Notifiche Telegram**
   - Invia notifiche su ogni operazione simulata (BUY, SELL, chiusura trade).
   - Richiede di configurare `TELEGRAM_TOKEN` e `TELEGRAM_CHAT_ID` in un file `.env`.

4. **Gestione trade**
   - Simula apertura e chiusura delle posizioni.
   - Calcola il profit/loss percentuale (PnL).
   - Salva lo storico delle operazioni in `trades.csv`.

5. **Configurazione personalizzabile**
   - Paio di trading (`SYMBOL`), timeframe, quantità di trade (`TRADE_AMOUNT`).
   - Parametri degli indicatori (`RSI_PERIOD`, `SMA_PERIOD`).
   - Stop loss e take profit (`STOP_LOSS_PCT`, `TAKE_PROFIT_PCT`).

---

## Requisiti

- Python 3.8+
- Librerie Python:
  ```bash
  pip install ccxt pandas ta requests python-dotenv
````

---

## Configurazione

1. Crea un file `.env` nella root del progetto con i tuoi token Telegram:

   ```env
   TELEGRAM_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

2. Modifica i parametri di configurazione nel file principale (`SYMBOL`, `TIMEFRAME`, ecc.) se necessario.

---

## Avvio del bot

Esegui il bot con:

```bash
python main.py
```

Il bot girerà in **modalità simulata**, generando segnali e notifiche Telegram ogni ora.

---

## Avvertenze

* Questo bot **non esegue ordini reali** sul mercato. È solo a scopo educativo e di testing.
* Non condividere il tuo file `.env` pubblicamente, contiene credenziali sensibili.
* Testare sempre strategie di trading in modalità simulata prima di operare con fondi reali.

---

## Output

* **Console**: stampa dei segnali e dello stato del saldo.
* **CSV**: `trades.csv` con storico delle operazioni.

---

## Autore

Omarinho12345

```

---
Vuoi che faccia quella versione?
```
