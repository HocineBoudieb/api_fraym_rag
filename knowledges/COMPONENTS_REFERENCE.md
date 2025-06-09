# Référence des Composants Disponibles

## Vue d'ensemble

Ce document liste tous les composants disponibles dans le système de rendu, organisés par catégorie, avec leurs propriétés et exemples d'utilisation.

## Composants de Base

### Button
Bouton interactif avec différents styles et tailles.

**Props :**
- `children` (string) - Texte du bouton
- `className` (string) - Classes CSS additionnelles
- `color` (string) - Couleur : `'blue'`, `'green'`, `'red'`, `'gray'`, `'black'`, `'white'`
- `size` (string) - Taille : `'sm'`, `'md'`, `'lg'`, `'xl'`
- `variant` (string) - Variante : `'solid'`, `'outline'`, `'ghost'`
- `onClick` (function) - Fonction appelée au clic
- `disabled` (boolean) - Désactive le bouton

**Exemple :**
```json
{
  "type": "Button",
  "props": {
    "children": "Cliquez ici",
    "color": "blue",
    "size": "lg",
    "className": "mt-4"
  }
}
```

### Card
Conteneur avec ombre et bordures arrondies.

**Props :**
- `children` (ReactNode) - Contenu de la carte
- `className` (string) - Classes CSS additionnelles
- `padding` (string) - Espacement interne
- `shadow` (string) - Intensité de l'ombre

**Exemple :**
```json
{
  "type": "Card",
  "props": {
    "className": "hover:shadow-lg transition-shadow",
    "children": {
      "type": "Text",
      "props": {
        "children": "Contenu de la carte"
      }
    }
  }
}
```

### Text
Texte avec différentes tailles et couleurs.

**Props :**
- `children` (string) - Contenu textuel
- `className` (string) - Classes CSS additionnelles
- `size` (string) - Taille : `'xs'`, `'sm'`, `'md'`, `'lg'`, `'xl'`, `'2xl'`, `'3xl'`
- `color` (string) - Couleur du texte (classes Tailwind)
- `weight` (string) - Poids de la police : `'normal'`, `'medium'`, `'semibold'`, `'bold'`

**Exemple :**
```json
{
  "type": "Text",
  "props": {
    "children": "Ceci est un texte",
    "size": "lg",
    "color": "gray-600",
    "className": "text-center"
  }
}
```

### Heading
Titres hiérarchiques (h1 à h6).

**Props :**
- `children` (string) - Texte du titre
- `level` (number) - Niveau du titre (1-6)
- `className` (string) - Classes CSS additionnelles
- `color` (string) - Couleur du texte
- `align` (string) - Alignement : `'left'`, `'center'`, `'right'`

**Exemple :**
```json
{
  "type": "Heading",
  "props": {
    "level": 1,
    "children": "Titre Principal",
    "className": "text-center mb-8",
    "color": "blue-600"
  }
}
```

### Image
Affichage d'images avec gestion responsive.

**Props :**
- `src` (string) - URL de l'image
- `alt` (string) - Texte alternatif
- `className` (string) - Classes CSS additionnelles
- `width` (number) - Largeur
- `height` (number) - Hauteur
- `objectFit` (string) - Ajustement : `'cover'`, `'contain'`, `'fill'`

**Exemple :**
```json
{
  "type": "Image",
  "props": {
    "src": "/images/hero.jpg",
    "alt": "Image héro",
    "className": "w-full h-64 object-cover rounded-lg"
  }
}
```

### Input
Champ de saisie avec différents types.

**Props :**
- `placeholder` (string) - Texte d'aide
- `className` (string) - Classes CSS additionnelles
- `type` (string) - Type : `'text'`, `'email'`, `'password'`, `'number'`
- `value` (string) - Valeur
- `onChange` (function) - Fonction de changement
- `disabled` (boolean) - Désactive le champ

**Exemple :**
```json
{
  "type": "Input",
  "props": {
    "placeholder": "Entrez votre email",
    "type": "email",
    "className": "mb-4"
  }
}
```

## Composants de Layout

### Container
Conteneur avec largeur maximale et centrage.

**Props :**
- `children` (ReactNode) - Contenu
- `className` (string) - Classes CSS additionnelles
- `maxWidth` (string) - Largeur max : `'sm'`, `'md'`, `'lg'`, `'xl'`, `'2xl'`, `'4xl'`, `'6xl'`, `'full'`
- `padding` (string) - Espacement interne

**Exemple :**
```json
{
  "type": "Container",
  "props": {
    "maxWidth": "lg",
    "className": "py-8",
    "children": [...]
  }
}
```

### Grid
Grille responsive avec colonnes configurables.

**Props :**
- `children` (array) - Éléments de la grille
- `cols` (number) - Nombre de colonnes : 1, 2, 3, 4, 6, 12
- `gap` (number) - Espacement entre éléments
- `className` (string) - Classes CSS additionnelles
- `responsive` (object) - Configuration responsive

**Exemple :**
```json
{
  "type": "Grid",
  "props": {
    "cols": 3,
    "gap": 6,
    "className": "mb-8",
    "children": [
      {"type": "Card", "props": {"children": "Item 1"}},
      {"type": "Card", "props": {"children": "Item 2"}},
      {"type": "Card", "props": {"children": "Item 3"}}
    ]
  }
}
```

### Flex
Conteneur flexbox avec contrôle de direction et alignement.

**Props :**
- `children` (ReactNode) - Contenu
- `direction` (string) - Direction : `'row'`, `'col'`, `'row-reverse'`, `'col-reverse'`
- `justify` (string) - Justification : `'start'`, `'center'`, `'end'`, `'between'`, `'around'`, `'evenly'`
- `align` (string) - Alignement : `'start'`, `'center'`, `'end'`, `'stretch'`, `'baseline'`
- `gap` (number) - Espacement entre éléments
- `className` (string) - Classes CSS additionnelles

**Exemple :**
```json
{
  "type": "Flex",
  "props": {
    "direction": "row",
    "justify": "center",
    "align": "center",
    "gap": 4,
    "children": [...]
  }
}
```

## Composants Spécialisés

### ProductCard
Carte produit pour e-commerce.

**Props :**
- `title` (string) - Nom du produit
- `price` (string) - Prix
- `image` (string) - URL de l'image
- `description` (string) - Description
- `buttonText` (string) - Texte du bouton (défaut: "Voir plus")
- `className` (string) - Classes CSS additionnelles
- `onButtonClick` (function) - Action du bouton

**Exemple :**
```json
{
  "type": "ProductCard",
  "props": {
    "title": "Smartphone Pro",
    "price": "899,99 €",
    "image": "/images/phone.jpg",
    "description": "Le dernier smartphone avec toutes les fonctionnalités",
    "buttonText": "Acheter maintenant"
  }
}
```

### Hero
Section héro pour pages d'atterrissage.

**Props :**
- `title` (string) - Titre principal
- `subtitle` (string) - Sous-titre
- `buttonText` (string) - Texte du bouton CTA
- `backgroundImage` (string) - Image de fond
- `className` (string) - Classes CSS additionnelles
- `onButtonClick` (function) - Action du bouton

**Exemple :**
```json
{
  "type": "Hero",
  "props": {
    "title": "Révolutionnez votre Business",
    "subtitle": "Notre plateforme IA vous aide à automatiser vos processus",
    "buttonText": "Commencer gratuitement",
    "className": "bg-gradient-to-r from-blue-600 to-purple-600 text-white"
  }
}
```

### Navigation
Barre de navigation avec liens.

**Props :**
- `items` (array) - Liste des éléments de navigation
- `className` (string) - Classes CSS additionnelles
- `orientation` (string) - Orientation : `'horizontal'`, `'vertical'`
- `activeItem` (string) - Élément actif

**Exemple :**
```json
{
  "type": "Navigation",
  "props": {
    "items": ["Accueil", "Services", "À propos", "Contact"],
    "className": "mb-8",
    "section": "navbar"
  }
}
```

## Composants Zara

### ZaraHeader
En-tête spécifique à l'interface Zara.

**Props :**
- `className` (string) - Classes CSS additionnelles

**Exemple :**
```json
{
  "type": "ZaraHeader",
  "props": {
    "className": "mb-8"
  }
}
```

### ZaraWelcome
Message de bienvenue Zara.

**Props :**
- `className` (string) - Classes CSS additionnelles

**Exemple :**
```json
{
  "type": "ZaraWelcome",
  "props": {
    "className": "mb-6"
  }
}
```

### ZaraCategoryButtons
Boutons de catégories Zara.

**Props :**
- `className` (string) - Classes CSS additionnelles
- `onCategoryClick` (function) - Action de clic sur catégorie

**Exemple :**
```json
{
  "type": "ZaraCategoryButtons",
  "props": {
    "className": "mb-8"
  }
}
```

### ZaraProductGrid
Grille de produits Zara avec données intégrées.

**Props :**
- `className` (string) - Classes CSS additionnelles

**Exemple :**
```json
{
  "type": "ZaraProductGrid",
  "props": {
    "className": "mb-8"
  }
}
```

### ZaraProductCard
Carte produit spécifique Zara.

**Props :**
- `product` (object) - Objet produit avec `id`, `name`, `price`, `image`, `alt`
- `className` (string) - Classes CSS additionnelles

**Exemple :**
```json
{
  "type": "ZaraProductCard",
  "props": {
    "product": {
      "id": 1,
      "name": "Trench à double épaisseur",
      "price": "119,00 €",
      "image": "/images/trench.jpg",
      "alt": "Trench coat beige"
    }
  }
}
```

### ZaraMessageInput
Zone de saisie de message Zara avec bouton d'envoi et microphone.

**Props :**
- `className` (string) - Classes CSS additionnelles
- `onSend` (function) - Action d'envoi
- `onVoiceInput` (function) - Action microphone

**Exemple :**
```json
{
  "type": "ZaraMessageInput",
  "props": {
    "className": "mt-8"
  }
}
```

### ZaraContainer
Conteneur complet Zara avec tous les composants intégrés.

**Props :**
- `className` (string) - Classes CSS additionnelles

**Exemple :**
```json
{
  "type": "ZaraContainer",
  "props": {
    "className": "min-h-screen"
  }
}
```

## Composants de Structure

### Header
En-tête de page générique.

**Props :**
- `children` (ReactNode) - Contenu de l'en-tête
- `className` (string) - Classes CSS additionnelles

### Footer
Pied de page générique.

**Props :**
- `children` (ReactNode) - Contenu du pied de page
- `className` (string) - Classes CSS additionnelles

### Sidebar
Barre latérale pour layouts dashboard.

**Props :**
- `children` (ReactNode) - Contenu de la sidebar
- `className` (string) - Classes CSS additionnelles

### Welcome
Section de bienvenue générique.

**Props :**
- `title` (string) - Titre de bienvenue
- `subtitle` (string) - Sous-titre
- `className` (string) - Classes CSS additionnelles

## Propriétés Communes

Tous les composants supportent ces propriétés communes :

- `className` (string) - Classes CSS Tailwind additionnelles
- `id` (string) - Identifiant unique
- `style` (object) - Styles CSS inline
- `children` (ReactNode) - Contenu enfant (selon le composant)

## Classes Tailwind Utiles

### Espacement
- `m-{size}` / `p-{size}` - Margin/Padding (0, 1, 2, 3, 4, 6, 8, 12, 16, 20, 24)
- `mb-{size}`, `mt-{size}`, `ml-{size}`, `mr-{size}` - Margins directionnelles
- `gap-{size}` - Espacement dans Grid/Flex

### Couleurs
- `text-{color}-{shade}` - Couleur du texte
- `bg-{color}-{shade}` - Couleur de fond
- `border-{color}-{shade}` - Couleur de bordure

### Tailles
- `w-{size}`, `h-{size}` - Largeur/Hauteur
- `max-w-{size}` - Largeur maximale
- `text-{size}` - Taille du texte

### Responsive
- `sm:`, `md:`, `lg:`, `xl:`, `2xl:` - Préfixes responsive

Exemple : `"className": "w-full md:w-1/2 lg:w-1/3 p-4 mb-6 text-center"`