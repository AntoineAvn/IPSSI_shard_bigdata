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
