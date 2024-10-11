# Projet de charding/cluster Big Data

Dans ce projet nous allons configurer :

- **3 shards**, chacun étant un replica set avec un PRIMARY et **2 SECONDARIES**.
- Un **mongos** (routeur) pour gérer le cluster sharded.
- Un ensemble de **config servers** en replica set pour stocker les métadonnées du cluster.

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/faccdd11-c580-45a8-954a-19fe894e2f59/779bd245-d104-420a-b2dd-e561e33c1abd/image.png)

### **Prérequis :**

- **Docker Desktop**
- **MongoDB Compass**
- Récupérer le fichier [liste_des_prenoms.json sur oendata](https://opendata.paris.fr/explore/dataset/liste_des_prenoms/table/?disjunctive.annee&disjunctive.prenoms&sort=annee)

---

## **Étapes de configuration :**

### **1. Créer un réseau Docker dédié**

Pour permettre la communication entre les conteneurs, on créer un réseau Docker :

```bash
docker network create mongo-cluster
```

### **2. Configurer les Config Servers**

Les config servers stockent les métadonnées du cluster sharded.

- **Lancer les instances des config servers :**

```bash
# Config Server 1
docker run -d --name config1 --net mongo-cluster mongo:latest mongod --configsvr --replSet cfgrs --port 27017

# Config Server 2
docker run -d --name config2 --net mongo-cluster mongo:latest mongod --configsvr --replSet cfgrs --port 27017

# Config Server 3
docker run -d --name config3 --net mongo-cluster mongo:latest mongod --configsvr --replSet cfgrs --port 27017
```

- **Initialiser le replica set des config servers :**

Se connecter à l'un des config servers :

```bash
docker exec -it config1 mongosh --port 27017
```

Dans le shell MongoDB, on exécute:

```jsx
javascript
Copier le code
rs.initiate({
  _id: "cfgrs",
  configsvr: true,
  members: [
    { _id: 0, host: "config1:27017" },
    { _id: 1, host: "config2:27017" },
    { _id: 2, host: "config3:27017" }
  ]
})
```

### **3. Configurer les Shards**

Pour chaque shard, nous allons créer un replica set avec un PRIMARY et deux SECONDARIES.

### **Shard 1 :**

- **Lancer les instances :**

```bash
# PRIMARY
docker run -d --name shard1-primary --net mongo-cluster mongo:latest mongod --shardsvr --replSet shard1rs --port 27018

# SECONDARY 1
docker run -d --name shard1-secondary1 --net mongo-cluster mongo:latest mongod --shardsvr --replSet shard1rs --port 27018

# SECONDARY 2
docker run -d --name shard1-secondary2 --net mongo-cluster mongo:latest mongod --shardsvr --replSet shard1rs --port 27018
```

- **Initialiser le replica set :**

```bash
docker exec -it shard1-primary mongosh --port 27018
```

Dans le shell MongoDB :

```jsx
javascript
Copier le code
rs.initiate({
  _id: "shard1rs",
  members: [
    { _id: 0, host: "shard1-primary:27018" },
    { _id: 1, host: "shard1-secondary1:27018" },
    { _id: 2, host: "shard1-secondary2:27018" }
  ]
})
```

### **Shard 2 :**

- **Lancer les instances :**

```bash
# PRIMARY
docker run -d --name shard2-primary --net mongo-cluster mongo:latest mongod --shardsvr --replSet shard2rs --port 27019

# SECONDARY 1
docker run -d --name shard2-secondary1 --net mongo-cluster mongo:latest mongod --shardsvr --replSet shard2rs --port 27019

# SECONDARY 2
docker run -d --name shard2-secondary2 --net mongo-cluster mongo:latest mongod --shardsvr --replSet shard2rs --port 27019
```

- **Initialiser le replica set :**

```bash
docker exec -it shard2-primary mongosh --port 27019
```

Dans le shell MongoDB :

```jsx
javascript
Copier le code
rs.initiate({
  _id: "shard2rs",
  members: [
    { _id: 0, host: "shard2-primary:27019" },
    { _id: 1, host: "shard2-secondary1:27019" },
    { _id: 2, host: "shard2-secondary2:27019" }
  ]
})
```

### **Shard 3 :**

- **Lancer les instances :**

```bash
# PRIMARY
docker run -d --name shard3-primary --net mongo-cluster mongo:latest mongod --shardsvr --replSet shard3rs --port 27020

# SECONDARY 1
docker run -d --name shard3-secondary1 --net mongo-cluster mongo:latest mongod --shardsvr --replSet shard3rs --port 27020

# SECONDARY 2
docker run -d --name shard3-secondary2 --net mongo-cluster mongo:latest mongod --shardsvr --replSet shard3rs --port 27027
```

- **Initialiser le replica set :**

```bash
docker exec -it shard3-primary mongo --port 27020
```

Dans le shell MongoDB :

```jsx
javascript
Copier le code
rs.initiate({
  _id: "shard3rs",
  members: [
    { _id: 0, host: "shard3-primary:27020" },
    { _id: 1, host: "shard3-secondary1:27020" },
    { _id: 2, host: "shard3-secondary2:27020" }
  ]
})
```

### **4. Démarrer le mongos (routeur)**

Le mongos sert de point d'entrée pour les clients et distribue les opérations aux shards appropriés.

```bash
docker run -d --name mongos --net mongo-cluster mongo:latest mongos --configdb cfgrs/config1:27017,config2:27017,config3:27017 --bind_ip_all
```

### **5. Ajouter les shards au cluster**

Connectez au mongos :

```bash
docker exec -it mongos mongosh
```

Dans le shell MongoDB, ajoutez les shards :

```jsx
sh.addShard("shard1rs/shard1-primary:27018,shard1-secondary1:27018,shard1-secondary2:27018")
sh.addShard("shard2rs/shard2-primary:27019,shard2-secondary1:27019,shard2-secondary2:27019")
sh.addShard("shard3rs/shard3-primary:27020,shard3-secondary1:27020,shard3-secondary2:27020")
```

### **6. Vérifier la configuration du cluster**

Toujours dans le shell MongoDB du mongos, on exécute :

```jsx
sh.status()
```

Cela affichera l'état du cluster sharded, confirmant que tous les shards et config servers sont correctement configurés.

## Analyser notre terminal

```powershell
[direct: mongos] test> sh.status()
shardingVersion
{ _id: 1, clusterId: ObjectId('6708dd3624e1dedaa3d7928f') }
---
shards
[
  {
    _id: 'shard1rs',
    host: 'shard1rs/shard1-primary:27018,shard1-secondary1:27018,shard1-secondary2:27018',
    state: 1,
    topologyTime: Timestamp({ t: 1728634302, i: 10 }),
    replSetConfigVersion: Long('-1')
  },
  {
    _id: 'shard2rs',
    host: 'shard2rs/shard2-primary:27019,shard2-secondary1:27019,shard2-secondary2:27019',
    state: 1,
    topologyTime: Timestamp({ t: 1728634303, i: 3 }),
    replSetConfigVersion: Long('-1')
  },
  {
    _id: 'shard3rs',
    host: 'shard3rs/shard3-primary:27020,shard3-secondary1:27020,shard3-secondary2:27020',
    state: 1,
    topologyTime: Timestamp({ t: 1728634303, i: 26 }),
    replSetConfigVersion: Long('-1')
  }
]
---
active mongoses
[ { '8.0.1': 1 } ]
---
autosplit
{ 'Currently enabled': 'yes' }
---
balancer
{
  'Currently enabled': 'yes',
  'Currently running': 'no',
  'Failed balancer rounds in last 5 attempts': 0,
  'Migration Results for the last 24 hours': 'No recent migrations'
}
---
databases
[
  {
    database: { _id: 'config', primary: 'config', partitioned: true },
    collections: {}
  }
]
```

### **1.** Accéder au cluster depuis ma machine local : **Utiliser MongoDB Compass pour surveiller le cluster**

**MongoDB Compass** est un outil graphique qui permet de visualiser, analyser et optimiser vos bases de données MongoDB.

### **a. Se connecter au cluster via MongoDB Compass**

```powershell
mongodb://localhost:27017
```

### **b. Explorer le cluster**

Une fois connecté, on peut :

- **Visualiser les bases de données et collections**.
- **Exécuter des requêtes** pour interagir avec les données.
- **Analyser les performances** via l'onglet **"Performance"**.
- **Gérer les index** et optimiser les requêtes.

**Note** : Comme on se connecte au **mongos**, toutes les opérations sont automatiquement réparties sur les shards appropriés.

### **2. Étapes pour se connecter au cluster avec MongoDB Compass :**

### **a. Exposer le port du mongos vers l'hôte**

Actuellement, notre routeur **mongos** est exécuté dans un conteneur Docker sans port exposé vers notre machine hôte. Pour permettre à MongoDB Compass de se connecter au cluster, on doit mapper le port du **mongos** du conteneur Docker vers notre machine hôte.

**Arrêter et supprimer le conteneur mongos existant :**

```bash
docker stop mongos
docker rm mongos
```

**Relancer le mongos en mappant le port 27017 :**

```bash
docker run -d --name mongos --net mongo-cluster -p 27017:27017 mongo:latest mongos --configdb cfgrs/config1:27017,config2:27017,config3:27017 --bind_ip_all
```

Cette commande mappe le port 27017 du conteneur vers le port 27017 de votre machine hôte.

IMPORTANT : Mapper le mongos sur un autre port

- On préfère ne pas arrêter notre service MongoDB local, donc on peut mapper le **mongos** sur un autre port, par exemple **37017**.
- **Relancer le conteneur mongos** :
    
    ```bash
    docker stop mongos
    docker rm mongos
    docker run -d --name mongos --net mongo-cluster -p 37017:27017 mongo:latest mongos --configdb cfgrs/config1:27017,config2:27017,config3:27017 --bind_ip_all
    ```
    
- **Connexion avec Navicat ou MongoDB Compass** :
    - Utilisez mongodb://localhost:**`37017`** comme hôte pour nous connecter au **mongos**.

### **3. Créer une base de données et une collection**

### **a. Utiliser le shell MongoDB pour créer une base de données et une collection**

1. **Se connecter au mongos via le shell MongoDB** :
    - Si on a mappé le **mongos** sur le port **37017** :
        
        ```bash
        mongo --host localhost --port 37017
        ```
        
    - Si on a arrêté le service MongoDB local et mappé sur le port **27017** :
        
        ```bash
        mongo --host localhost --port 27017
        ```
        
2. **Créer une base de données et une collection** :
    
    Dans le shell MongoDB, on exécute :
    
    ```jsx
    use maBase
    db.maCollection.insertOne({ test: "valeur" })
    ```
    
    - **Explication** :
        - `use maBase` : Sélectionne ou crée la base de données `maBase`.
        - `db.maCollection.insertOne({ test: "valeur" })` : Crée la collection `maCollection` et insère un document.
3. **Vérifier que la collection est créée** :
    
    ```jsx
    show collections
    ```
    

### **b. Vérifier dans Navicat et MongoDB Compass**

- **On actualise la connexion** : Dans Navicat et MongoDB Compass, on actualise la liste des bases de données. On peut maintenant voir `maBase` avec la collection `maCollection`.

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/faccdd11-c580-45a8-954a-19fe894e2f59/14c796c8-a7f7-4065-9518-0b0eefd97bbd/image.png)

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/faccdd11-c580-45a8-954a-19fe894e2f59/f529577a-180e-4833-9820-f3da9bb69daf/image.png)

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/faccdd11-c580-45a8-954a-19fe894e2f59/249308ac-76b5-4f1d-8f30-291dab6d436f/image.png)

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/faccdd11-c580-45a8-954a-19fe894e2f59/06ab5d33-ace5-40c4-bb74-67a98dcd03af/image.png)

### **4. Configurer le sharding sur le champ `annee`**

### **a. Activer le sharding sur la base de données**

Dans le shell MongoDB connecté au **mongos** :

```jsx
sh.enableSharding("maBase")
```

### **b. Créer un index sur le champ `annee`**

```jsx
use maBase
db.liste_des_prenoms.createIndex({ annee: 1 })
```

### **c. Activer le sharding sur la collection**

```jsx
sh.shardCollection("maBase.liste_des_prenoms", { annee: 1 })
```

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/faccdd11-c580-45a8-954a-19fe894e2f59/645c8515-04b6-458a-8501-fe7265db6522/image.png)

### **5. Pré-splitter les données en plages spécifiques**

### **a. Désactiver temporairement le balancer**

```jsx
sh.stopBalancer()
```

### **b. Créer des points de split**

- **Point de split à 2014** :
    
    ```jsx
    sh.splitAt("maBase.liste_des_prenoms", { annee: 2014 })
    ```
    

### **c. Déplacer les chunks vers les shards appropriés**

- **Données de 2004 à 2013 vers `shard1rs`** :
    
    ```jsx
    sh.moveChunk("maBase.liste_des_prenoms", { annee: 2005 }, "shard1rs")
    ```
    
- **Données de 2014 à 2023 vers `shard2rs`** :
    
    ```jsx
    sh.moveChunk("maBase.liste_des_prenoms", { annee: 2015 }, "shard2rs")
    ```
    

**Remarque** : Si on a un troisième shard (`shard3rs`) et qu’on souhaite répartir les données différemment, on ajuste les points de split et les déplacements de chunks en conséquence.

### **d. Réactiver le balancer**

```jsx
sh.startBalancer()
```

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/faccdd11-c580-45a8-954a-19fe894e2f59/9555534b-1806-4967-903c-b665f85bfe84/image.png)

### **6. Vérifier la répartition des données**

### **a. Utiliser `sh.status()`**

Dans le shell MongoDB :

```jsx
sh.status()
```

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/faccdd11-c580-45a8-954a-19fe894e2f59/92e524bf-ea26-4e84-a548-5d19f53629da/image.png)

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/faccdd11-c580-45a8-954a-19fe894e2f59/1d0a3b36-f46f-4735-b272-687ed3479d0a/image.png)

**Analyse de la sortie :**

```vbnet
vbnet
Copier le code
sharding version: ...
shards:
   {  "_id" : "shard1rs",  "host" : "shard1rs/shard1-primary:27018,...",  ... }
   {  "_id" : "shard2rs",  "host" : "shard2rs/shard2-primary:27019,...",  ... }
databases:
   {  "_id" : "maBase",  "partitioned" : true,  "primary" : "shard1rs" }
      maBase.maCollection
         shard key: { "annee" : 1 }
         chunks:
            shard1rs  1
            shard2rs  1
         { "annee" : { "$minKey" : 1 } } -->> { "annee" : 2014 } on : shard1rs
         { "annee" : 2014 } -->> { "annee" : { "$maxKey" : 1 } } on : shard2rs

```

- **Interprétation :**
    - Les **chunks** sont les morceaux de données que MongoDB utilise pour répartir les données entre les shards.
    - Chaque **chunk** est défini par une plage de valeurs de la clé de sharding (`annee` dans notre cas).
    - Les lignes `{ "annee" : { "$minKey" : 1 } } -->> { "annee" : 2014 } on : shard1rs` indiquent que les documents avec `annee` de la valeur minimale jusqu'à 2014 sont sur `shard1rs`.
    - De même pour `shard2rs` avec `annee` de 2014 à la valeur maximale.

### **7. Utiliser `db.liste_des_prenoms.getShardDistribution()`**

Cette méthode vous permet de voir la distribution des documents d'une collection entre les shards.

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/faccdd11-c580-45a8-954a-19fe894e2f59/0cbb26b2-d585-4101-b842-a7856fba3c18/image.png)

# Simulation panne shard avec script Python

```python
import docker
import time
from pymongo import MongoClient

# Initialiser le client Docker
docker_client = docker.from_env()

# Fonction pour arrêter un shard
def stop_shard(shard_name_prefix):
    containers = docker_client.containers.list()
    shard_containers = [container for container in containers if shard_name_prefix in container.name]
    for container in shard_containers:
        print(f"Arrêt du conteneur : {container.name}")
        container.stop()
    print(f"Shard '{shard_name_prefix}' arrêté.")

# Fonction pour démarrer un shard
def start_shard(shard_name_prefix):
    containers = docker_client.containers.list(all=True)
    shard_containers = [container for container in containers if shard_name_prefix in container.name]
    for container in shard_containers:
        print(f"Démarrage du conteneur : {container.name}")
        container.start()
    print(f"Shard '{shard_name_prefix}' démarré.")

# Fonction pour effectuer des requêtes
def test_queries():
    # Se connecter au mongos
    client = MongoClient('localhost', 27017)
    db = client['maBase']
    collection = db['maCollection']
    try:
        # Requête sur l'année 2006
        print("Requête sur annee=2006")
        result = collection.find_one({'annee': 2006})
        print(result)
    except Exception as e:
        print(f"Erreur lors de la requête sur annee=2006 : {e}")

    try:
        # Requête sur l'année 2016
        print("Requête sur annee=2016")
        result = collection.find_one({'annee': 2016})
        print(result)
    except Exception as e:
        print(f"Erreur lors de la requête sur annee=2016 : {e}")

if __name__ == "__main__":
    shard_to_stop = 'shard1'  # Par exemple, arrêter 'shard1'

    # Arrêter le shard
    stop_shard(shard_to_stop)

    # Attendre un moment pour que le cluster détecte la panne
    time.sleep(10)

    # Effectuer des requêtes pour observer le comportement
    test_queries()

    # Redémarrer le shard
    start_shard(shard_to_stop)

    # Attendre que le shard soit opérationnel
    time.sleep(30)

    # Effectuer à nouveau les requêtes
    test_queries()

```

### **1. Observer et analyser le comportement du cluster après la panne du shard**

Après avoir arrêté le shard, on peut observer comment le cluster réagit.

### **a. Comportement attendu**

- **Requêtes sur les données du shard indisponible** : Les requêtes qui ciblent des données présentes sur le shard arrêté échoueront avec une erreur.
- **Requêtes sur les données des autres shards** : Les requêtes sur les données des shards encore actifs continueront de fonctionner normalement.
- **Le mongos reste opérationnel** : Le routeur mongos reste actif et continue de router les requêtes vers les shards disponibles.

### **b. Tester les requêtes via le mongos**

Connectez-vous au **mongos** via le shell MongoDB ou MongoDB Compass et effectuez des requêtes.

- **Requête sur une année du shard indisponible** :
    
    ```jsx
    use maBase
    db.maCollection.find({ annee: 2006 }).pretty()
    ```
    
    - **Résultat attendu** : La requête échoue avec une erreur indiquant que le shard est indisponible.
- **Requête sur une année d'un shard disponible** :
    
    ```jsx
    db.maCollection.find({ annee: 2016 }).pretty()
    ```
    
    - **Résultat attendu** : La requête réussit et renvoie les documents correspondants.

### **c. Observer les messages d'erreur**

On peut observer cette erreur :

```vbnet
Error: error: {
  "ok" : 0,
  "errmsg" : "ShardNotFound: No shard found for shard key { annee: 2006 }",
  "code" : 42,
  "codeName" : "ShardNotFound"

```

### **d. Vérifier l'état du cluster avec `sh.status()`**

On exécute `sh.status()` pour voir que le shard est marqué comme **DOWN** :

```jsx

sh.status()

```

### **e. Observation**

```python
--- Sharding Status ---
  sharding version: {
    "_id" : 1,
    "minCompatibleVersion" : 5,
    "currentVersion" : 6,
    "clusterId" : ObjectId("614a6e8e9f9a25e7f6b8b0d4")
  }
  shards:
    {  "_id" : "shard1rs",  "host" : "shard1rs/shard1-primary:27018,shard1-secondary1:27018,shard1-secondary2:27018",  "error" : "Could not connect to shard1rs/shard1-primary:27018" }
    {  "_id" : "shard2rs",  "host" : "shard2rs/shard2-primary:27019,shard2-secondary1:27019,shard2-secondary2:27019",  "state" : "up" }
    {  "_id" : "shard3rs",  "host" : "shard3rs/shard3-primary:27020,shard3-secondary1:27020,shard3-secondary2:27020",  "state" : "up" }
  active mongoses:
    "3.6.8" : 1
  autosplit:
    Currently enabled: yes
  balancer:
    Currently enabled: yes
    Currently running: no
    Failed balancer rounds in last 5 attempts: 0
    Migration Results for the last 24 hours:
        No recent migrations
  databases:
    {  "_id" : "maBase",  "primary" : "shard1rs",  "partitioned" : true }
      maBase.maCollection
        shard key: { "annee" : 1 }
        chunks:
            shard1rs  1
            shard2rs  1
        { "annee" : { "$minKey" : 1 } } -->> { "annee" : 2014 } on : shard1rs
        { "annee" : 2014 } -->> { "annee" : { "$maxKey" : 1 } } on : shard2rs

```

### f. Interprétation **:**

- **shards:**
    - **`shard1rs`** :
        - Affiche un **`error`** indiquant qu'il n'a pas pu se connecter au shard, ce qui signifie qu'il est **down**.
    - **`shard2rs`** et **`shard3rs`** :
        - Ont un état `"up"`, ce qui signifie qu'ils fonctionnent correctement.
- **databases:**
    - La base de données `maBase` est partitionnée (shardée).
    - Les chunks sont répartis entre les shards disponibles.
    - Le chunk qui était sur `shard1rs` est toujours référencé, mais le shard étant indisponible, les données de cette plage ne sont pas accessibles.

### Conclusion, on peut voir qu’un des shard est bien down, ce qui permet à un autre shard de prendre le relai