#!/bin/bash
# Script de sauvegarde pour le Bot de Trading XRP v3.0

# Définition des variables
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups"
BACKUP_FILE="${BACKUP_DIR}/xrp_bot_backup_${TIMESTAMP}.tar.gz"
DIRS_TO_BACKUP="config data logs"

# Création du répertoire de sauvegarde s'il n'existe pas
mkdir -p ${BACKUP_DIR}

# Message de début
echo "Démarrage de la sauvegarde du Bot de Trading XRP v3.0..."
echo "Date et heure: $(date)"

# Vérification de l'existence des répertoires à sauvegarder
for dir in ${DIRS_TO_BACKUP}; do
  if [ ! -d "$dir" ]; then
    echo "Avertissement: Le répertoire $dir n'existe pas, création..."
    mkdir -p $dir
  fi
done

# Création de l'archive
echo "Création de l'archive de sauvegarde..."
tar -czf ${BACKUP_FILE} ${DIRS_TO_BACKUP}

# Vérification du succès de la sauvegarde
if [ $? -eq 0 ]; then
  echo "Sauvegarde réussie: ${BACKUP_FILE}"
  echo "Taille de la sauvegarde: $(du -h ${BACKUP_FILE} | cut -f1)"
  
  # Suppression des anciennes sauvegardes (garder les 10 plus récentes)
  echo "Nettoyage des anciennes sauvegardes..."
  ls -t ${BACKUP_DIR}/xrp_bot_backup_*.tar.gz | tail -n +11 | xargs -r rm
  echo "Nombre de sauvegardes conservées: $(ls ${BACKUP_DIR}/xrp_bot_backup_*.tar.gz | wc -l)"
else
  echo "Erreur lors de la création de la sauvegarde!"
  exit 1
fi

echo "Processus de sauvegarde terminé."
