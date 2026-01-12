# Intégration Frontend - Guide des Nouvelles Fonctionnalités

## 1. Gestion des Utilisateurs
### Inscription Client
*   **Endpoint**: `POST /users/register`
*   **Payload**:
    ```json
    {
      "nom": "Jean",
      "email": "jean@example.com",
      "mot_de_passe": "secret",
      "age": 25,
      "phone": "+33600000000"
    }
    ```
*   **Note**: Le rôle sera automatiquement "client".

### Création d'Agent (Admin seulement)
*   **Endpoint**: `POST /users/` (Protected: Admin)
*   **Payload**:
    ```json
    {
      "nom": "Agent 007",
      "email": "agent@hosto.com",
      "mot_de_passe": "secret",
      "role": "agent"
    }
    ```

## 2. Tickets et Files d'Attente
### Rejoindre une File (Client)
*   **Endpoint**: `POST /tickets/`
*   **Payload**:
    ```json
    {
      "queue_id": 1,
      "severity": "high",  // low, medium, high
      "urgency": "medium", // low, medium, high
      "prioritaire": false // Reserved for manual override if needed
    }
    ```
*   **Réponse**: Contient `priority_score`, `ticket_id`, `numero`.

### Tableau de Bord Client
*   Utiliser `GET /tickets/history` pour voir les tickets de l'utilisateur.
*   Afficher la position (déduite ou ajoutée plus tard, pour l'instant afficher `numero` et `statut`).

### Tableau de Bord Admin/Agent
*   **Voir la liste d'attente pour une file** :
    *   `GET /tickets/queue/{queue_id}?status=attente`
    *   Affiche la liste triée par Priorité (Gravité/Urgence/Age) puis par heure d'arrivée.
*   **Appeler le suivant** :
    *   `POST /tickets/{queue_id}/next`
    *   Retourne le ticket appelé et le passe en statut "appele".
*   **Gérer un ticket (Actions)** :
    *   **Traiter (Terminer)** : `PUT /tickets/{ticket_id}/status` avec body `{"status": "traite"}`.
    *   **Absent** : `PUT /tickets/{ticket_id}/status` avec body `{"status": "absent"}`.
    *   **Sauter** : `PUT /tickets/{ticket_id}/status` avec body `{"status": "saute"}`.
*   **Statistiques** :
    *   `GET /queues/{queue_id}/stats`
    *   Retourne :
        ```json
        {
          "average_wait_time_minutes": 15.5,
          "waiting_candidates": 12
        }
        ```
