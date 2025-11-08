# Widget ElevenLabs - Informations

## Comportement Normal

Le widget ElevenLabs démarre en mode "bubble" (petit bouton en bas à droite) et nécessite :

1. **Un clic de l'utilisateur** pour s'ouvrir (pour des raisons de sécurité navigateur)
2. **Permissions microphone** accordées par l'utilisateur

## Ouverture Automatique

Le code tente d'ouvrir le widget automatiquement au chargement, mais :

- Le navigateur peut bloquer l'ouverture automatique
- L'utilisateur DOIT autoriser le microphone lors de la première utilisation
- Si l'erreur `Uncaught (in promise) undefined` apparaît, c'est normal - il faut cliquer manuellement

## Solution Simple

**Pour tester immédiatement** : Cliquez simplement sur le bouton "Need help?" en bas à droite.

Une fois que vous avez cliqué et autorisé le microphone, le widget s'ouvrira automatiquement aux prochains chargements.

## Mode Plein Écran vs Minimisé

- **Par défaut (isMinimized = false)** : Le wrapper est en plein écran
- **Après transition (isMinimized = true)** : Le widget se minimise en bas à droite et la carte apparaît

Pour tester la transition : **Ctrl+T** (déclenche manuellement la minimisation)

## Debugging

Si le widget ne s'affiche pas correctement, vérifiez dans la console :
```
✅ Widget ElevenLabs found
🖱️ Opening widget via API
```

Si vous voyez ces messages, tout fonctionne normalement.
