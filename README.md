# MAADBproject

## Generazione dei Dati

I dati utilizzati in questo progetto sono generati utilizzando il generatore ufficiale di dataset LDBC Social Network Benchmark (SNB). È possibile generare i dati seguendo le istruzioni riportate nel repository ufficiale disponibile al seguente link:

🔗 [https://github.com/ldbc/ldbc\_snb\_datagen\_spark](https://github.com/ldbc/ldbc_snb_datagen_spark)

Assicurarsi di generare correttamente le cartelle `dynamic` e `static`, che dovranno poi essere posizionate nella directory `data` come indicato nella sezione di configurazione.

Questo progetto richiede una configurazione specifica dei dati e utilizza Docker per la containerizzazione. Si prega di seguire attentamente le istruzioni riportate di seguito per eseguirlo correttamente.

## Istruzioni per la Configurazione

1. **Clonare il Repository:**

   ```bash
   git clone <repository_url>
   cd MAADBproject
   ```

2. **Creare la Cartella dei Dati:**
   Nella directory principale del progetto, creare una cartella denominata `data`:

   ```bash
   mkdir data
   ```

3. **Copiare le Cartelle del Dataset:**
   Copiare le cartelle `dynamic` e `static` del dataset all'interno della cartella `data` appena creata. La struttura del progetto dovrebbe apparire come segue:

   ```
   MAADBproject/
   ├── data/
   │   ├── dynamic/
   │   └── static/
   ├── ... (altri file del progetto)
   ```

   In alternativa, se si preferisce non copiare le cartelle, assicurarsi che i percorsi ai dataset `dynamic` e `static` siano correttamente configurati nei file di configurazione del progetto.

## Esecuzione del Progetto con Docker

1. **Costruire l’Immagine Docker:**
   Portarsi nella directory principale del progetto (dove si trova il file `docker-compose.yml`) ed eseguire:

   ```bash
   docker-compose build app
   ```

   Questo comando provvederà a costruire l’immagine Docker per il servizio dell'applicazione.

2. **Avviare i Container Docker:**
   Una volta completata la build, avviare i container in modalità detach con il seguente comando:

   ```bash
   docker-compose up -d
   ```

   Verranno avviati in background tutti i servizi definiti nel file `docker-compose.yml`.

   Dopo l’avvio dei container, l’applicazione inizierà il processo di configurazione. L’inizializzazione di Neo4J può richiedere un tempo significativo.

## Monitoraggio della Configurazione

Per monitorare l’avanzamento della configurazione, in particolare quella di MongoDB, è possibile consultare periodicamente i log del container dell'applicazione con il comando:

```bash
docker logs maadbproject-app-1
```

---

## (Facoltativo) Ripristino dei Backup dei Volumi Docker (Windows & macOS/Linux)

Questa sezione è opzionale e necessaria solo se si desidera ripristinare i volumi dei database da file di backup precedenti.

### 1. Scaricare i File di Backup

Posizionare i seguenti file `.tar.bz2` in una cartella a scelta:

* `mongodb_backup.tar.bz2`
* `neo4j_backup.tar.bz2`
* `postgres_backup.tar.bz2`

---

### 2. Aprire un Terminale in Quella Cartella

* **Windows:** Fare clic con il tasto destro sulla cartella e selezionare **“Apri in PowerShell”**
* **macOS/Linux:** Aprire il terminale ed eseguire `cd` nella cartella

---

### 3. Creare i Volumi Docker (se non già presenti)

```bash
docker volume create maadbproject_mongodb_data
docker volume create maadbproject_neo4j_data
docker volume create maadbproject_postgres_data
```

---

### 4. Eseguire i Comandi di Ripristino

> Utilizzare `${PWD}` in **PowerShell** e `$(pwd)` nel **Terminale macOS/Linux**

#### PowerShell su Windows

```powershell
docker run --rm -v maadbproject_mongodb_data:/volume -v ${PWD}:/backup loomchild/volume-backup restore mongodb_backup.tar.bz2
docker run --rm -v maadbproject_neo4j_data:/volume -v ${PWD}:/backup loomchild/volume-backup restore neo4j_backup.tar.bz2
docker run --rm -v maadbproject_postgres_data:/volume -v ${PWD}:/backup loomchild/volume-backup restore postgres_backup.tar.bz2
```

#### Terminale su macOS/Linux

```bash
docker run --rm -v maadbproject_mongodb_data:/volume -v $(pwd):/backup loomchild/volume-backup restore mongodb_backup.tar.bz2
docker run --rm -v maadbproject_neo4j_data:/volume -v $(pwd):/backup loomchild/volume-backup restore neo4j_backup.tar.bz2
docker run --rm -v maadbproject_postgres_data:/volume -v $(pwd):/backup loomchild/volume-backup restore postgres_backup.tar.bz2
```

---

In caso di errore riguardante file mancanti, verificare che i file `.tar.bz2` si trovino nella cartella corrente e che i nomi siano corretti.

---

## Conversione del Campo Email in Array

Nella collezione `Person` di MongoDB, il campo `email` può contenere una stringa unica con più indirizzi email separati da `;`. Per convertire questo campo in un array di stringhe, eseguire lo script `email_to_array.py` con il seguente comando:

```bash
docker exec maadbproject-app-1 python /app/misch/email_to_array.py
```

---

## Creazione Manuale degli Indici dopo l’Inizializzazione

Dopo che tutti i container sono stati avviati e i dati inizializzati correttamente, è **fortemente consigliato** creare manualmente alcuni indici nei vari motori di database, al fine di migliorare le prestazioni delle query, in particolare su dataset di grandi dimensioni.

### PostgreSQL

Accedere al client PostgreSQL o connettersi tramite container ed eseguire i seguenti comandi SQL:

```sql
CREATE INDEX idx_organization_name ON organization(name);
CREATE INDEX idx_tag_class_id ON Tag("TypeTagClassId"); -- per Matteo
CREATE INDEX idx_place_id ON place(id); -- aggiunto da Matteo
CREATE INDEX idx_tagclass_name ON tagclass(name); -- aggiunto da Matteo
```

### MongoDB

Accedere da Mongo Compass alla Mongo shell (`mongosh`):

Eseguire quindi:

```javascript
db.person.createIndex({ email: 1 }, { name: "email_index" });
db.post.createIndex({ CreatorPersonId: 1 }, { name: "post_creator_index" });
db.person.createIndex({ LocationCityId: 1 }, { name: "location_city_index" });
db.Comment.createIndex({ CreatorPersonId: 1, ParentPostId: 1 });
```

### Neo4j

Tramite Neo4j browser o `cypher-shell`, eseguire il seguente comando Cypher:

```cypher
CREATE INDEX works_from_date_index FOR ()-[r:WORK_AT]-() ON (r.workFrom);
```

> Questi indici non vengono creati automaticamente per garantire il pieno controllo sullo schema. La loro creazione consente **tempi di risposta più rapidi** per le query più frequenti e rilevanti all'interno del progetto.
