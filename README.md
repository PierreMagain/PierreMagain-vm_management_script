# Configuration des Scripts dans le Dossier Bin

Ce dépôt contient des scripts de création/gestion/suppression de VM seulement sur KVM . Suivez ces étapes pour les configurer correctement.
A savoir que ces script font appel des VM 'templates' selon les distribution de votre choix nommées 0-debian,0-ubuntu,0-rocky,... A vous de créer ces 'templates' en amont.
A créer également en amont est le network dans lequel votre infrastructure va être.

## Étapes de Configuration

### 1. Créer le Dossier Bin

Créez un dossier nommé `Bin` où vous allez stocker vos scripts. Utilisez la commande suivante pour le créer :

```sh
mkdir -p /home/pierrem/Documents/Bin
```
###  2. Ajout du dossier Bin dans le bashrc

Ensuite ajoutez tout en bas de votre fichier ~/.basrc les deux lignes suivantes :

```sh
nano ~/.bashrc
```
```sh
export PATH=$PATH:/home/pierrem/Documents/Bin
```
et a ne pas oublier bien sur :

```sh
source ~/.bashrc
```
###  3. Exemple d'utilisation
Une fois tout ceci fait, en incluant les templates et le réseau,
il vous suffit de créer un dossier avec dans lequel vous editez votre kvm-manager.conf (exemple mis dans le repo)
et puis executer le script shell avec la commande suivante :

```sh
kvm-manager.sh clone
```
il vous demanderont une confirmation :  mettre 'yes'
